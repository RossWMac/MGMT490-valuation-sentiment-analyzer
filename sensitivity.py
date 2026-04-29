"""
sensitivity.py
--------------
Generates a 2-D sensitivity table (DataFrame) and an annotated heatmap
for DCF intrinsic value vs. WACC and Terminal Growth Rate / Exit Multiple.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from dcf_engine import run_dcf


def build_sensitivity_table(
    financial_data: dict,
    base_wacc: float,
    base_growth_rate: float,
    terminal_method: str = "gordon",
    base_terminal_growth: float = 0.025,
    base_exit_multiple: float = 12.0,
    years: int = 5,
    margin_of_safety: float = 0.20,
    wacc_steps: int = 7,
    tv_steps: int = 7,
) -> pd.DataFrame:
    """
    Build a sensitivity DataFrame where:
      Rows    = WACC values (from base ± 3%, in ~1% steps)
      Columns = Terminal Growth Rate OR Exit Multiple (from base ± range)

    Returns a DataFrame of intrinsic value per share.
    """
    # ── WACC range ────────────────────────────────────────────────────────────
    half_w = 0.03
    wacc_range = np.linspace(base_wacc - half_w, base_wacc + half_w, wacc_steps)
    wacc_range = np.clip(wacc_range, 0.04, 0.30)

    # ── Terminal param range ──────────────────────────────────────────────────
    if terminal_method == "gordon":
        half_t = 0.02
        tv_range = np.linspace(
            max(0.005, base_terminal_growth - half_t),
            min(base_terminal_growth + half_t, base_wacc - 0.005),
            tv_steps,
        )
        col_label = "Terminal Growth Rate"
        col_fmt = "{:.1%}"
    else:
        half_m = 4.0
        tv_range = np.linspace(
            max(2.0, base_exit_multiple - half_m),
            base_exit_multiple + half_m,
            tv_steps,
        )
        col_label = "EV/EBITDA Multiple"
        col_fmt = "{:.1f}x"

    # ── Build matrix ──────────────────────────────────────────────────────────
    matrix = []
    for w in wacc_range:
        row = []
        for tv_val in tv_range:
            tg = tv_val if terminal_method == "gordon" else base_terminal_growth
            mx = tv_val if terminal_method == "multiple" else base_exit_multiple
            result = run_dcf(
                financial_data,
                wacc=w,
                growth_rate=base_growth_rate,
                terminal_method=terminal_method,
                terminal_growth=tg,
                exit_multiple=mx,
                years=years,
                margin_of_safety=margin_of_safety,
            )
            row.append(result["intrinsic_value_per_share"])
        matrix.append(row)

    # ── Format index / columns ────────────────────────────────────────────────
    if terminal_method == "gordon":
        col_labels = [f"{v:.1%}" for v in tv_range]
    else:
        col_labels = [f"{v:.1f}x" for v in tv_range]

    row_labels = [f"{v:.1%}" for v in wacc_range]

    df = pd.DataFrame(matrix, index=row_labels, columns=col_labels)
    df.index.name = "WACC"
    df.columns.name = col_label
    return df


def plot_sensitivity_heatmap(
    df: pd.DataFrame,
    current_price: float,
    ticker: str,
    terminal_method: str = "gordon",
    figsize: tuple = (10, 6),
) -> plt.Figure:
    """
    Render a color-coded heatmap of the sensitivity table.
    Green = above current price (undervalued), Red = below (overvalued).
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor="#0f1117")
    ax.set_facecolor("#0f1117")

    # Build a diverging colormap centered at the current price
    vmin = df.values.min()
    vmax = df.values.max()
    vcenter = current_price if (vmin < current_price < vmax) else (vmin + vmax) / 2

    cmap = sns.diverging_palette(10, 130, s=85, l=45, as_cmap=True)
    norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)

    # Annotation: show dollar value (compatible with old and new pandas)
    try:
        annot = df.map(lambda v: f"${v:,.0f}")        # pandas ≥ 2.1
    except AttributeError:
        annot = df.applymap(lambda v: f"${v:,.0f}")   # pandas < 2.1


    sns.heatmap(
        df,
        ax=ax,
        cmap=cmap,
        norm=norm,
        annot=annot,
        fmt="",
        linewidths=0.4,
        linecolor="#1e2130",
        cbar_kws={"label": "Intrinsic Value / Share", "shrink": 0.85},
        annot_kws={"size": 9, "weight": "bold"},
    )

    tv_label = "Terminal Growth Rate" if terminal_method == "gordon" else "EV/EBITDA Multiple"
    ax.set_title(
        f"{ticker} — Sensitivity: WACC × {tv_label}\n"
        f"(Current Price: ${current_price:,.2f}  |  Green = Undervalued  |  Red = Overvalued)",
        color="white",
        fontsize=12,
        pad=14,
    )
    ax.set_xlabel(tv_label, color="#a0aec0", fontsize=10)
    ax.set_ylabel("WACC", color="#a0aec0", fontsize=10)
    ax.tick_params(colors="white", labelsize=8)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    plt.setp(ax.get_yticklabels(), rotation=0)

    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color("white")
    cbar.ax.tick_params(colors="white", labelsize=8)

    fig.tight_layout()
    return fig
