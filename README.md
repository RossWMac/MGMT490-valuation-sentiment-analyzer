# Valuation + Sentiment Analyzer

## Project Description
The Valuation + Sentiment Analyzer is a unified, Python-based Streamlit application that deeply integrates a quantitative Discounted Cash Flow (DCF) model with a qualitative semantic Sentiment Engine. By actively scraping live financial and news data, the application calculates traditional intrinsic equity value, and then algorithmically adjusts its underlying assumptions (such as the Weighted Average Cost of Capital and Near-Term Free Cash Flow Growth Rates) based on the aggregate public sentiment surrounding the asset.

## Project Goals
1. **Dynamic Financial Modeling**: Create a robust DCF valuation tool that pulls real-time data from Yahoo Finance to establish baseline equity valuations.
2. **Semantic Contextualization**: Develop a Sentiment Engine that scrapes Google News and historical databases to score public perception between -1.0 (Bearish) and +1.0 (Bullish).
3. **Deep Cross-Component Integration**: Mathematically bridge the gap between qualitative news and quantitative finance by explicitly allowing sentiment scores to modify risk premiums (WACC) and revenue expectations (Growth).
4. **Interactive Transparency**: Provide users with deep parameter control (Sentiment Weight, Time Windows, Max Impact spreads) and clear cross-component sensitivity visualizations to demonstrate exactly how the inputs shift the final outputs.

## Instructions for Running the Application
### Prerequisites
- Python 3.8+
- Active Internet Connection

### Boot Sequence
1. Open your terminal and navigate to the project directory:
   ```bash
   cd valuation-sentiment-analyzer
   ```
2. (Optional but Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch the Streamlit dashboard:
   ```bash
   streamlit run app.py
   ```
5. A browser window will automatically open at `http://localhost:8501`. Enter a valid stock ticker (e.g., `AAPL`) to begin your analysis.

## DRIVER Workflow
Throughout the development of this application, specific DRIVER AI-collaboration skills were utilized to achieve the complex integration of the two projects.

* **`/driver:define`**: The project began by strictly defining the architecture. I instructed the AI on the precise mathematical relationship needed (e.g., "Use sentiment signals to adjust valuation assumptions like growth rate and risk premium") and established the exact parameters required for the UI (Sentiment weight, time window).
* **`/driver:evolve`**: Rather than keeping the two projects isolated in different languages (React vs Python), we evolved the architecture into a single "deep integration" Streamlit application. This required porting the React mock data services into a dynamic Python `sentiment_engine.py` capable of scraping live XML feeds to match the real-time nature of the `yfinance` fetcher. We also evolved the UI to add features like the interactive "Source Filter" drop-down.
* **`/driver:reflect`**: Once the core integration was functioning, we stepped back to reflect on whether the project "exceptionally" met the requirements. Through reflection, we realized the initial ±2% hard-coded sentiment adjustment lacked transparency. This reflection drove the addition of the "Advanced Sentiment Tuning" expanders (Max WACC/Growth Impacts) and the implementation of a high-fidelity spline chart to explicitly graph the cross-component sensitivity.

## AI Usage Disclosure and Reflection
**Disclosure**: Artificial Intelligence (Google Gemini / Antigravity) was heavily utilized as a pair-programming partner in the creation of this project. The AI was responsible for porting React logic into Python, generating the Streamlit CSS UI styling, architecting the Plotly data visualizations, and writing the boilerplate mathematical integrations for the DCF engine.

**Reflection**: Utilizing AI as a collaborative tool drastically accelerated the timeline for integrating two previously disparate applications. The most challenging aspect was managing architectural decisions—specifically deciding whether to build a Python backend for the React app or port the React frontend features into Streamlit. Relying on the AI's technical foresight allowed us to choose the Streamlit route, which ultimately provided the smoothest and most stable integration. Overall, the AI proved highly effective at generating data visualizations (like the complex sensitivity matrices) and writing data-scraping logic, enabling a far more polished final product than could have been built manually in the same timeframe.
