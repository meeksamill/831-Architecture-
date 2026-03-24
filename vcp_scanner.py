"""
831 Operating System: Ghost Protocol Omni-Scan
Goal: Automate institutional accumulation detection across the entire S&P 500.
Protect the capital. Protect the time.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import ssl
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bypass SSL certificate issues for dynamic ticker fetching
ssl._create_default_https_context = ssl._create_unverified_context

# Configuration constants
MIN_DATA_POINTS = 20
VOLUME_CONTRACTION_THRESHOLD = 0.80  # 20% contraction
PRICE_TIGHTNESS_THRESHOLD = 0.05  # 5% variance
SQUAT_BAR_VOLUME_MULTIPLIER = 1.2  # 20% above average
SQUAT_BAR_CLOSE_RATIO = 0.4  # Price closes in lower 40% of range
BATCH_SIZE = 100
LOOKBACK_PERIOD = "2mo"
RECENT_LOOKBACK = 15  # 3 weeks of tape action
RECENT_VOLUME_WINDOW = 3  # Last 3 days


class MarketScanner:
    """Scans S&P 500 for institutional accumulation patterns."""
    
    def __init__(self):
        self.tickers = []
        self.valid_setups = []
    
    @staticmethod
    def get_broad_market_tickers() -> List[str]:
        """Dynamically fetches all S&P 500 tickers."""
        try:
            logger.info("🌐 Fetching Broad Market Tickers from Wikipedia...")
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            table = pd.read_html(url)[0]
            tickers = table['Symbol'].tolist()
            # Clean up formatting for Yahoo Finance (e.g., BRK.B -> BRK-B)
            cleaned_tickers = [ticker.replace('.', '-') for ticker in tickers]
            logger.info(f"✅ Successfully fetched {len(cleaned_tickers)} tickers")
            return cleaned_tickers
        except Exception as e:
            logger.error(f"❌ Failed to fetch tickers: {e}")
            return []
    
    @staticmethod
    def detect_squat_bar(bar: pd.Series, avg_volume: float) -> bool:
        """
        Detects hidden selling (Squat Bars):
        High volume but price closes poorly = institutional offloading.
        
        Returns True if squat bar detected (ABORT signal).
        """
        high_volume = bar['Volume'] > avg_volume * SQUAT_BAR_VOLUME_MULTIPLIER
        range_size = bar['High'] - bar['Low']
        
        if range_size == 0:
            return False
        
        close_ratio = (bar['Close'] - bar['Low']) / range_size
        poor_close = close_ratio < SQUAT_BAR_CLOSE_RATIO
        
        return high_volume and poor_close
    
    @staticmethod
    def analyze_vcp_and_vpa(ticker: str, data: pd.DataFrame) -> bool:
        """
        Core Marcus Logic: VCP, Institutional Accumulation, and Squat Bar detection.
        Optimized for the $180 -> $300 grind. Maximum 2% Risk-of-Ruin floor.
        
        Returns True if setup passes all filters.
        """
        if len(data) < MIN_DATA_POINTS:
            return False
        
        # Get recent 3 weeks of tape action
        recent_data = data.tail(RECENT_LOOKBACK)
        
        # Filter 1: Trend Filter - Price above 20-day SMA
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        if data['Close'].iloc[-1] < data['SMA_20'].iloc[-1]:
            return False
        
        # Filter 2: Volume Contraction (VCP)
        # Is volume drying up as price moves sideways?
        avg_vol = recent_data['Volume'].mean()
        recent_vol = recent_data['Volume'].iloc[-RECENT_VOLUME_WINDOW:].mean()
        volume_drying_up = recent_vol < (avg_vol * VOLUME_CONTRACTION_THRESHOLD)
        
        if not volume_drying_up:
            return False
        
        # Filter 3: Squat Bar Detection (Hidden Selling)
        # Abort if institutions are secretly offloading
        last_bar = data.iloc[-1]
        if MarketScanner.detect_squat_bar(last_bar, avg_vol):
            return False
        
        # Filter 4: Price Tightness (VPA - Volatile Price Action containment)
        # Max 5% variance in last 5 days
        recent_5d = recent_data.iloc[-5:]
        recent_high = recent_5d['High'].max()
        recent_low = recent_5d['Low'].min()
        
        if recent_low == 0:
            return False
        
        price_tight = (recent_high - recent_low) / recent_low < PRICE_TIGHTNESS_THRESHOLD
        
        return price_tight
    
    def scan_batch(self, tickers_batch: List[str]) -> List[str]:
        """
        Downloads and analyzes a batch of tickers.
        Returns list of tickers that pass all filters.
        """
        valid = []
        try:
            logger.info(f"📊 Downloading {len(tickers_batch)} tickers...")
            data_batch = yf.download(
                tickers_batch,
                period=LOOKBACK_PERIOD,
                group_by="ticker",
                threads=True,
                show_errors=False,
                progress=False
            )
            
            for ticker in tickers_batch:
                try:
                    ticker_data = data_batch[ticker].dropna()
                    if self.analyze_vcp_and_vpa(ticker, ticker_data):
                        valid.append(ticker)
                except Exception as e:
                    # Skip missing or delisted tickers silently
                    pass
        except Exception as e:
            logger.warning(f"⚠️ Batch download failed: {e}")
        
        return valid
    
    def run_scan(self):
        """Executes the full Ghost Protocol scan."""
        logger.info("\n🙏 GOD FIRST. FATHERHOOD AUDIT ACTIVE.")
        logger.info("🛡️ Protecting time for Rachel, CJ, Reah, and Ciaro.")
        logger.info("⚡ Initiating Ghost Protocol Omni-Scan...\n")
        
        # Fetch all tickers
        self.tickers = self.get_broad_market_tickers()
        if not self.tickers:
            logger.error("Failed to fetch tickers. Aborting scan.")
            return
        
        # Process in batches to prevent timeout/IP bans
        logger.info(f"📊 Scanning {len(self.tickers)} tickers for Institutional Accumulation...\n")
        
        for i in range(0, len(self.tickers), BATCH_SIZE):
            batch = self.tickers[i:i + BATCH_SIZE]
            batch_results = self.scan_batch(batch)
            self.valid_setups.extend(batch_results)
            
            # Progress indicator
            progress = min(i + BATCH_SIZE, len(self.tickers))
            logger.info(f"Progress: {progress}/{len(self.tickers)} tickers scanned | Found: {len(self.valid_setups)} setups")
        
        self.print_results()
    
    def print_results(self):
        """Formats and displays scan results."""
        print("\n" + "="*60)
        print("🎯 GHOST PROTOCOL COMPLETE.")
        print(f"📈 90% Conviction Setups Found: {len(self.valid_setups)}")
        
        if self.valid_setups:
            print(f"\n🔥 TICKERS ({len(self.valid_setups)}):")
            for i, ticker in enumerate(self.valid_setups, 1):
                print(f"  {i}. {ticker}")
        else:
            print("\n🛡️ No high-conviction setups found.")
            print("Action: Keep the capital in cash. Close the laptop. Go be a dad.")
        
        print("="*60 + "\n")


def main():
    """Entry point."""
    scanner = MarketScanner()
    scanner.run_scan()


if __name__ == "__main__":
    main()