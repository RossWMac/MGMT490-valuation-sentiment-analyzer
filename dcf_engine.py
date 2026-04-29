"""
dcf_engine.py
-------------
Core Discounted Cash Flow engine.

Inputs:
    financial_data  : dict from data_fetcher.get_financial_data()
    wacc            : float, e.g. 0.09 (9%)
    growth_rate     : float, near-term FCF / revenue growth, e.g. 0.05 (5%)
    terminal_method : "gordon"  → perpetuity growth model
                      "multiple" → EV/EBITDA exit multiple
    terminal_growth : float, long-run growth rate for Gordon model (e.g. 0.025)
    exit_multiple   : float, EV/EBITDA multiple for the exit multiple method
    years           : int, projection horizon (5 or 10)
    margin_of_safety: float, e.g. 0.20 (20%)

Returns a dict with full DCF outputs.
"""

import numpy as np


def compute_wacc(
    beta: float,
    tax_rate: float,
    total_debt: float,
    market_cap: float,
    risk_free_rate: float = 0.045,   # ~10-yr US Treasury
    equity_risk_premium: float = 0.055,
    pre_tax_cost_of_debt: float = 0.05,
) -> float:
    """
    WACC = (E/V) * Re + (D/V) * Rd * (1 - T)
    where Re is computed via CAPM.
    """
    Re = risk_free_rate + beta * equity_risk_premium  # Cost of equity (CAPM)
    Rd = pre_tax_cost_of_debt                          # Cost of debt
    V = market_cap + total_debt
    if V == 0:
        return Re  # all equity
    E_weight = market_cap / V
    D_weight = total_debt / V
    wacc = E_weight * Re + D_weight * Rd * (1 - tax_rate)
    # Keep WACC in a sensible range
    return max(min(wacc, 0.30), 0.04)


def project_fcf(
    base_fcf: float,
    growth_rate: float,
    years: int,
) -> list:
    """
    Project Free Cash Flows for `years` years using a constant `growth_rate`.
    Returns a list of projected FCF values (Year 1 … Year N).
    """
    projected = []
    fcf = base_fcf
    for _ in range(years):
        fcf *= (1 + growth_rate)
        projected.append(fcf)
    return projected


def terminal_value_gordon(
    last_fcf: float,
    wacc: float,
    terminal_growth: float,
) -> float:
    """
    Terminal Value (Gordon Growth Model) at end of projection horizon.
    TV = FCF_N * (1 + g) / (WACC - g)
    """
    if wacc <= terminal_growth:
        # Prevent divide-by-zero / negative TV
        return last_fcf * 20  # rough fallback cap
    return last_fcf * (1 + terminal_growth) / (wacc - terminal_growth)


def terminal_value_multiple(
    ebitda: float,
    exit_multiple: float,
) -> float:
    """
    Terminal Value (Exit Multiple Method).
    TV = EBITDA * EV/EBITDA multiple
    """
    return ebitda * exit_multiple


def run_dcf(
    financial_data: dict,
    wacc: float,
    growth_rate: float,
    terminal_method: str = "gordon",
    terminal_growth: float = 0.025,
    exit_multiple: float = 12.0,
    years: int = 5,
    margin_of_safety: float = 0.20,
) -> dict:
    """
    Full DCF calculation. Returns a results dictionary.
    """
    base_fcf = financial_data.get("free_cash_flow", 0) or 0
    ebitda = financial_data.get("ebitda", 0) or 0
    net_debt = financial_data.get("net_debt", 0) or 0
    shares = financial_data.get("shares_outstanding", 1) or 1

    # ── Project FCFs ──────────────────────────────────────────────────────────
    projected_fcfs = project_fcf(base_fcf, growth_rate, years)

    # ── PV of projected FCFs ──────────────────────────────────────────────────
    pv_fcfs = []
    for i, fcf in enumerate(projected_fcfs, start=1):
        pv = fcf / (1 + wacc) ** i
        pv_fcfs.append(pv)
    sum_pv_fcfs = sum(pv_fcfs)

    # ── Terminal Value ────────────────────────────────────────────────────────
    last_fcf = projected_fcfs[-1]
    if terminal_method == "gordon":
        tv = terminal_value_gordon(last_fcf, wacc, terminal_growth)
    else:
        tv = terminal_value_multiple(ebitda, exit_multiple)

    pv_terminal = tv / (1 + wacc) ** years

    # ── Enterprise Value ──────────────────────────────────────────────────────
    enterprise_value = sum_pv_fcfs + pv_terminal

    # ── Equity Value ──────────────────────────────────────────────────────────
    equity_value = enterprise_value - net_debt

    # ── Per-share intrinsic value ──────────────────────────────────────────────
    intrinsic_value_per_share = equity_value / shares if shares else 0
    mos_price = intrinsic_value_per_share * (1 - margin_of_safety)

    # ── Current price comparison ──────────────────────────────────────────────
    current_price = financial_data.get("current_price", 0) or 0
    upside_pct = (
        (intrinsic_value_per_share - current_price) / current_price * 100
        if current_price
        else None
    )

    return {
        # Projection data
        "projected_fcfs": projected_fcfs,
        "pv_fcfs": pv_fcfs,
        "years": list(range(1, years + 1)),
        # Terminal value
        "terminal_value": tv,
        "pv_terminal_value": pv_terminal,
        "tv_pct_of_ev": (pv_terminal / enterprise_value * 100) if enterprise_value else 0,
        # Key outputs
        "sum_pv_fcfs": sum_pv_fcfs,
        "enterprise_value": enterprise_value,
        "net_debt": net_debt,
        "equity_value": equity_value,
        "shares_outstanding": shares,
        "intrinsic_value_per_share": intrinsic_value_per_share,
        "margin_of_safety_price": mos_price,
        "current_price": current_price,
        "upside_pct": upside_pct,
        # Inputs echoed back
        "wacc_used": wacc,
        "growth_rate_used": growth_rate,
        "terminal_method": terminal_method,
        "terminal_growth_used": terminal_growth if terminal_method == "gordon" else None,
        "exit_multiple_used": exit_multiple if terminal_method == "multiple" else None,
    }
