"""
Validation script to check news quality for a ticker.

Fetches news for a ticker and prints statistics about relevance filtering.
"""
import asyncio
from datetime import date, timedelta
from ingest.alphavantage_news_client import fetch_ticker_news
from config.relevance_filter import is_article_relevant_to_ticker


async def validate_ticker_news(symbol: str, days_back: int = 7):
    """
    Fetch and validate news for a ticker.
    
    Args:
        symbol: Stock ticker symbol
        days_back: Number of days to look back
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"Fetching news for {symbol} from {start_date} to {end_date}...")
    print("=" * 80)
    
    try:
        articles = await fetch_ticker_news(symbol, start_date, end_date)
        
        total = len(articles)
        relevant = sum(1 for a in articles if a.get("is_relevant", False))
        irrelevant = total - relevant
        
        print(f"\nTotal articles fetched: {total}")
        print(f"Relevant articles: {relevant} ({100*relevant/total:.1f}%)" if total > 0 else "Relevant articles: 0")
        print(f"Irrelevant articles: {irrelevant} ({100*irrelevant/total:.1f}%)" if total > 0 else "Irrelevant articles: 0")
        
        if relevant > 0:
            print("\n" + "=" * 80)
            print("Sample RELEVANT articles:")
            print("=" * 80)
            relevant_samples = [a for a in articles if a.get("is_relevant", False)][:5]
            for i, article in enumerate(relevant_samples, 1):
                print(f"\n{i}. {article['headline']}")
                print(f"   Source: {article['source']}")
                print(f"   Date: {article['published_at']}")
        
        if irrelevant > 0:
            print("\n" + "=" * 80)
            print("Sample IRRELEVANT articles (filtered out):")
            print("=" * 80)
            irrelevant_samples = [a for a in articles if not a.get("is_relevant", True)][:5]
            for i, article in enumerate(irrelevant_samples, 1):
                print(f"\n{i}. {article['headline']}")
                print(f"   Source: {article['source']}")
                print(f"   Date: {article['published_at']}")
        
        print("\n" + "=" * 80)
        print("Validation complete!")
        
        if total == 0:
            print("⚠️  No articles found. This could be due to:")
            print("   - NewsAPI rate limits")
            print("   - No news in the date range")
            print("   - Ticker not in configuration")
        elif relevant / total < 0.3:
            print("⚠️  Low relevance rate. Consider:")
            print("   - Reviewing ticker search terms in config/news_queries.py")
            print("   - Adjusting noise phrase filters in config/relevance_filter.py")
        else:
            print("✅ Relevance filtering appears to be working well!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    days_back = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    
    asyncio.run(validate_ticker_news(symbol, days_back))

