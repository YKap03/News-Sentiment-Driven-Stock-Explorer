"""
Data refresh service: checks DB cache and fetches from APIs if needed.
"""
from datetime import date, timedelta
from typing import Optional
from db import crud_supabase
from ingest import alphavantage_news_client, openai_sentiment, yfinance_client


def ensure_price_data(
    ticker_symbol: str,
    start_date: date,
    end_date: date,
    max_staleness_days: int = 1
) -> None:
    """
    Ensure price data exists in DB for the given range.
    If missing or stale, fetch from Yahoo Finance and cache.
    
    Args:
        ticker_symbol: Stock symbol
        start_date: Start date
        end_date: End date
        max_staleness_days: Consider data stale if last date is older than this
    """
    # Cap dates to today - yfinance can't fetch future data
    today = date.today()
    if end_date > today:
        print(f"[INFO] Capping end_date from {end_date} to {today} (cannot fetch future data)")
        end_date = today
    if start_date > today:
        print(f"[INFO] Capping start_date from {start_date} to {today - timedelta(days=365)} (cannot fetch future data)")
        start_date = today - timedelta(days=365)
    
    # Ensure valid date range
    if start_date >= end_date:
        start_date = end_date - timedelta(days=365)
    
    # Check what we have
    latest_date = crud_supabase.get_latest_price_date(ticker_symbol)
    
    # Determine what we need to fetch
    fetch_start = start_date
    fetch_end = end_date
    
    if latest_date:
        # If we have recent data, only fetch missing ranges
        if latest_date >= end_date - timedelta(days=max_staleness_days):
            # We have recent data, check for gaps
            existing_prices = crud_supabase.get_prices(ticker_symbol, start_date, end_date)
            existing_dates = {date.fromisoformat(p["date"]) for p in existing_prices}
            
            # Find missing dates
            current = start_date
            missing_ranges = []
            range_start = None
            
            while current <= end_date:
                if current not in existing_dates:
                    if range_start is None:
                        range_start = current
                else:
                    if range_start is not None:
                        missing_ranges.append((range_start, current - timedelta(days=1)))
                        range_start = None
                current += timedelta(days=1)
            
            if range_start is not None:
                missing_ranges.append((range_start, end_date))
            
            # Fetch missing ranges
            for ms, me in missing_ranges:
                prices = yfinance_client.fetch_price_data(ticker_symbol, ms, me)
                if prices:
                    crud_supabase.upsert_prices(prices)
            return
        else:
            # Data is stale, fetch from latest_date to end_date
            fetch_start = latest_date + timedelta(days=1)
    
    # Fetch the needed range
    prices = yfinance_client.fetch_price_data(ticker_symbol, fetch_start, fetch_end)
    if prices:
        crud_supabase.upsert_prices(prices)


def ensure_news_data(
    ticker_symbol: str,
    start_date: date,
    end_date: date,
    company_name: Optional[str] = None,
    max_days_to_fetch: int = 2,
    only_recent_if_missing: bool = True
) -> int:
    """
    Ensure news articles exist in DB for the given range.
    
    IMPORTANT: This function is CONSERVATIVE to avoid wasting API requests:
    - Only fetches if data is missing AND the date range is very recent (last N days)
    - For older date ranges, returns 0 and relies on existing DB data
    
    This function should NOT be used for large backfills. Use the dedicated
    backfill script instead: backend/scripts/backfill_news.py
    
    Args:
        ticker_symbol: Stock symbol
        start_date: Start date
        end_date: End date
        company_name: Optional company name for search
        max_days_to_fetch: Maximum days back to fetch (default: 2 days)
        only_recent_if_missing: If True, only fetch if end_date is within max_days_to_fetch of today
        
    Returns:
        Number of new articles added (0 if no fetch was performed)
    """
    # Check existing articles
    existing_articles = crud_supabase.get_articles(ticker_symbol, start_date, end_date, relevant_only=True)
    
    # If we have articles, don't fetch (conservative approach)
    if len(existing_articles) > 0:
        return 0
    
    # Only fetch if the date range is very recent (to avoid wasting API calls)
    today = date.today()
    days_since_end = (today - end_date).days
    
    if only_recent_if_missing and days_since_end > max_days_to_fetch:
        # Date range is too old - don't fetch, rely on existing data
        return 0
    
    # Limit the fetch to recent dates only
    if days_since_end > max_days_to_fetch:
        # Adjust start_date to only fetch recent data
        fetch_start = today - timedelta(days=max_days_to_fetch)
        if fetch_start > end_date:
            # Requested range is too old, don't fetch
            return 0
        start_date = max(start_date, fetch_start)
    
    # Only fetch a small recent window
    fetch_end = min(end_date, today)
    fetch_start = fetch_end - timedelta(days=max_days_to_fetch)
    
    if fetch_start > fetch_end:
        return 0
    
    # Now fetch only this small window
    import asyncio
    try:
        articles = asyncio.run(alphavantage_news_client.fetch_ticker_news(ticker_symbol, fetch_start, fetch_end, company_name))
        
        if articles:
            crud_supabase.upsert_articles(articles)
            return len(articles)
    except Exception as e:
        # Silently fail - don't break the API if Alpha Vantage is unavailable
        print(f"Warning: Could not fetch news for {ticker_symbol}: {e}")
        return 0
    
    return 0


def enrich_sentiment_for_new_articles(
    batch_size: int = 50
) -> int:
    """
    Find articles without sentiment and enrich them using OpenAI.
    Returns number of articles enriched.
    
    Args:
        batch_size: Number of articles to process at once
        
    Returns:
        Number of articles enriched
    """
    articles_needing_sentiment = crud_supabase.get_articles_needing_sentiment(limit=batch_size)
    
    if not articles_needing_sentiment:
        return 0
    
    # Prepare articles for sentiment analysis
    article_dicts = [
        {
            "headline": a["headline"],
            "raw_text": a.get("raw_text") or ""
        }
        for a in articles_needing_sentiment
    ]
    
    # Analyze sentiment
    import asyncio
    sentiment_results = asyncio.run(openai_sentiment.analyze_sentiment_batch(article_dicts))
    
    # Update articles
    enriched_count = 0
    for article, (score, label) in zip(articles_needing_sentiment, sentiment_results):
        crud_supabase.update_article_sentiment(article["id"], score, label)
        enriched_count += 1
    
    return enriched_count
