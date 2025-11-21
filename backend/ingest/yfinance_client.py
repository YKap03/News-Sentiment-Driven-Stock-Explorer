"""
Yahoo Finance client for fetching stock price data.
No API key required - completely free!
"""
import yfinance as yf
import pandas as pd
from datetime import date, datetime, timedelta
from typing import List, Dict
import warnings
import time

# Suppress yfinance warnings
warnings.filterwarnings('ignore')


def fetch_price_data(
    symbol: str,
    start_date: date,
    end_date: date
) -> List[Dict]:
    """
    Fetch daily price data from Yahoo Finance for a symbol and date range.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        start_date: Start date
        end_date: End date
        
    Returns:
        List of price dictionaries with keys: ticker_symbol, date, open, high, low, close, volume
    """
    try:
        # Get system date - use actual system date, don't assume 2025 is wrong
        system_today = date.today()
        today = system_today
        
        # Only adjust dates if they're actually in the future (more than 1 day ahead)
        # This allows same-day and next-day requests, and allows 2025 dates if system is in 2025
        if start_date > today:
            days_ahead = (start_date - today).days
            if days_ahead > 1:
                # More than 1 day in the future - adjust to last 30 days
                print(f"[WARN] Start date {start_date} is {days_ahead} days in the future, adjusting to {today - timedelta(days=30)}")
                start_date = today - timedelta(days=30)
            # If 0-1 days ahead, allow it (might be same day or next day)
        
        if end_date > today:
            days_ahead = (end_date - today).days
            if days_ahead > 0:
                # Any future date - cap at today
                print(f"[WARN] End date {end_date} is {days_ahead} days in the future, adjusting to {today}")
                end_date = today
        
        # Ensure we have a valid date range
        if start_date >= end_date:
            start_date = end_date - timedelta(days=365)
        
        # Download data using yfinance with retries
        max_retries = 3
        df = None
        
        for attempt in range(max_retries):
            try:
                # Convert dates to datetime for yfinance
                start_dt = datetime.combine(start_date, datetime.min.time())
                end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
                
                # Method 1: Try using yf.download() (sometimes more reliable)
                try:
                    df = yf.download(
                        symbol,
                        start=start_dt,
                        end=end_dt,
                        interval="1d",
                        progress=False,
                        show_errors=False
                    )
                    if df is not None and not df.empty:
                        # Filter to exact date range
                        df = df[(df.index.date >= start_date) & (df.index.date <= end_date)]
                        if not df.empty:
                            break
                except Exception:
                    pass
                
                # Method 2: Try using Ticker().history() with start/end
                if df is None or df.empty:
                    try:
                        ticker = yf.Ticker(symbol)
                        df = ticker.history(start=start_dt, end=end_dt, interval="1d", timeout=30)
                        if df is not None and not df.empty:
                            # Filter to exact date range
                            df = df[(df.index.date >= start_date) & (df.index.date <= end_date)]
                            if not df.empty:
                                break
                    except Exception:
                        pass
                
                # Method 3: Try using period
                if df is None or df.empty:
                    days_diff = (end_date - start_date).days
                    if days_diff <= 5:
                        period = "5d"
                    elif days_diff <= 30:
                        period = "1mo"
                    elif days_diff <= 90:
                        period = "3mo"
                    elif days_diff <= 180:
                        period = "6mo"
                    elif days_diff <= 365:
                        period = "1y"
                    else:
                        period = "2y"
                    
                    try:
                        ticker = yf.Ticker(symbol)
                        df = ticker.history(period=period, interval="1d", timeout=30)
                        if df is not None and not df.empty:
                            # Filter to exact date range
                            df = df[(df.index.date >= start_date) & (df.index.date <= end_date)]
                            if not df.empty:
                                break
                    except Exception:
                        pass
                
                # If still empty, wait and retry
                if df is None or df.empty:
                    if attempt < max_retries - 1:
                        time.sleep(3)  # Wait 3 seconds before retry
                        continue
                    else:
                        return []
                else:
                    break
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                else:
                    return []
        
        if df is None or df.empty:
            return []
        
        # Convert to list of dictionaries
        prices = []
        for idx, row in df.iterrows():
            try:
                # Get date from index (Timestamp)
                if isinstance(idx, pd.Timestamp):
                    price_date = idx.date()
                elif hasattr(idx, 'date'):
                    price_date = idx.date()
                elif hasattr(idx, 'to_pydatetime'):
                    price_date = idx.to_pydatetime().date()
                else:
                    # Try to convert to date
                    price_date = pd.to_datetime(idx).date()
                
                # Ensure date is within range
                if start_date <= price_date <= end_date:
                    prices.append({
                        "ticker_symbol": symbol,
                        "date": price_date,
                        "open": float(row["Open"]) if not pd.isna(row["Open"]) else 0.0,
                        "high": float(row["High"]) if not pd.isna(row["High"]) else 0.0,
                        "low": float(row["Low"]) if not pd.isna(row["Low"]) else 0.0,
                        "close": float(row["Close"]) if not pd.isna(row["Close"]) else 0.0,
                        "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
                    })
            except Exception:
                continue  # Skip this row if there's an error
        
        return prices
    except Exception as e:
        # Return empty list on any error
        return []

