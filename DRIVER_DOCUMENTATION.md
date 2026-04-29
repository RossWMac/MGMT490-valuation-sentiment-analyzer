# Valuation + Sentiment Analyzer: DRIVER Documentation & Operator's Manual

## Target Audience
This manual is provided for grading administrators, technical reviewers, and end-users operating the Unified Valuation & Sentiment Analysis Dashboard created by combining MGMT 490 - Project 1 and Project 2.

---

## 1. System Architecture & Operation
The dashboard is a Streamlit-based Python application designed to dynamically integrate Discounted Cash Flow (DCF) models with real-time semantic sentiment aggregation. 

**Boot Sequence:**
1. Navigate to the unified project root: `cd valuation-sentiment-analyzer`
2. Activate the virtual environment (if configured): `source .venv/bin/activate`
3. Execute the localized Streamlit server: `streamlit run app.py`
4. Access the terminal via browser: `http://localhost:8501`

*Note: The application performs live HTTP calls to external networks (Yahoo Finance, Google News) to calculate live equity metrics and live sentiment scores. A stable internet connection is required.*

---

## 2. Interactive Parameters (Driving the Dashboard)
The dashboard strictly meets the dynamic input and cross-component integration requirements of the assignment via the Control Sidebar.

### A. Ticker Indexing & Live Data
- Input any valid US stock ticker (e.g., `AAPL`, `MSFT`, `TSLA`) into the search bar.
- **Validation:** The engine immediately proxies a query to Yahoo Finance. If the ticker is invalid, the system rejects it safely. If valid, the engine automatically populates current real-world metrics including Beta, EBITDA, outstanding shares, and current market price.

### B. Core DCF Assumptions
- Users can manually set the baseline `WACC` and `Near-Term FCF Growth Rate`.
- Users can toggle between **Gordon Growth Model** (perpetuity) and **EV/EBITDA Exit Multiple** methods for Terminal Value calculations.

### C. Advanced Sentiment Filtering & Weighting
- **Time Window Adjustments**: A temporal dropdown allows toggling the lookback period for scraping articles (7 Days, 14 Days, 30 Days, 90 Days).
- **Source Sorting**: Users can actively isolate the sentiment parser to evaluate only **News Articles**, only **Social Media**, or **All Sources**.
- **Sentiment Weight**: A slider (0% to 100%) that determines exactly how heavily the application should let the public sentiment dictate the financial valuation.

### D. Advanced Tuning (Impact Spreads)
- Users can open the **Advanced Sentiment Tuning** expander to explicitly cap the maximum adjustment boundaries.
- **Max WACC Impact**: Limits how much a perfect 1.0 (or -1.0) sentiment score can adjust the discount rate.
- **Max Growth Impact**: Limits how much a perfect 1.0 (or -1.0) sentiment score can boost or penalize the Free Cash Flow projections.

---

## 3. Deep Integration & Data Verification
To verify the fidelity of the platform and the integration between Project 1 and Project 2 during demonstrations:

1. **Cross-Component Math Auditing**:
   - Navigate to the `🧠 Sentiment Signals` panel. You will see the base WACC alongside the mathematically adjusted WACC (calculated via: `wacc_adj = -(sent_score * sentiment_weight * max_wacc_impact)`).
   - Positive sentiment mathematically suppresses the discount rate (lowering perceived risk) and artificially boosts near-term growth rates, immediately altering the generated Enterprise Value.
2. **Sentiment Verification**:
   - Expand the `📰 View Recent News & Social Mentions` tab. You can verify the individual live articles scraped from the web, their source, and the algorithmic score assigned to them.
3. **Cross-Component Sensitivity Heatmap**:
   - Scroll to the bottom of the dashboard to view the **Intrinsic Value vs. Hypothetical Sentiment Score** spline chart. This interactive Plotly graph allows auditors to hover and verify exactly how moving the sentiment score from a Bearish -1.0 to a Bullish +1.0 completely reframes the intrinsic value of the asset.
4. **WACC vs. Terminal Value Sensitivity Matrix**:
   - The dashboard includes a traditional 2D heatmap demonstrating how shifts in the (sentiment-adjusted) WACC interact with terminal multiples to form a range of potential valuations.

---

## 4. Technical Resilience
- The underlying financial engine subverts reliance on static spreadsheets by programmatically scraping `yfinance` arrays, ensuring the application remains accurate to today's market.
- The sentiment engine dynamically parses XML feeds (Google News RSS) and cross-references a historical JSON datastore to guarantee enough data density across the 90-day horizon, ensuring the application never crashes due to a lack of live media coverage on obscure tickers.
