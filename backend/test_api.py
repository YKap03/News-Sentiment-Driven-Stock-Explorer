"""
Quick test script to verify API endpoints work for all tickers.
"""
import requests
from datetime import date

BASE_URL = "http://localhost:8000"

def test_ticker(ticker: str):
    """Test API endpoint for a ticker."""
    url = f"{BASE_URL}/api/summary"
    # Don't pass start_date/end_date - will default to last 30 days
    params = {
        "ticker": ticker
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {ticker}: {len(data.get('price_series', []))} prices, {len(data.get('sentiment_series', []))} sentiment points, {data.get('n_articles', 0)} articles")
            return True
        else:
            print(f"❌ {ticker}: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ {ticker}: Error - {e}")
        return False

if __name__ == "__main__":
    print("Testing API endpoints for all tickers...")
    print("=" * 60)
    
    tickers = ["AAPL", "AMZN", "GOOGL", "JNJ", "JPM", "META", "MSFT", "NVDA", "TSLA", "V"]
    
    results = []
    for ticker in tickers:
        results.append(test_ticker(ticker))
    
    print("=" * 60)
    print(f"Results: {sum(results)}/{len(tickers)} tickers working")
    
    if not all(results):
        print("\n⚠️  Some tickers failed. Check backend logs for errors.")

