"""
CRUD operations using Supabase client.
"""
from supabase import Client
from datetime import date, datetime
from typing import List, Optional, Dict
from db.supabase_client import get_supabase


# Ticker operations
def get_tickers() -> List[Dict]:
    """Get all tickers."""
    supabase = get_supabase()
    response = supabase.table("tickers").select("*").order("symbol", desc=False).execute()
    return response.data if response.data else []


def get_ticker_by_symbol(symbol: str) -> Optional[Dict]:
    """Get ticker by symbol."""
    supabase = get_supabase()
    response = supabase.table("tickers").select("*").eq("symbol", symbol).execute()
    return response.data[0] if response.data else None


def create_ticker(symbol: str, name: Optional[str] = None) -> Dict:
    """Create a new ticker."""
    supabase = get_supabase()
    data = {"symbol": symbol}
    if name:
        data["name"] = name
    response = supabase.table("tickers").insert(data).execute()
    return response.data[0] if response.data else {}


# DailyPrice operations
def get_prices(
    ticker_symbol: str,
    start_date: date,
    end_date: date
) -> List[Dict]:
    """Get price data for a ticker in date range."""
    supabase = get_supabase()
    response = (
        supabase.table("daily_prices")
        .select("*")
        .eq("ticker_symbol", ticker_symbol)
        .gte("date", start_date.isoformat())
        .lte("date", end_date.isoformat())
        .order("date")
        .execute()
    )
    return response.data if response.data else []


def get_latest_price_date(ticker_symbol: str) -> Optional[date]:
    """Get the latest date for which we have price data."""
    supabase = get_supabase()
    response = (
        supabase.table("daily_prices")
        .select("date")
        .eq("ticker_symbol", ticker_symbol)
        .order("date", desc=True)
        .limit(1)
        .execute()
    )
    if response.data:
        return datetime.fromisoformat(response.data[0]["date"]).date()
    return None


def upsert_prices(prices: List[Dict]) -> None:
    """Upsert price data (insert or update)."""
    supabase = get_supabase()
    # Convert date objects to strings and ensure numeric types
    processed_prices = []
    for price in prices:
        processed = {
            "ticker_symbol": price["ticker_symbol"],
            "date": price["date"].isoformat() if isinstance(price.get("date"), date) else price["date"],
            "open": float(price["open"]),
            "high": float(price["high"]),
            "low": float(price["low"]),
            "close": float(price["close"]),
            "volume": int(price["volume"])
        }
        processed_prices.append(processed)
    
    # Upsert in batches
    batch_size = 100
    for i in range(0, len(processed_prices), batch_size):
        batch = processed_prices[i:i + batch_size]
        try:
            supabase.table("daily_prices").upsert(batch, on_conflict="ticker_symbol,date").execute()
        except Exception as e:
            print(f"    Warning: Error upserting batch {i//batch_size + 1}: {e}")
            # Try inserting one by one if batch fails
            for price in batch:
                try:
                    supabase.table("daily_prices").upsert(price, on_conflict="ticker_symbol,date").execute()
                except Exception as e2:
                    print(f"    Warning: Failed to insert price for {price.get('ticker_symbol')} on {price.get('date')}: {e2}")


# NewsArticle operations
def get_articles(
    ticker_symbol: str,
    start_date: date,
    end_date: date,
    relevant_only: bool = True
) -> List[Dict]:
    """
    Get news articles for a ticker in date range.
    
    Args:
        ticker_symbol: Stock ticker symbol
        start_date: Start date
        end_date: End date
        relevant_only: If True, only return articles where is_relevant = true
        
    Returns:
        List of article dictionaries
    """
    supabase = get_supabase()
    start_datetime = datetime.combine(start_date, datetime.min.time()).isoformat()
    end_datetime = datetime.combine(end_date, datetime.max.time()).isoformat()
    
    query = (
        supabase.table("news_articles")
        .select("*")
        .eq("ticker_symbol", ticker_symbol)
        .gte("published_at", start_datetime)
        .lte("published_at", end_datetime)
    )
    
    # Filter by relevance if requested
    if relevant_only:
        query = query.eq("is_relevant", True)
    
    response = query.order("published_at", desc=True).execute()
    return response.data if response.data else []


def get_articles_needing_sentiment(limit: int = 50, relevant_only: bool = True) -> List[Dict]:
    """
    Get articles that need sentiment analysis.
    
    Args:
        limit: Maximum number of articles to return
        relevant_only: If True, only return relevant articles
        
    Returns:
        List of article dictionaries
    """
    supabase = get_supabase()
    query = (
        supabase.table("news_articles")
        .select("*")
        .is_("sentiment_score", "null")
    )
    
    # Only process relevant articles for sentiment
    if relevant_only:
        query = query.eq("is_relevant", True)
    
    response = query.order("published_at").limit(limit).execute()
    return response.data if response.data else []


def upsert_articles(articles: List[Dict]) -> None:
    """Upsert news articles."""
    supabase = get_supabase()
    # Convert datetime objects to strings
    processed_articles = []
    for article in articles:
        processed = {
            "ticker_symbol": article["ticker_symbol"],
            "published_at": article["published_at"].isoformat() if isinstance(article.get("published_at"), datetime) else article["published_at"],
            "headline": article["headline"],
            "source": article["source"],
            "url": article.get("url"),
            "raw_text": article.get("raw_text"),
            # Don't overwrite existing sentiment
            "sentiment_score": article.get("sentiment_score"),
            "sentiment_label": article.get("sentiment_label"),
            # Include is_relevant flag (default to True if not provided)
            "is_relevant": article.get("is_relevant", True),
            # Include relevance_score (0.0 to 1.0)
            "relevance_score": article.get("relevance_score")
        }
        processed_articles.append(processed)
    
    # Upsert in batches
    batch_size = 50  # Smaller batches for articles
    for i in range(0, len(processed_articles), batch_size):
        batch = processed_articles[i:i + batch_size]
        try:
            # Insert and ignore duplicates (Supabase will handle this)
            supabase.table("news_articles").upsert(batch).execute()
        except Exception as e:
            print(f"    Warning: Error upserting article batch {i//batch_size + 1}: {e}")
            # Try inserting one by one if batch fails
            for article in batch:
                try:
                    supabase.table("news_articles").upsert(article).execute()
                except Exception as e2:
                    print(f"    Warning: Failed to insert article: {article.get('headline', 'Unknown')[:50]}...")


def update_article_sentiment(
    article_id: int,
    sentiment_score: float,
    sentiment_label: str
) -> None:
    """Update sentiment for a specific article."""
    supabase = get_supabase()
    supabase.table("news_articles").update({
        "sentiment_score": sentiment_score,
        "sentiment_label": sentiment_label
    }).eq("id", article_id).execute()


# DailyFeature operations (for ML)
def upsert_features(features: List[Dict]) -> None:
    """Upsert daily features."""
    supabase = get_supabase()
    # Convert date objects to strings
    for feature in features:
        if isinstance(feature.get("date"), date):
            feature["date"] = feature["date"].isoformat()
    
    # Upsert in batches
    batch_size = 100
    for i in range(0, len(features), batch_size):
        batch = features[i:i + batch_size]
        supabase.table("daily_features").upsert(batch, on_conflict="ticker_symbol,date").execute()


# Sync versions for training script (same functions, just different naming)
get_prices_sync = get_prices
get_articles_sync = get_articles

