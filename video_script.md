# Valuation + Sentiment Analyzer: 12-Minute Video Presentation Script

**Estimated Runtime:** 12 Minutes (~1,800 words)  
**Tone:** Professional, Analytical, Academic

---

## [0:00 - 2:00] Introduction: Problem, Approach, & Solution
**(Visual: Title slide or screen recording of the dashboard landing page)**

"Hello everyone. Today I'm going to walk you through my final project: The Unified Valuation and Sentiment Analyzer. 

First, let's establish the **Problem**. In quantitative finance, traditional Discounted Cash Flow (DCF) models operate under the assumption of perfectly rational markets. However, we know from behavioral finance that actual stock prices are frequently driven by highly emotional, irrational public sentiment. The problem is that these qualitative emotions are incredibly difficult to factor into a rigid quantitative equation. 

My **Approach** to this problem was to combine two previously independent systems I had built: a DCF valuation engine (Project 1) and a semantic Sentiment Analyzer (Project 2). Instead of keeping them isolated, I used Python and Streamlit to deeply integrate them into a single, cohesive architecture.

The **Solution** is this dashboard. We mathematically bridge the gap between qualitative news and quantitative finance by explicitly allowing our algorithm to scrape public sentiment and use those scores to automatically modify our core DCF assumptions—specifically adjusting the Weighted Average Cost of Capital (WACC) and Near-Term Free Cash Flow Growth Rates before the final intrinsic value is calculated.

Ultimately, our **Findings** show that by turning emotional volatility into a dynamic mathematical multiplier, we can trace exactly how a single news cycle ripples down to alter the final perceived intrinsic value of an asset."

---

## [2:00 - 6:00] Demonstration: Walkthrough & The Ripple Effect
**(Visual: Type 'META' into the sidebar. Click 'Fetch Financial Data'.)**

"Let me demonstrate exactly how this works using a live example: Meta Platforms, ticker symbol META. 

When I type META into the sidebar and hit fetch, the engine does two things simultaneously. 
First, our data fetcher script pings the Yahoo Finance API to pull down live, trailing-twelve-month data like Revenue, EBITDA, and Total Debt. More importantly, it pulls the stock's Beta, which it immediately uses within the Capital Asset Pricing Model (CAPM) to auto-calculate a baseline WACC. 
Second, our sentiment engine scrapes live Google News RSS feeds to grab today's headlines, while also querying our historical database to fulfill a robust 30-day timeline.

If we run a pure, standard DCF without any sentiment adjustments, our baseline intrinsic value for Meta comes out to around $245 a share.

**(Visual: Scroll to the 'Sentiment Signals' section and the 'Advanced Sentiment Tuning' expander. Adjust the sliders.)**

But the market doesn't trade in a vacuum. Let's see how sentiment changes the math. Our engine has scored Meta's recent news, returning an aggregate score of roughly +0.22 (Bullish). 

I want to trace exactly how a change in this one qualitative input ripples through the entire pipeline to warp our final quantitative output. 
On the sidebar, I open 'Advanced Sentiment Tuning'. I'll set my 'Sentiment Weight' to 50%—meaning I only trust the sentiment half as much as the raw financials. I'll set my 'Max WACC Impact' to 2.0% and my 'Max Growth Impact' to 2.0%. 

Because the sentiment is bullish (+0.22), the algorithm assumes two things:
1. The company is perceived as safer right now, so it *reduces* the discount rate (WACC). 
2. Consumer demand is likely high, so it *increases* the near-term cash flow growth projections.

The math executes perfectly: Our WACC drops from 11.3% down to 11.1%, and our Growth Rate is boosted from 19.9% up to 20.1%. 

If we scroll down to our new 'Sentiment Ripple Effect Pipeline Trace', you can see the end-to-end workflow visualized. We started with a baseline Intrinsic Value of $245. We applied the semantic signal of +0.22 and our custom multipliers. The ripple effect of altering both the discount rate and the cash flow projections results in a final, adjusted Intrinsic Value of $254. 

**(Visual: Point out the 'Intrinsic Value vs. Hypothetical Sentiment Score' line chart)**
Furthermore, if we look at our line chart, we can explicitly hover and see how the valuation would change if the news cycle suddenly turned bearish tomorrow. We are visually mapping market psychology directly to intrinsic value."

---

