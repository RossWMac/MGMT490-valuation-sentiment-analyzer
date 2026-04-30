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
# DRIVER™ Methodology Application Report
**Project:** Unified Valuation + Sentiment Analyzer
**Date:** April 2026

This document details how the DRIVER™ Framework (Discover & Define, Represent, Implement, Validate, Evolve, Reflect) was systematically applied during the development of the Valuation + Sentiment Analyzer to ensure professional-grade AI operation.

---

## D - DISCOVER & DEFINE
**Define Destination and Assess Resources**
* **The Goal:** The primary objective was clearly defined before engaging the AI: Combine a Python DCF valuation tool (Project 1) and a React sentiment analyzer (Project 2) into a unified, high-fidelity application that demonstrates cross-component sensitivity.
* **The Resources:** We assessed the existing codebases and recognized a language mismatch (React vs. Python).
* **The AI Partnership:** Instead of wandering aimlessly, I instructed the AI on the exact mathematical relationship needed ("Use sentiment signals to adjust valuation assumptions like growth rate and risk premium") and explicitly defined the required UI parameters (Sentiment weight, time window).

## R - REPRESENT
**Visualize Analytical Workflows**
* **The Process:** Rather than blindly coding, we first represented the architecture. We visualized the data flow: Ticker -> Yahoo Finance API -> DCF Math <- Google News Scraper <- NLP Scoring.
* **The Solution:** We determined that the cleanest representation of this workflow was a single, unified Streamlit dashboard, requiring the React frontend to be completely ported into Python. 
* **The AI Partnership:** I worked with the AI to map out the "Ripple Effect Pipeline Trace"—a visual step-by-step representation explicitly showing how the baseline math, sentiment modifiers, and final intrinsic value interact on the screen.

## I - IMPLEMENT
**Execute with AI Partnership**
* **The Execution:** We executed the build by treating the AI as a highly capable junior developer. I maintained strict human control over the architectural decisions (e.g., keeping data parsing offline/fallback capable to prevent crashes), while directing the AI to write the specific, bounded tasks like the Plotly charting logic and Streamlit CSS styling.
* **The AI Partnership:** The AI successfully bridged the gap between the complex qualitative NLP logic and the quantitative DCF formulas, writing the boilerplate code required to fetch XML RSS feeds and parse Yahoo Finance JSON arrays.

## V - VALIDATE
**Verify Accuracy and Reliability**
* **The Verification:** We did not blindly trust the AI's initial mock numbers. During the drafting of the presentation script, I identified that the AI's hypothetical example for Apple (AAPL) being "bullish" directly contradicted the live bearish reality of Apple's stock that day.
* **The AI Partnership:** To validate the system properly, we built a dedicated `evaluation_harness.py`. This script looped through actual live tickers (AAPL, MSFT, META) to verify that the mathematical adjustments were accurately compounding. We then updated the presentation script to use the exact, verified live data for META to ensure no hallucinations or logical errors existed in the final demo.

## E - EVOLVE
**Optimize and Extend**
* **The Optimization:** Once the base application was functioning, we iterated to improve the idea. The initial implementation utilized a hard-coded ±2% impact for the sentiment modifier.
* **The AI Partnership:** Through iterative ideation with the AI, we evolved the UI by introducing the "Advanced Sentiment Tuning" expander. This extended the platform's capability, allowing users to explicitly define the maximum WACC and Growth impact spreads, turning a static multiplier into a dynamic, professional-grade scenario modeling tool.

## R - REFLECT
**Document and Transfer Knowledge**
* **The Documentation:** The final step was recording the methodology and transferring the knowledge to ensure continuous improvement and institutional memory.
* **The AI Partnership:** I directed the AI to generate a comprehensive `README.md`, a detailed `DRIVER_DOCUMENTATION.md` operator's manual, a Substack post conceptualizing the project, and a 12-minute video presentation script. This documentation ensures that any grading administrator or future developer can seamlessly boot the application, understand the underlying assumptions, and verify the platform's fidelity without relying on tribal knowledge.

---

**Conclusion:**
By adhering to the Kasparov Principle—*human + machine + better process*—the DRIVER™ methodology transformed what could have been a chaotic codebase merger into a systematic, robust, and highly transparent professional financial application.
