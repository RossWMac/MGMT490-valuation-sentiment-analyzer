"""
app.py
------
Streamlit-based DCF Valuation Tool.

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")

from data_fetcher import get_financial_data
from dcf_engine import run_dcf, compute_wacc
from sensitivity import build_sensitivity_table, plot_sensitivity_heatmap
from sentiment_engine import get_sentiment_data


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="DCF Valuation Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
#  CUSTOM CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  /* Global */
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Sidebar */
  [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
      border-right: 1px solid #30363d;
  }
  [data-testid="stSidebar"] * { color: #e6edf3 !important; }

  /* Main background */
  .stApp { background-color: #0d1117; color: #e6edf3; }

  /* Metric cards */
  .metric-card {
      background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 20px 24px;
      text-align: center;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  .metric-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  }
  .metric-label {
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #8b949e;
      margin-bottom: 6px;
  }
  .metric-value {
      font-size: 28px;
      font-weight: 700;
      color: #e6edf3;
      line-height: 1.1;
  }
  .metric-sub {
      font-size: 13px;
      margin-top: 4px;
  }

  /* Section headers */
  .section-header {
      font-size: 18px;
      font-weight: 600;
      color: #58a6ff;
      border-bottom: 1px solid #21262d;
      padding-bottom: 8px;
      margin-bottom: 16px;
      letter-spacing: 0.02em;
  }

  /* Company header */
  .company-header {
      background: linear-gradient(135deg, #161b22, #1c2128);
      border: 1px solid #30363d;
      border-radius: 16px;
      padding: 24px 32px;
      margin-bottom: 24px;
  }
  .company-name { font-size: 28px; font-weight: 700; color: #e6edf3; }
  .company-sub  { font-size: 14px; color: #8b949e; margin-top: 4px; }

  /* Badges */
  .badge {
      display: inline-block;
      background: #21262d;
      border: 1px solid #30363d;
      border-radius: 20px;
      padding: 2px 12px;
      font-size: 12px;
      color: #8b949e;
      margin-right: 6px;
  }

  /* Upside indicator */
  .upside-positive { color: #3fb950; font-weight: 700; }
  .upside-negative { color: #f85149; font-weight: 700; }

  /* Data table */
  .financials-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
  }
  .financials-table th {
      background: #21262d;
      color: #8b949e;
      padding: 10px 16px;
      text-align: left;
      font-weight: 500;
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.06em;
  }
  .financials-table td {
      padding: 10px 16px;
      border-bottom: 1px solid #21262d;
      color: #e6edf3;
  }
  .financials-table tr:hover td { background: #1c2128; }

  /* Plotly chart container */
  .stPlotlyChart { border-radius: 12px; overflow: hidden; }

  /* Streamlit default overrides */
  div[data-testid="stMarkdownContainer"] p { color: #e6edf3; }
  .stSlider > label { color: #c9d1d9 !important; }
  .stSelectbox > label { color: #c9d1d9 !important; }
  .stTextInput > label { color: #c9d1d9 !important; }
  div[data-baseweb="input"] { background: #21262d !important; border-color: #30363d !important; }
  div[data-baseweb="input"] input { color: #e6edf3 !important; }
  .stButton > button {
      background: linear-gradient(135deg, #238636, #2ea043);
      color: white;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      padding: 10px 24px;
      width: 100%;
      transition: opacity 0.2s;
  }
  .stButton > button:hover { opacity: 0.88; }
  div[data-testid="stExpander"] { background: #161b22; border: 1px solid #30363d; border-radius: 10px; }
  .streamlit-expanderHeader { color: #58a6ff !important; font-weight: 600; }
</style>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def fmt_millions(val: float, currency: str = "USD") -> str:
    """Format a dollar value in millions or billions."""
    symbol = "$" if currency == "USD" else currency + " "
    if val is None:
        return "N/A"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1e12:
        return f"{sign}{symbol}{abs_val/1e12:.2f}T"
    if abs_val >= 1e9:
        return f"{sign}{symbol}{abs_val/1e9:.2f}B"
    if abs_val >= 1e6:
        return f"{sign}{symbol}{abs_val/1e6:.2f}M"
    return f"{sign}{symbol}{abs_val:,.0f}"


def upside_html(pct: float) -> str:
    if pct is None:
        return "<span>N/A</span>"
    css = "upside-positive" if pct >= 0 else "upside-negative"
    arrow = "▲" if pct >= 0 else "▼"
    return f'<span class="{css}">{arrow} {abs(pct):.1f}%</span>'


# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
if "fin_data" not in st.session_state:
    st.session_state.fin_data = None
if "auto_wacc" not in st.session_state:
    st.session_state.auto_wacc = 0.09
if "sentiment_score" not in st.session_state:
    st.session_state.sentiment_score = 0.0
if "sentiment_items" not in st.session_state:
    st.session_state.sentiment_items = []
if "sentiment_trend" not in st.session_state:
    st.session_state.sentiment_trend = []


# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📈 DCF Valuation Tool")
    st.markdown("---")

    # ── Ticker Input ──────────────────────────────────────────────────────────
    st.markdown("### 🔍 Stock Lookup")
    ticker_input = st.text_input(
        "Enter Ticker Symbol",
        value="AAPL",
        placeholder="e.g. AAPL, MSFT, JNJ",
        help="Enter any valid US stock ticker symbol",
    ).strip().upper()

    fetch_btn = st.button("📥  Fetch Financial Data", key="fetch")

    if fetch_btn and ticker_input:
        with st.spinner(f"Fetching data for {ticker_input}…"):
            try:
                data = get_financial_data(ticker_input)
                st.session_state.fin_data = data
                # Auto-compute WACC from fetched data
                auto = compute_wacc(
                    beta=data["beta"],
                    tax_rate=data["tax_rate"],
                    total_debt=data["total_debt"],
                    market_cap=data["market_cap"],
                )
                st.session_state.auto_wacc = round(auto, 4)
                st.success(f"✅ Loaded {data['company_name']}")
                
                # Fetch default sentiment
                score, items, trend = get_sentiment_data(ticker_input, days_window=30, source_type='all')
                st.session_state.sentiment_score = score
                st.session_state.sentiment_items = items
                st.session_state.sentiment_trend = trend
            except Exception as e:
                st.error(f"❌ Error fetching data: {e}")

    st.markdown("---")

    # ── Assumptions (only shown after data loaded) ─────────────────────────
    if st.session_state.fin_data:
        fin = st.session_state.fin_data
        st.markdown("### 🧠 Sentiment Parameters")
        
        sentiment_weight = st.slider(
            "Sentiment Weight (%)",
            min_value=0, max_value=100,
            value=50, step=5,
            format="%d%%",
            help="How strongly sentiment affects your valuation assumptions"
        ) / 100
        
        time_window = st.selectbox(
            "Sentiment Time Window",
            options=[7, 14, 30, 90],
            index=2,
            format_func=lambda x: f"{x} Days",
            help="Lookback period for news/social sentiment"
        )
        
        source_type = st.selectbox(
            "Source Filter",
            options=["all", "news", "social"],
            index=0,
            format_func=lambda x: x.capitalize(),
            help="Filter sentiment sources by type"
        )
        
        with st.expander("Advanced Sentiment Tuning", expanded=False):
            max_wacc_impact = st.slider(
                "Max WACC Impact (±%)",
                min_value=0.0, max_value=5.0,
                value=2.0, step=0.1,
                format="%.1f%%",
                help="How much WACC changes if Sentiment is perfectly 1.0 or -1.0 and Weight is 100%"
            ) / 100
            
            max_growth_impact = st.slider(
                "Max Growth Impact (±%)",
                min_value=0.0, max_value=10.0,
                value=2.0, step=0.5,
                format="%.1f%%",
                help="How much Growth changes if Sentiment is perfectly 1.0 or -1.0 and Weight is 100%"
            ) / 100
        
        # If time window or source filter changed, we should ideally refetch sentiment but since it's fast we'll just recompute on the fly
        score, items, trend = get_sentiment_data(ticker_input, days_window=time_window, source_type=source_type)
        st.session_state.sentiment_score = score
        st.session_state.sentiment_items = items
        st.session_state.sentiment_trend = trend
        
        st.markdown("---")
        st.markdown("### ⚙️ Base Assumptions")

        base_wacc = st.slider(
            "Base WACC (%)",
            min_value=4.0, max_value=25.0,
            value=round(st.session_state.auto_wacc * 100, 1),
            step=0.1,
            format="%.1f%%",
            help="Starting WACC before sentiment adjustment",
        ) / 100

        base_growth = st.slider(
            "Base Near-Term FCF Growth (%)",
            min_value=-10.0, max_value=50.0,
            value=round(max(min(fin.get("revenue_growth_3y", 0.05) * 100, 50.0), -10.0), 1),
            step=0.5,
            format="%.1f%%",
            help="Base annual FCF growth rate",
        ) / 100

        years = st.selectbox(
            "Projection Horizon",
            options=[5, 10],
            index=0,
            help="Number of years to project Free Cash Flows",
        )

        st.markdown("**Terminal Value Method**")
        tv_method = st.radio(
            "Terminal Value Method",
            options=["Gordon Growth Model", "EV/EBITDA Exit Multiple"],
            index=0,
            label_visibility="collapsed",
        )
        terminal_method = "gordon" if tv_method == "Gordon Growth Model" else "multiple"

        if terminal_method == "gordon":
            terminal_growth = st.slider(
                "Terminal Growth Rate (%)",
                min_value=0.5, max_value=5.0,
                value=2.5, step=0.1,
                format="%.1f%%",
                help="Long-run perpetuity growth rate (must be < WACC)",
            ) / 100
            exit_multiple = 12.0
        else:
            exit_multiple = st.slider(
                "EV/EBITDA Exit Multiple",
                min_value=3.0, max_value=30.0,
                value=12.0, step=0.5,
                format="%.1fx",
                help="Terminal year EV/EBITDA multiple",
            )
            terminal_growth = 0.025

        margin_of_safety = st.slider(
            "Margin of Safety (%)",
            min_value=0, max_value=50,
            value=20, step=5,
            format="%d%%",
            help="Discount applied to intrinsic value for safety buffer",
        ) / 100

        st.markdown("---")
        st.markdown("### 📊 Sensitivity Grid")
        sens_wacc_steps = st.slider("WACC rows", 5, 9, 7, step=2)
        sens_tv_steps   = st.slider("Terminal cols", 5, 9, 7, step=2)

    else:
        st.info("Enter a ticker and click **Fetch** to begin.")
        # defaults so the page doesn't crash before fetch
        base_wacc = 0.09
        base_growth = 0.05
        sentiment_weight = 0.5
        max_wacc_impact = 0.02
        max_growth_impact = 0.02
        years = 5
        terminal_method = "gordon"
        terminal_growth = 0.025
        exit_multiple = 12.0
        margin_of_safety = 0.20
        sens_wacc_steps = 7
        sens_tv_steps = 7


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN PANEL
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.fin_data:
    # ── Landing / Welcome ──────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 80px 0 40px 0;">
        <div style="font-size:64px;">📈</div>
        <h1 style="font-size:36px; font-weight:700; color:#e6edf3; margin-bottom:8px;">
            DCF Corporate Valuation Tool
        </h1>
        <p style="font-size:18px; color:#8b949e; max-width:520px; margin:0 auto 24px auto;">
            Enter any stock ticker in the sidebar to instantly retrieve live
            financial data, run a DCF model, and explore a sensitivity analysis.
        </p>
        <div style="display:flex; justify-content:center; gap:16px; flex-wrap:wrap; margin-top:32px;">
    """, unsafe_allow_html=True)

    # Feature cards
    features = [
        ("🌐", "Live Data", "Pulls revenue, FCF, EBITDA, debt, and more via Yahoo Finance"),
        ("⚙️", "Adjustable Inputs", "Tune WACC, growth rate, terminal method, and MoS in real-time"),
        ("🎯", "DCF Engine", "Full WACC-based DCF with Gordon Growth or Exit Multiple TV"),
        ("🔥", "Sensitivity Grid", "2-D heatmap showing intrinsic value across assumption ranges"),
    ]
    cols = st.columns(4)
    for col, (icon, title, desc) in zip(cols, features):
        col.markdown(f"""
        <div class="metric-card" style="text-align:left;">
            <div style="font-size:28px; margin-bottom:8px;">{icon}</div>
            <div style="font-size:15px; font-weight:600; color:#58a6ff; margin-bottom:6px;">{title}</div>
            <div style="font-size:13px; color:#8b949e;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ── Data is loaded ────────────────────────────────────────────────────────────
fin = st.session_state.fin_data
sent_score = st.session_state.sentiment_score
sent_items = st.session_state.sentiment_items
sent_trend = st.session_state.sentiment_trend

# Apply Sentiment adjustments
# High positive sentiment = lower WACC and higher growth
wacc_adj = -(sent_score * sentiment_weight * max_wacc_impact)
growth_adj = (sent_score * sentiment_weight * max_growth_impact)

wacc = base_wacc + wacc_adj
growth_rate = base_growth + growth_adj

# Run Baseline DCF (Without Sentiment)
baseline_dcf = run_dcf(
    fin,
    wacc=base_wacc,
    growth_rate=base_growth,
    terminal_method=terminal_method,
    terminal_growth=terminal_growth,
    exit_multiple=exit_multiple,
    years=years,
    margin_of_safety=margin_of_safety,
)

# Run Adjusted DCF
dcf = run_dcf(
    fin,
    wacc=wacc,
    growth_rate=growth_rate,
    terminal_method=terminal_method,
    terminal_growth=terminal_growth,
    exit_multiple=exit_multiple,
    years=years,
    margin_of_safety=margin_of_safety,
)


# ── Company Header ────────────────────────────────────────────────────────────
price_color = "#3fb950" if fin["current_price"] <= dcf["intrinsic_value_per_share"] else "#f85149"
st.markdown(f"""
<div class="company-header">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
        <div>
            <div class="company-name">{fin['company_name']}</div>
            <div class="company-sub">
                <span class="badge">{fin['ticker']}</span>
                <span class="badge">{fin['sector']}</span>
                <span class="badge">{fin['industry']}</span>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:13px; color:#8b949e;">Current Market Price</div>
            <div style="font-size:36px; font-weight:700; color:{price_color};">
                ${fin['current_price']:,.2f}
            </div>
            <div style="font-size:13px; color:#8b949e;">{fin['currency']}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Key Financials ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Key Financials (TTM)</div>', unsafe_allow_html=True)

fin_rows = [
    ("Revenue",             fin["revenue"],             "Total trailing-twelve-month revenue"),
    ("EBITDA",              fin["ebitda"],               "Earnings before interest, taxes, depreciation & amortization"),
    ("Free Cash Flow",      fin["free_cash_flow"],       "Operating cash flow minus capital expenditures"),
    ("Operating Cash Flow", fin["operating_cash_flow"],  "Cash generated from core operations"),
    ("CapEx",              -fin["capex"],                "Capital expenditures (negative = cash out)"),
    ("Total Debt",          fin["total_debt"],           "Total short + long-term debt"),
    ("Cash & Equivalents",  fin["cash_and_equivalents"], "Cash and liquid assets on balance sheet"),
    ("Net Debt",            fin["net_debt"],             "Total Debt minus Cash"),
]

fin_table_rows = ""
for label, val, tooltip in fin_rows:
    color = "#3fb950" if val >= 0 else "#f85149"
    fin_table_rows += f"""
    <tr>
        <td title="{tooltip}">{label}</td>
        <td style="color:{color}; text-align:right; font-family:monospace;">
            {fmt_millions(val, fin['currency'])}
        </td>
    </tr>"""

col_fin1, col_fin2 = st.columns([1, 1])
with col_fin1:
    st.markdown(f"""
    <table class="financials-table">
        <thead><tr><th>Metric</th><th style="text-align:right;">Value</th></tr></thead>
        <tbody>{fin_table_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

with col_fin2:
    # Beta / growth info card
    growth_hist = fin.get("revenue_growth_3y", 0) or 0
    fcf_margin  = fin.get("fcf_margin") or 0
    risk_data = [
        ("Beta",                 f"{fin['beta']:.2f}",      "Systematic risk vs. market"),
        ("Market Cap",           fmt_millions(fin["market_cap"], fin["currency"]), ""),
        ("Shares Outstanding",   f"{fin['shares_outstanding']/1e6:,.1f}M",  ""),
        ("3Y Revenue CAGR",      f"{growth_hist:.1%}",      "Compound annual revenue growth (historical)"),
        ("FCF Margin",           f"{fcf_margin:.1%}" if fcf_margin else "N/A", "FCF / Revenue"),
        ("Tax Rate (assumed)",   f"{fin['tax_rate']:.0%}",  "Effective corporate tax rate"),
        ("Auto WACC",            f"{st.session_state.auto_wacc:.2%}", "CAPM-derived WACC before your adjustment"),
    ]
    risk_rows = ""
    for label, val, tip in risk_data:
        risk_rows += f'<tr><td title="{tip}">{label}</td><td style="text-align:right; font-family:monospace;">{val}</td></tr>'

    st.markdown(f"""
    <table class="financials-table">
        <thead><tr><th>Metric</th><th style="text-align:right;">Value</th></tr></thead>
        <tbody>{risk_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)


# ── Sentiment Signals ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🧠 Sentiment Signals</div>', unsafe_allow_html=True)

sent_color = "#3fb950" if sent_score >= 0.1 else ("#f85149" if sent_score <= -0.1 else "#8b949e")
sent_label = "BULLISH" if sent_score >= 0.1 else ("BEARISH" if sent_score <= -0.1 else "NEUTRAL")

col_s1, col_s2, col_s3 = st.columns([1, 1, 1])

with col_s1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Aggregate Sentiment Score</div>
        <div class="metric-value" style="color:{sent_color};">{sent_score:+.2f}</div>
        <div class="metric-sub" style="color:#8b949e;">{sent_label} (based on {len(sent_items)} articles)</div>
    </div>
    """, unsafe_allow_html=True)

with col_s2:
    wacc_adj_color = "#3fb950" if wacc_adj <= 0 else "#f85149"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">WACC Adjustment</div>
        <div class="metric-value" style="color:{wacc_adj_color};">{wacc_adj*100:+.2f}%</div>
        <div class="metric-sub" style="color:#8b949e;">Base: {base_wacc*100:.1f}% → Adjusted: {wacc*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
with col_s3:
    growth_adj_color = "#3fb950" if growth_adj >= 0 else "#f85149"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Growth Rate Adjustment</div>
        <div class="metric-value" style="color:{growth_adj_color};">{growth_adj*100:+.2f}%</div>
        <div class="metric-sub" style="color:#8b949e;">Base: {base_growth*100:.1f}% → Adjusted: {growth_rate*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with st.expander("📰 View Recent News & Social Mentions"):
    for item in sent_items[:5]:
        score_color = "#3fb950" if item['score'] > 0 else ("#f85149" if item['score'] < 0 else "#8b949e")
        st.markdown(f"""
        <div style="border-left: 3px solid {score_color}; padding-left: 12px; margin-bottom: 12px;">
            <div style="font-size: 14px; font-weight: 600; color: #e6edf3;">{item['title']}</div>
            <div style="font-size: 12px; color: #8b949e;">
                {item['source']} • Score: <span style="color: {score_color};">{item['score']:+.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

if len(sent_trend) > 0:
    trend_df = pd.DataFrame(sent_trend)
    fig_trend = go.Figure()
    # Add filled area under line for the "SentimentChart" look
    fig_trend.add_trace(go.Scatter(
        x=trend_df['name'], y=trend_df['score'],
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color="#58a6ff", width=2),
        marker=dict(size=6, color="#58a6ff"),
        fillcolor="rgba(88, 166, 255, 0.2)"
    ))
    fig_trend.update_layout(
        template="plotly_dark", paper_bgcolor="#161b22", plot_bgcolor="#161b22",
        title="Sentiment Trend",
        xaxis_title="",
        yaxis_title="Score",
        height=250, margin=dict(t=40, b=20, l=40, r=20),
        yaxis=dict(range=[-1.0, 1.0])
    )
    st.plotly_chart(fig_trend, use_container_width=True)


# ── Pipeline Trace ────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">🌊 Sentiment Ripple Effect (Pipeline Trace)</div>', unsafe_allow_html=True)
st.caption("Tracing exactly how the calculated sentiment propagates through the mathematical pipeline to warp the final output.")

base_iv = baseline_dcf['intrinsic_value_per_share']
adj_iv = dcf['intrinsic_value_per_share']
delta_iv = adj_iv - base_iv
delta_pct = (delta_iv / base_iv) * 100 if base_iv != 0 else 0
delta_color = "#3fb950" if delta_iv >= 0 else "#f85149"

st.markdown(f"""
<div style="background: linear-gradient(135deg, #161b22 0%, #1c2128 100%); border: 1px solid #30363d; border-radius: 12px; padding: 24px; margin-bottom: 24px;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
        <div style="flex: 1; text-align: center; border-right: 1px solid #30363d; padding-right: 15px;">
            <div style="font-size: 13px; color: #8b949e; margin-bottom: 8px;">1. Baseline (No Sentiment)</div>
            <div style="font-size: 24px; font-weight: 700; color: #e6edf3;">${base_iv:,.2f}</div>
        </div>
        <div style="flex: 1; text-align: center; border-right: 1px solid #30363d; padding-right: 15px;">
            <div style="font-size: 13px; color: #8b949e; margin-bottom: 8px;">2. Semantic Signal</div>
            <div style="font-size: 24px; font-weight: 700; color: {sent_color};">{sent_score:+.2f}</div>
        </div>
        <div style="flex: 1; text-align: center; border-right: 1px solid #30363d; padding-right: 15px;">
            <div style="font-size: 13px; color: #8b949e; margin-bottom: 8px;">3. Multipliers Applied</div>
            <div style="font-size: 14px; font-weight: 600; color: #58a6ff;">Weight: {sentiment_weight*100:.0f}%</div>
            <div style="font-size: 14px; font-weight: 600; color: #58a6ff;">Spreads: ±{max_wacc_impact*100:.0f}%</div>
        </div>
        <div style="flex: 1; text-align: center;">
            <div style="font-size: 13px; color: #8b949e; margin-bottom: 8px;">4. Final Output Ripple</div>
            <div style="font-size: 26px; font-weight: 700; color: {delta_color};">{delta_iv:+.2f} ({delta_pct:+.1f}%)</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Valuation Results ─────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">💰 DCF Valuation Results</div>', unsafe_allow_html=True)

upside = dcf.get("upside_pct")
upside_str = upside_html(upside)

c1, c2, c3, c4, c5 = st.columns(5)
valuation_cards = [
    (c1, "Enterprise Value",     fmt_millions(dcf["enterprise_value"], fin["currency"]),
     f'PV FCFs: {fmt_millions(dcf["sum_pv_fcfs"], fin["currency"])}', "#58a6ff"),
    (c2, "Net Debt",             fmt_millions(dcf["net_debt"], fin["currency"]),
     "Debt − Cash",              "#8b949e"),
    (c3, "Equity Value",         fmt_millions(dcf["equity_value"], fin["currency"]),
     "EV − Net Debt",            "#e6edf3"),
    (c4, "Intrinsic Value / Sh", f"${dcf['intrinsic_value_per_share']:,.2f}",
     upside_str,                  "#3fb950" if (upside or 0) >= 0 else "#f85149"),
    (c5, "MoS Price",            f"${dcf['margin_of_safety_price']:,.2f}",
     f"At {margin_of_safety:.0%} margin of safety", "#f0883e"),
]

for col, label, value, sub, color in valuation_cards:
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color};">{value}</div>
        <div class="metric-sub" style="color:#8b949e;">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

# Terminal value breakdown
tv_pct = dcf.get("tv_pct_of_ev", 0)
st.markdown(f"""
<div style="background:#161b22; border:1px solid #30363d; border-radius:10px;
            padding:12px 20px; margin-top:16px; font-size:13px; color:#8b949e;">
    <b style="color:#e6edf3;">Model Settings Used:</b>&nbsp;
    WACC = <b style="color:#58a6ff;">{wacc:.2%}</b> &nbsp;|&nbsp;
    Near-term FCF Growth = <b style="color:#58a6ff;">{growth_rate:.1%}</b> &nbsp;|&nbsp;
    Horizon = <b style="color:#58a6ff;">{years} years</b> &nbsp;|&nbsp;
    Terminal Method = <b style="color:#58a6ff;">{tv_method}</b> &nbsp;|&nbsp;
    {"TGR = <b style='color:#58a6ff;'>" + f"{terminal_growth:.1%}" + "</b>" if terminal_method == "gordon"
     else "Exit Multiple = <b style='color:#58a6ff;'>" + f"{exit_multiple:.1f}x" + "</b>"} &nbsp;|&nbsp;
    Terminal Value = <b style="color:#f0883e;">{tv_pct:.1f}% of EV</b>
</div>
""", unsafe_allow_html=True)


# ── FCF Projection Chart ──────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">📊 Free Cash Flow Projections</div>', unsafe_allow_html=True)

proj_df = pd.DataFrame({
    "Year": [f"Year {y}" for y in dcf["years"]],
    "Projected FCF": dcf["projected_fcfs"],
    "PV of FCF":     dcf["pv_fcfs"],
})

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    name="Projected FCF",
    x=proj_df["Year"],
    y=proj_df["Projected FCF"],
    marker_color="#58a6ff",
    marker_line_color="#1f6feb",
    marker_line_width=1,
    opacity=0.85,
    text=[fmt_millions(v, fin["currency"]) for v in proj_df["Projected FCF"]],
    textposition="outside",
))
fig_bar.add_trace(go.Bar(
    name="PV of FCF",
    x=proj_df["Year"],
    y=proj_df["PV of FCF"],
    marker_color="#3fb950",
    marker_line_color="#238636",
    marker_line_width=1,
    opacity=0.85,
    text=[fmt_millions(v, fin["currency"]) for v in proj_df["PV of FCF"]],
    textposition="outside",
))
# Add base FCF line
fig_bar.add_hline(
    y=fin["free_cash_flow"],
    line_dash="dot",
    line_color="#f0883e",
    annotation_text=f"Base FCF: {fmt_millions(fin['free_cash_flow'], fin['currency'])}",
    annotation_position="top right",
    annotation_font_color="#f0883e",
)
fig_bar.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    barmode="group",
    title=f"{fin['ticker']} — {years}-Year FCF Projection & Present Value",
    xaxis_title="",
    yaxis_title=f"Free Cash Flow ({fin['currency']})",
    legend=dict(
        orientation="h", y=1.02, x=0,
        bgcolor="rgba(0,0,0,0)", font_color="#e6edf3",
    ),
    font=dict(color="#e6edf3", family="Inter"),
    height=400,
    margin=dict(t=60, b=40, l=60, r=20),
)
st.plotly_chart(fig_bar, use_container_width=True)


# ── Sensitivity Analysis ──────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔥 Cross-Component Sensitivity</div>', unsafe_allow_html=True)
st.caption("Shows how intrinsic value per share changes across WACC and terminal assumption ranges, incorporating current sentiment adjustments.")

with st.spinner("Computing sensitivity grid…"):
    sens_df = build_sensitivity_table(
        financial_data=fin,
        base_wacc=wacc, # Uses adjusted WACC
        base_growth_rate=growth_rate, # Uses adjusted growth
        terminal_method=terminal_method,
        base_terminal_growth=terminal_growth,
        base_exit_multiple=exit_multiple,
        years=years,
        margin_of_safety=0.0,
        wacc_steps=sens_wacc_steps,
        tv_steps=sens_tv_steps,
    )

fig_heat = plot_sensitivity_heatmap(
    df=sens_df,
    current_price=fin["current_price"],
    ticker=fin["ticker"],
    terminal_method=terminal_method,
    figsize=(11, 6),
)
st.pyplot(fig_heat)

st.markdown("### 🧠 Sentiment vs. WACC Sensitivity")
st.caption("Illustrates the specific impact of the Sentiment Score on Intrinsic Value by dynamically computing WACC and Growth across different hypothetical sentiment scores.")

# Calculate intrinsic value across a range of sentiment scores (-1.0 to 1.0)
hypothetical_scores = np.linspace(-1.0, 1.0, 21)
intrinsic_values = []
for test_score in hypothetical_scores:
    test_wacc = base_wacc - (test_score * sentiment_weight * max_wacc_impact)
    test_growth = base_growth + (test_score * sentiment_weight * max_growth_impact)
    
    # Ensure WACC doesn't drop below 0 by clipping it minimally
    test_wacc = max(test_wacc, 0.01)
    
    test_dcf = run_dcf(
        fin, wacc=test_wacc, growth_rate=test_growth, terminal_method=terminal_method,
        terminal_growth=terminal_growth, exit_multiple=exit_multiple, years=years, margin_of_safety=0.0
    )
    intrinsic_values.append(test_dcf["intrinsic_value_per_share"])

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=hypothetical_scores, y=intrinsic_values, mode='lines',
    fill='tozeroy',
    line=dict(color="#58a6ff", width=4, shape='spline'),
    fillcolor="rgba(88, 166, 255, 0.15)",
    name="Intrinsic Value"
))
fig_line.add_hline(y=fin["current_price"], line_dash="dash", line_color="#8b949e", annotation_text="Current Market Price")
fig_line.add_vline(x=sent_score, line_dash="dot", line_color="#3fb950", line_width=2, annotation_text="Current Sentiment")
fig_line.update_layout(
    template="plotly_dark", paper_bgcolor="#161b22", plot_bgcolor="#161b22",
    title="Intrinsic Value vs. Hypothetical Sentiment Score",
    xaxis_title="Sentiment Score (-1.0 Bearish to +1.0 Bullish)",
    yaxis_title="Implied Intrinsic Value ($)",
    height=450, margin=dict(t=50, b=40, l=60, r=40),
    hovermode="x unified"
)
st.plotly_chart(fig_line, use_container_width=True)

# Also show the raw sensitivity table
with st.expander("📄 Sensitivity Data Table (WACC vs Terminal)"):
    formatted_df = sens_df.applymap(lambda v: f"${v:,.2f}")
    st.dataframe(
        formatted_df,
        use_container_width=True,
        height=300,
    )


# ── Valuation Summary Assumptions ──────────────────────────────────────────────
with st.expander("ℹ️ Methodology & Assumptions"):
    st.markdown(f"""
**DCF Model Overview**

| Parameter | Value |
|---|---|
| Base Free Cash Flow | {fmt_millions(fin['free_cash_flow'], fin['currency'])} |
| Base Growth Rate | {base_growth:.2%} per year |
| Base WACC (discount rate) | {base_wacc:.2%} |
| Sentiment Weight | {sentiment_weight:.0%} |
| Current Sentiment Score | {sent_score:+.2f} |
| Adjusted Growth Rate | {growth_rate:.2%} per year |
| Adjusted WACC | {wacc:.2%} |
| Projection Horizon | {years} years |
| Terminal Value Method | {tv_method} |
| {"Terminal Growth Rate" if terminal_method == "gordon" else "EV/EBITDA Multiple"} | {f"{terminal_growth:.2%}" if terminal_method == "gordon" else f"{exit_multiple:.1f}x"} |
| Margin of Safety | {margin_of_safety:.0%} |

**Enterprise Value Breakdown**

| Component | Value | % of EV |
|---|---|---|
| PV of Projected FCFs | {fmt_millions(dcf['sum_pv_fcfs'], fin['currency'])} | {100 - dcf['tv_pct_of_ev']:.1f}% |
| PV of Terminal Value | {fmt_millions(dcf['pv_terminal_value'], fin['currency'])} | {dcf['tv_pct_of_ev']:.1f}% |
| **Enterprise Value** | **{fmt_millions(dcf['enterprise_value'], fin['currency'])}** | 100% |

**WACC Components (Auto-calculated)**

| Component | Value |
|---|---|
| Risk-Free Rate | 4.50% (10-yr US Treasury proxy) |
| Equity Risk Premium | 5.50% |
| Beta | {fin['beta']:.2f} |
| Cost of Equity (CAPM) | {(0.045 + fin['beta'] * 0.055):.2%} |
| Pre-tax Cost of Debt | 5.00% |
| Tax Rate | {fin['tax_rate']:.0%} |
| Auto-calculated WACC | {st.session_state.auto_wacc:.2%} |

> **Disclaimer:** This tool is for educational purposes only. All valuations are estimates based
> on publicly available data and simplified models. This is not investment advice.
    """)


# ═══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center; padding: 40px 0 20px 0; color:#484f58; font-size:12px;">
    DCF Valuation Tool — MGMT 490 Project 1 &nbsp;|&nbsp;
    Data via Yahoo Finance &nbsp;|&nbsp;
    For educational use only
</div>
""", unsafe_allow_html=True)