## [6:00 - 8:30] Limitations of the System
**(Visual: Scroll to the 'Methodology & Assumptions' disclaimer or the 'View Recent News' expander)**

"Now, while this integration is powerful, it's vital to address the system's limitations. 

First, we have **Data Quality and API Limitations**. To prevent rate-limiting, our live news scraper only pulls a handful of articles from Google News. To fulfill the requirement of having a dense 90-day time window, it relies on a static JSON database of historical data. Therefore, the sentiment score isn't a perfect reflection of the *entire* internet's viewpoint—it's a sampled approximation. 

Second, we have **Model Assumptions and NLP Limitations**. The sentiment parser uses a deterministic, pseudo-randomized algorithm based on the publisher and title string to assign scores. It lacks a true deep-learning Natural Language Processing transformer model, meaning it cannot understand complex financial sarcasm, nuance, or 'buy the rumor, sell the news' dynamics. 

Finally, there is the risk of **Compounding Errors Across Components**. This is the danger of deep integration. If our sentiment engine misinterprets a neutral news story as highly bearish, it will artificially raise the WACC *and* lower the growth rate. Because the DCF formula is highly sensitive to the discount rate in its denominator, altering both variables in the same direction based on a single faulty sentiment score will compound the error, resulting in a wildly inaccurate and heavily penalized Intrinsic Value. "

---

## [8:30 - 10:30] How Would a Professional Use This?
**(Visual: Scroll to the 'Cross-Component Sensitivity Heatmap' and interact with the WACC/Terminal sliders)**

"Despite these limitations, how would a professional actually use a tool like this in the real world?

A professional would *never* use this application to make a final, execution-level investment decision. The assumptions in a DCF are too rigid, and automated sentiment is too volatile to blindly trade off of. 

However, a professional *would* use this as a powerful **Top-of-Funnel Screening Tool and Due Diligence Support system**. 

Imagine an equity analyst tracking 50 different companies. They could use this dashboard to quickly run scenario analyses. If a company is currently trading at $150, but the baseline DCF says it's only worth $120, the analyst can ask: *'How bullish does the market psychology need to be to justify this $150 price tag?'* 

Using the cross-component sensitivity chart, they can trace the line and see that the market is currently pricing the stock as if the sentiment score is a perfect +1.0. If the analyst looks at the actual 'Sentiment Signals' panel and sees the real-world sentiment is only a +0.20, they immediately know the stock is overvalued by emotional retail traders and is ripe for a correction. It provides a structured sandbox to quantify exactly how much of a stock's current price is driven by cash flow versus the current news cycle.

Furthermore, to make this realistic for institutional use, I implemented a custom **Evaluation Harness** script that runs entirely outside of this Streamlit UI. This harness allows an analyst to input a basket of hundreds of tickers—say, the entire S&P 500. The harness loops through the list, automatically fetches the baseline financial data, scrapes the sentiment scores, calculates the exact dollar-value 'Ripple Effect' delta for every single stock, and exports it directly into a clean CSV file. This bridges the gap between single-stock due diligence and macro-level market screening."

---

## [10:30 - 12:00] AI Usage Disclosure & Reflection
**(Visual: Show the terminal code or the README.md on screen)**

"Before I conclude, I want to provide a formal disclosure regarding my use of Artificial Intelligence during this project's development. 

**Disclosure**: I utilized AI—specifically Google Gemini through the Antigravity framework—as an active pair-programming partner. The AI assisted with porting the original React logic into Python, generating the Streamlit CSS UI styling, architecting the Plotly data visualizations, and writing the mathematical integrations for the DCF engine.

**Reflection**: Integrating two highly complex systems is usually a messy process. By using the 'DRIVER' workflow—specifically the 'Define', 'Evolve', and 'Reflect' skills—the AI drastically accelerated the timeline. For example, instead of awkwardly connecting a React frontend to a Python backend, the AI helped me *Evolve* the architecture into a unified Streamlit application. Furthermore, when I *Reflected* on the rubric requirement to trace the pipeline's ripple effect, the AI helped me quickly spin up the exact 'Pipeline Trace' visualizer we saw earlier. The AI proved to be an invaluable tool for quickly prototyping UI and data-scraping logic, allowing me to focus on the high-level financial concepts and workflow design rather than getting bogged down in boilerplate syntax.

Thank you all for your time, and I'd be happy to answer any questions."
