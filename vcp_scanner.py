# 831 Operating System: VCP Market Sniper
# Goal: Automate the Marcus Strategy for sub-$5 runners.
# Protect the capital. Protect the time.

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# The 831 Watchlist (Add any tickers you are stalking here)
# Currently loaded with our runners and potential targets
watchlist = ["UGRO", "BIAF", "KOS", "SERV", "TLYS", "RXT", "SOUN", "PLTR"]

def check_vcp(ticker):
    try:
        # Fetch the last 30 days of daily data
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        
        if len(df) < 20:
            return None # Not enough data
            
        current_price = df['Close'].iloc[-1]
        
        # Filter 1: Sniper Ammo Range ($1.00 to $10.00)
        if current_price < 1.00 or current_price > 10.00:
            return None

        # Filter 2: Price Consolidation (Tightening)
        # Is the price resting quietly near its 20-day moving average?
        sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
        price_spread = abs(current_price - sma_20) / sma_20
        
        # Filter 3: Volume Contraction
        # Is today's volume significantly lower than the 20-day average? (The "Quiet" before the move)
        avg_vol_20 = df['Volume'].rolling(window=20).mean().iloc[-1]
        current_vol = df['Volume'].iloc[-1]
        
        is_tight = price_spread < 0.05  # Price is within 5% of the 20 SMA
        is_quiet = current_vol < (avg_vol_20 * 0.7) # Volume is 30% below average
        
        if is_tight and is_quiet:
            return {
                "Ticker": ticker,
                "Price": round(current_price, 2),
                "Status": "🚨 VCP ALERT: Tight & Quiet. Prime for Breakout.",
                "Volume Level": "Low (Accumulation Phase)"
            }
        return None

    except Exception as e:
        return None

# Execute the Scan
print(f"--- 831 SNIPER SCAN INITIATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
print("Scanning for Volume Contraction and Institutional Accumulation...\n")

found_setups = False

for ticker in watchlist:
    result = check_vcp(ticker)
    if result:
        found_setups = True
        print(f"[{result['Ticker']}] - Price: ${result['Price']}")
        print(f" -> {result['Status']}")
        print("-" * 40)

if not found_setups:
    print("🛡️ Fatherhood Audit Triggered: No high-conviction setups found.")
    print("Action: Keep the $117.75 in cash. Close the laptop. Go be a dad.")
