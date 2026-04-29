"""
data_fetcher.py
---------------
Fetches financial data for a given stock ticker using yfinance.
Returns a clean dictionary of the metrics needed for DCF analysis.
"""

import yfinance as yf
import numpy as np


def get_financial_data(ticker: str) -> dict:
    """
    Pull all required financial data from Yahoo Finance.

    Returns a dict with keys:
        ticker, company_name, sector, industry, current_price,
        market_cap, shares_outstanding,
        revenue, ebitda, net_income,
        free_cash_flow, operating_cash_flow, capex,
        total_debt, cash_and_equivalents, net_debt,
        beta, tax_rate,
        revenue_growth_3y, fcf_margin,
        currency
    """
    stock = yf.Ticker(ticker.upper())
    info = stock.info

    # ── Basic Info ─────────────────────────────────────────────────────────────
    company_name = info.get("longName") or info.get("shortName") or ticker.upper()
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    current_price = (
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("previousClose")
        or 0.0
    )
    market_cap = info.get("marketCap", 0) or 0
    shares_outstanding = info.get("sharesOutstanding", 0) or 0
    currency = info.get("currency", "USD")

    # ── Income Statement Metrics ───────────────────────────────────────────────
    revenue = info.get("totalRevenue", 0) or 0
    ebitda = info.get("ebitda", 0) or 0
    net_income = info.get("netIncomeToCommon", 0) or 0

    # ── Cash Flow Metrics ──────────────────────────────────────────────────────
    operating_cash_flow = info.get("operatingCashflow", 0) or 0
    free_cash_flow = info.get("freeCashflow", 0) or 0

    # CapEx: try info dict first, then fall back to cashflow statement
    capex = info.get("capitalExpenditures", 0) or 0
    if capex == 0:
        capex = _get_capex_from_cashflow(stock)
    capex_positive = abs(capex)

    # Derive FCF from OCF - CapEx if not directly available or zero
    if free_cash_flow == 0 and operating_cash_flow != 0:
        free_cash_flow = operating_cash_flow - capex_positive

    # ── Balance Sheet Metrics ─────────────────────────────────────────────────
    total_debt = info.get("totalDebt", 0) or 0
    cash_and_equivalents = info.get("totalCash", 0) or 0
    net_debt = total_debt - cash_and_equivalents

    # ── Risk / Tax ────────────────────────────────────────────────────────────
    beta = info.get("beta", 1.0) or 1.0
    # Approximate effective tax rate
    pretax_income = info.get("grossProfits", 0) or 0
    # Use a default US corporate tax rate if we cannot compute it
    tax_rate = 0.21

    # ── Historical Growth (try from financials) ───────────────────────────────
    revenue_growth_3y = _calc_revenue_growth(stock)

    # ── FCF Margin ────────────────────────────────────────────────────────────
    fcf_margin = (free_cash_flow / revenue) if revenue else None

    return {
        "ticker": ticker.upper(),
        "company_name": company_name,
        "sector": sector,
        "industry": industry,
        "current_price": current_price,
        "market_cap": market_cap,
        "shares_outstanding": shares_outstanding,
        "currency": currency,
        # Income
        "revenue": revenue,
        "ebitda": ebitda,
        "net_income": net_income,
        # Cash Flow
        "operating_cash_flow": operating_cash_flow,
        "capex": capex_positive,
        "free_cash_flow": free_cash_flow,
        # Balance Sheet
        "total_debt": total_debt,
        "cash_and_equivalents": cash_and_equivalents,
        "net_debt": net_debt,
        # Risk
        "beta": beta,
        "tax_rate": tax_rate,
        # Derived
        "revenue_growth_3y": revenue_growth_3y,
        "fcf_margin": fcf_margin,
    }


def _calc_revenue_growth(stock) -> float:
    """Compute 3-year CAGR of revenue from annual financials."""
    try:
        financials = stock.financials  # columns = years, rows = line items
        if financials is None or financials.empty:
            return 0.05  # default 5%
        # Row label variations
        rev_row = None
        for label in ["Total Revenue", "Revenue"]:
            if label in financials.index:
                rev_row = financials.loc[label]
                break
        if rev_row is None:
            return 0.05
        rev_row = rev_row.dropna().sort_index()
        if len(rev_row) < 2:
            return 0.05
        earliest = float(rev_row.iloc[0])
        latest = float(rev_row.iloc[-1])
        n = len(rev_row) - 1
        if earliest <= 0:
            return 0.05
        cagr = (latest / earliest) ** (1 / n) - 1
        return max(min(cagr, 0.50), -0.20)  # clamp to [-20%, +50%]
    except Exception:
        return 0.05


def _get_capex_from_cashflow(stock) -> float:
    """Read CapEx directly from the yfinance cashflow statement."""
    try:
        cf = stock.cashflow
        if cf is None or cf.empty:
            return 0.0
        for label in ["Capital Expenditure", "Capital Expenditures", "Purchase Of Property Plant And Equipment"]:
            if label in cf.index:
                val = cf.loc[label].dropna()
                if not val.empty:
                    return float(val.iloc[0])  # most recent year
        return 0.0
    except Exception:
        return 0.0

