import pandas as pd
import time
from data_fetcher import get_financial_data
from sentiment_engine import get_sentiment_data
from dcf_engine import compute_wacc, run_dcf

def run_evaluation_harness(tickers, sentiment_weight=0.5, max_wacc_impact=0.02, max_growth_impact=0.02):
    print(f"\n🚀 Starting Evaluation Harness for {len(tickers)} tickers...")
    print(f"Parameters: Weight={sentiment_weight*100}%, Max WACC Impact=±{max_wacc_impact*100}%, Max Growth Impact=±{max_growth_impact*100}%\n")
    
    results = []
    
    for ticker in tickers:
        print(f"Processing {ticker}...")
        try:
            # 1. Fetch Financial Data
            fin_data = get_financial_data(ticker)
            
            # 2. Compute Base Assumptions
            base_wacc = compute_wacc(
                beta=fin_data["beta"],
                tax_rate=fin_data["tax_rate"],
                total_debt=fin_data["total_debt"],
                market_cap=fin_data["market_cap"]
            )
            base_growth = max(min(fin_data.get("revenue_growth_3y", 0.05), 0.50), -0.10)
            
            # 3. Run Baseline DCF
            baseline_dcf = run_dcf(
                fin_data,
                wacc=base_wacc,
                growth_rate=base_growth,
                terminal_method="gordon",
                terminal_growth=0.025,
                years=5,
                margin_of_safety=0.0
            )
            base_iv = baseline_dcf["intrinsic_value_per_share"]
            
            # 4. Fetch Sentiment Data
            sent_score, _, _ = get_sentiment_data(ticker, days_window=30, source_type='all')
            
            # 5. Apply Sentiment Multipliers
            wacc_adj = -(sent_score * sentiment_weight * max_wacc_impact)
            growth_adj = (sent_score * sentiment_weight * max_growth_impact)
            
            adj_wacc = max(base_wacc + wacc_adj, 0.01) # Prevent negative WACC
            adj_growth = base_growth + growth_adj
            
            # 6. Run Adjusted DCF
            adj_dcf = run_dcf(
                fin_data,
                wacc=adj_wacc,
                growth_rate=adj_growth,
                terminal_method="gordon",
                terminal_growth=0.025,
                years=5,
                margin_of_safety=0.0
            )
            adj_iv = adj_dcf["intrinsic_value_per_share"]
            
            # Calculate Ripple Effect
            delta_dollar = adj_iv - base_iv
            delta_pct = (delta_dollar / base_iv) * 100 if base_iv != 0 else 0
            
            # Store Results
            results.append({
                "Ticker": ticker,
                "Market Price": f"${fin_data['current_price']:.2f}",
                "Base IV": f"${base_iv:.2f}",
                "Sentiment": f"{sent_score:+.2f}",
                "Adj IV": f"${adj_iv:.2f}",
                "Ripple Effect ($)": f"${delta_dollar:+.2f}",
                "Ripple Effect (%)": f"{delta_pct:+.1f}%"
            })
            
            time.sleep(1) # Prevent API rate limiting
            
        except Exception as e:
            print(f"❌ Failed to process {ticker}: {e}")
            results.append({
                "Ticker": ticker,
                "Market Price": "ERROR",
                "Base IV": "ERROR",
                "Sentiment": "ERROR",
                "Adj IV": "ERROR",
                "Ripple Effect ($)": "ERROR",
                "Ripple Effect (%)": "ERROR"
            })
            
    # Compile and Output Results
    df = pd.DataFrame(results)
    
    print("\n" + "="*80)
    print("📊 HARNESS EVALUATION RESULTS")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80)
    
    # Save to CSV for the analyst
    output_filename = "harness_results.csv"
    df.to_csv(output_filename, index=False)
    print(f"\n✅ Evaluation complete! Results saved to '{output_filename}'")


if __name__ == "__main__":
    # Define a basket of tickers to evaluate
    basket = ["AAPL", "MSFT", "NVDA", "TSLA", "META"]
    run_evaluation_harness(basket)
