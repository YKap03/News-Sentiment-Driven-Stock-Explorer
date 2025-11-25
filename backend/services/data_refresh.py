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
    
    # FIRST: Check if we already have all the data we need in the database
    existing_prices = crud_supabase.get_prices(ticker_symbol, start_date, end_date)
    existing_dates = set()
    for p in existing_prices:
        try:
            price_date = p["date"]
            if isinstance(price_date, str):
                price_date = date.fromisoformat(price_date)
            elif isinstance(price_date, date):
                pass
            else:
                continue
            existing_dates.add(price_date)
        except Exception:
            continue
    
    # Check if we have complete coverage
    # IMPORTANT: Only check for missing dates that are NOT in the future
    current = start_date
    missing_dates = []
    while current <= end_date:
        # Skip future dates - we can't fetch them from yfinance anyway
        if current <= today and current not in existing_dates:
            missing_dates.append(current)
        current += timedelta(days=1)
    
    # If we have all the data (or all missing dates are in the future), return early
    if not missing_dates:
        if end_date > today:
            print(f"[INFO] Price data for {ticker_symbol} exists in database for range {start_date} to {end_date}. "
                  f"End date is in the future ({end_date}), skipping yfinance fetch.")
        else:
            print(f"[INFO] Price data for {ticker_symbol} already exists in database for range {start_date} to {end_date}")
        return
    
    # We have some missing dates (all are <= today since we filtered above)
    # Group missing dates into ranges
    if missing_dates:
        missing_ranges = []
        range_start = missing_dates[0]
        range_end = missing_dates[0]
        
        for d in missing_dates[1:]:
            if d == range_end + timedelta(days=1):
                range_end = d
            else:
                # End current range and start new one
                if range_start <= today:  # Only fetch if not entirely in the future
                    fetch_end = min(range_end, today)
                    if fetch_end >= range_start:
                        missing_ranges.append((range_start, fetch_end))
                range_start = d
                range_end = d
        
        # Add final range
        if range_start <= today:
            fetch_end = min(range_end, today)
            if fetch_end >= range_start:
                missing_ranges.append((range_start, fetch_end))
        
        # Fetch missing ranges (only if not in the future)
        for ms, me in missing_ranges:
            if ms <= today and me <= today:
                prices = yfinance_client.fetch_price_data(ticker_symbol, ms, me)
                if prices:
                    crud_supabase.upsert_prices(prices)
    
    # Also check if we need to update stale data
    latest_date = crud_supabase.get_latest_price_date(ticker_symbol)
    if latest_date and latest_date < end_date - timedelta(days=max_staleness_days):
        # Data is stale, but only fetch if end_date is not in the future
        if end_date <= today:
            fetch_start = latest_date + timedelta(days=1)
            fetch_end = min(end_date, today)
            if fetch_start <= fetch_end:
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
