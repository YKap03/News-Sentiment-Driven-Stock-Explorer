"""
Safe news backfill script for repopulating news_articles with ticker-relevant news.

This script:
- Supports dry-run mode (zero API calls) to preview what would be fetched
- Only fetches ticker-focused, relevance-filtered news
- Respects Alpha Vantage rate limits with throttling
- Deduplicates requests by checking existing data
- Never runs automatically - must be explicitly invoked

IMPORTANT: Alpha Vantage only returns recent articles (last few days/weeks).
           Use recent date ranges (last 30 days) for best results.

Usage:
    # Dry-run (preview without making API calls) - last 30 days:
    python -m backend.scripts.backfill_news --tickers AAPL,MSFT,TSLA --start-date 2025-11-01 --end-date 2025-11-30 --dry-run
    
    # Actual backfill (after reviewing dry-run output) - last 30 days:
    python -m backend.scripts.backfill_news --tickers AAPL,MSFT,TSLA --start-date 2025-11-01 --end-date 2025-11-30 --no-dry-run
"""
import sys
import argparse
import asyncio
from datetime import date, timedelta
from typing import List, Set
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir.parent))

from db import crud_supabase
from ingest import alphavantage_news_client
from config.news_queries import get_ticker_config, get_tracked_tickers


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    return date.fromisoformat(date_str)


def get_existing_article_dates(ticker_symbol: str, start_date: date, end_date: date) -> Set[date]:
    """
    Get set of dates that already have articles in the database.
    
    Returns:
        Set of date objects for which articles exist
    """
    existing_articles = crud_supabase.get_articles(ticker_symbol, start_date, end_date, relevant_only=False)
    
    dates = set()
    for article in existing_articles:
        pub_date_str = article.get("published_at")
        if isinstance(pub_date_str, str):
            # Extract date part
            date_part = pub_date_str.split("T")[0].split(" ")[0]
            try:
                dates.add(date.fromisoformat(date_part))
            except:
                pass
        elif isinstance(pub_date_str, date):
            dates.add(pub_date_str)
    
    return dates


def check_data_coverage(
    ticker_symbol: str,
    start_date: date,
    end_date: date
) -> dict:
    """
    Check how much data we already have for a ticker in the date range.
    
    Returns:
        Dictionary with:
        - 'has_data': bool - Whether we have any articles
        - 'coverage_pct': float - Percentage of date range covered (0-100)
        - 'total_days': int - Total days in range
        - 'days_with_data': int - Days that have articles
    """
    existing_dates = get_existing_article_dates(ticker_symbol, start_date, end_date)
    
    total_days = (end_date - start_date).days + 1
    days_with_data = len(existing_dates)
    coverage_pct = (days_with_data / total_days * 100) if total_days > 0 else 0
    
    return {
        'has_data': days_with_data > 0,
        'coverage_pct': coverage_pct,
        'total_days': total_days,
        'days_with_data': days_with_data
    }


def find_missing_date_ranges(
    ticker_symbol: str,
    start_date: date,
    end_date: date,
    chunk_days: int = 7
) -> List[tuple]:
    """
    Find date ranges that need to be fetched (for incremental backfills).
    
    Only use this when we have partial data and want to fill gaps.
    For fresh backfills, use the full date range instead.
    
    Args:
        ticker_symbol: Stock symbol
        start_date: Start date
        end_date: End date
        chunk_days: Size of date chunks to check (default: 7 days)
        
    Returns:
        List of (chunk_start, chunk_end) tuples for missing ranges
    """
    existing_dates = get_existing_article_dates(ticker_symbol, start_date, end_date)
    
    missing_ranges = []
    current = start_date
    
    while current <= end_date:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end_date)
        
        # Check if this chunk has any articles
        chunk_dates = {
            current + timedelta(days=i)
            for i in range((chunk_end - current).days + 1)
        }
        
        # If less than 50% of dates have articles, consider it missing
        dates_with_articles = chunk_dates & existing_dates
        coverage = len(dates_with_articles) / len(chunk_dates) if chunk_dates else 0
        
        if coverage < 0.5:  # Less than 50% coverage
            missing_ranges.append((current, chunk_end))
        
        current = chunk_end + timedelta(days=1)
    
    return missing_ranges


async def backfill_ticker(
    ticker_symbol: str,
    start_date: date,
    end_date: date,
    dry_run: bool = True,
    force_full_range: bool = False
) -> dict:
    """
    Backfill news for a single ticker.
    
    Args:
        ticker_symbol: Stock symbol
        start_date: Start date
        end_date: End date
        dry_run: If True, don't make API calls, just return plan
        
    Returns:
        Dictionary with stats: {
            'api_calls': int,
            'articles_fetched': int,
            'articles_relevant': int,
            'articles_inserted': int
        }
    """
    print(f"\n{'='*80}")
    print(f"Processing {ticker_symbol}")
    print(f"{'='*80}")
    
    # Get ticker config
    try:
        config = get_ticker_config(ticker_symbol)
        company_name = config["company_name"]
    except KeyError:
        print(f"  [WARN] Ticker {ticker_symbol} not in config")
        company_name = None
    
    print(f"  Company: {company_name or 'N/A'}")
    print(f"  Date range: {start_date} to {end_date}")
    print(f"  [NOTE] Using Alpha Vantage NEWS_SENTIMENT API")
    print(f"  [NOTE] Rate limiting: 1 minute wait between calls (stays under 5 calls/min limit)")
    
    # Check existing data coverage
    coverage = check_data_coverage(ticker_symbol, start_date, end_date)
    print(f"  Existing data: {coverage['days_with_data']}/{coverage['total_days']} days ({coverage['coverage_pct']:.1f}% coverage)")
    
    # Strategy decision:
    # - If < 75% coverage OR force_full_range: Fetch full year in one query (more efficient)
    #   Reason: If more than 25% of data is missing, it's faster to fetch everything
    #   and let database deduplication handle it, rather than making many small queries
    # - If >= 75% coverage: Use chunking to fill gaps only (avoid re-fetching)
    #   Reason: When most data exists (>75%), only fetch missing chunks to save API calls
    use_full_range = force_full_range or coverage['coverage_pct'] < 75.0
    
    if use_full_range:
        # Fresh backfill: Fetch entire date range in one query (Alpha Vantage returns up to 1000 articles)
        if force_full_range:
            print(f"  [STRATEGY] Force full-range mode - Fetching full range in one query")
        else:
            print(f"  [STRATEGY] Low coverage ({coverage['coverage_pct']:.1f}%) - Fetching full range in one query")
        print(f"  [NOTE] Alpha Vantage returns up to 1000 articles per request")
        print(f"  [NOTE] Articles will be filtered by date range in code")
        print(f"  [NOTE] Database will deduplicate any existing articles automatically")
        
        # Alpha Vantage: One API call per ticker (returns up to 1000 articles)
        estimated_calls = "1 (Alpha Vantage returns up to 1000 articles per request)"
        
        if dry_run:
            print(f"  [DRY-RUN] Would fetch full range {start_date} to {end_date} in one query")
            print(f"  [DRY-RUN] Estimated API calls: {estimated_calls}")
            return {
                'api_calls': 1,  # Conservative estimate for dry-run
                'articles_fetched': 0,
                'articles_relevant': 0,
                'articles_inserted': 0
            }
        
        # Fetch full range
        print(f"  [FETCHING] Fetching full range {start_date} to {end_date}...")
        
        # Initialize variables
        total_fetched = 0
        total_relevant = 0
        total_inserted = 0
        estimated_api_calls = 0
        
        try:
            articles = await alphavantage_news_client.fetch_ticker_news(
                ticker_symbol,
                start_date,
                end_date,
                company_name
            )
            
            total_fetched = len(articles)
            relevant_articles = [a for a in articles if a.get("is_relevant", False)]
            total_relevant = len(relevant_articles)
            
            # Insert into DB
            if articles:
                crud_supabase.upsert_articles(articles)
                total_inserted = len(articles)
            
            # Alpha Vantage: One API call per ticker (returns up to 1000 articles)
            estimated_api_calls = 1
            
            if total_fetched == 0:
                print(f"  [WARN] No articles fetched for date range {start_date} to {end_date}")
                print(f"    [IMPORTANT] Alpha Vantage NEWS_SENTIMENT only returns RECENT articles (last few days)")
                print(f"    [IMPORTANT] It does NOT support historical date ranges")
                print(f"    [SOLUTION] Use a recent date range (e.g., last 30 days) instead")
                print(f"    [SOLUTION] See backend/ALPHAVANTAGE_LIMITATION.md for details")
            else:
                print(f"  [DONE] Fetched {total_fetched} articles ({total_relevant} relevant)")
                print(f"  [NOTE] Made 1 API call to Alpha Vantage")
                print(f"  [NOTE] Articles filtered to date range {start_date} to {end_date}")
            
            return {
                'api_calls': estimated_api_calls,
                'articles_fetched': total_fetched,
                'articles_relevant': total_relevant,
                'articles_inserted': total_inserted
            }
            
        except Exception as e:
            print(f"  [ERROR] Failed to fetch: {e}")
            print(f"  [NOTE] Check that ALPHAVANTAGE_API_KEY is set in .env")
            print(f"  [NOTE] Alpha Vantage free tier: 5 calls/minute, 500 calls/day")
            return {
                'api_calls': estimated_api_calls,
                'articles_fetched': total_fetched,
                'articles_relevant': total_relevant,
                'articles_inserted': total_inserted
            }
    
    else:
        # Incremental backfill: Only fetch missing chunks
        print(f"  [STRATEGY] Good coverage ({coverage['coverage_pct']:.1f}%) - Filling gaps only")
        
        missing_ranges = find_missing_date_ranges(ticker_symbol, start_date, end_date)
        
        if not missing_ranges:
            print(f"  [INFO] All date ranges already have articles, skipping")
            return {
                'api_calls': 0,
                'articles_fetched': 0,
                'articles_relevant': 0,
                'articles_inserted': 0
            }
        
        print(f"  Missing date ranges: {len(missing_ranges)} chunks")
        for i, (chunk_start, chunk_end) in enumerate(missing_ranges[:5], 1):
            print(f"    {i}. {chunk_start} to {chunk_end}")
        if len(missing_ranges) > 5:
            print(f"    ... and {len(missing_ranges) - 5} more")
        
        estimated_calls = len(missing_ranges)
        print(f"  Estimated API calls: {estimated_calls}")
        
        if dry_run:
            print(f"  [DRY-RUN] Would fetch {estimated_calls} missing chunks")
            return {
                'api_calls': estimated_calls,
                'articles_fetched': 0,
                'articles_relevant': 0,
                'articles_inserted': 0
            }
        
        # Fetch missing chunks
        print(f"  [FETCHING] Fetching {len(missing_ranges)} missing chunks...")
        total_fetched = 0
        total_relevant = 0
        total_inserted = 0
        api_calls = 0
        
        for chunk_start, chunk_end in missing_ranges:
            try:
                print(f"    Fetching {chunk_start} to {chunk_end}...", end=" ", flush=True)
                
                articles = await alphavantage_news_client.fetch_ticker_news(
                    ticker_symbol,
                    chunk_start,
                    chunk_end,
                    company_name
                )
                
                api_calls += 1
                total_fetched += len(articles)
                
                # Count relevant articles
                relevant_articles = [a for a in articles if a.get("is_relevant", False)]
                total_relevant += len(relevant_articles)
                
                # Insert into DB
                if articles:
                    crud_supabase.upsert_articles(articles)
                    total_inserted += len(articles)
                
                print(f"✓ ({len(articles)} articles, {len(relevant_articles)} relevant)")
                
            except Exception as e:
                print(f"✗ Error: {e}")
                continue
        
        print(f"  [DONE] Fetched {total_fetched} articles ({total_relevant} relevant), {api_calls} API calls")
    
    return {
        'api_calls': api_calls,
        'articles_fetched': total_fetched,
        'articles_relevant': total_relevant,
        'articles_inserted': total_inserted
    }


async def main():
    """Main backfill function."""
    parser = argparse.ArgumentParser(
        description="Backfill ticker-relevant news articles from Alpha Vantage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (preview) - last 30 days:
  python -m scripts.backfill_news --tickers AAPL,MSFT --start-date 2025-11-01 --end-date 2025-11-30 --dry-run
  
  # Actual backfill - last 30 days (uses smart strategy based on coverage):
  python -m scripts.backfill_news --tickers AAPL,MSFT --start-date 2025-11-01 --end-date 2025-11-30 --no-dry-run
  
  # Force full-range query (one query for entire range, more efficient for repopulation):
  python -m scripts.backfill_news --tickers AAPL --start-date 2025-11-01 --end-date 2025-11-30 --force-full-range --no-dry-run
  
  Note: Alpha Vantage only returns recent articles (last few days/weeks).
        Use recent date ranges (last 30 days) for best results.
        """
    )
    
    parser.add_argument(
        '--tickers',
        type=str,
        required=True,
        help='Comma-separated list of ticker symbols (e.g., AAPL,MSFT,TSLA)'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        required=True,
        help='Start date in YYYY-MM-DD format'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        required=True,
        help='End date in YYYY-MM-DD format'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Dry-run mode: preview without making API calls (default: True)'
    )
    parser.add_argument(
        '--no-dry-run',
        dest='dry_run',
        action='store_false',
        help='Disable dry-run mode and actually fetch data'
    )
    parser.add_argument(
        '--force-full-range',
        action='store_true',
        help='Force full-range query (one query for entire date range) instead of chunking. '
             'Useful when you want to repopulate even if some data exists.'
    )
    
    args = parser.parse_args()
    
    # Parse tickers
    tickers = [t.strip().upper() for t in args.tickers.split(',')]
    
    # Validate tickers
    tracked_tickers = get_tracked_tickers()
    invalid_tickers = [t for t in tickers if t not in tracked_tickers]
    if invalid_tickers:
        print(f"[WARN] Tickers not in config: {invalid_tickers}")
        print(f"Available tickers: {', '.join(tracked_tickers)}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Parse dates
    try:
        start_date = parse_date(args.start_date)
        end_date = parse_date(args.end_date)
    except ValueError as e:
        print(f"[ERROR] Invalid date format: {e}")
        print("Dates must be in YYYY-MM-DD format")
        return
    
    if start_date > end_date:
        print("[ERROR] Start date must be before end date")
        return
    
    # Check API key
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key and not args.dry_run:
        print("[ERROR] ALPHAVANTAGE_API_KEY not set in environment")
        print("Set it in .env file before running actual backfill")
        print("Get your free API key at: https://www.alphavantage.co/support/#api-key")
        return
    
    # Print summary
    print("=" * 80)
    print("News Backfill Script")
    print("=" * 80)
    print(f"Mode: {'DRY-RUN (no API calls)' if args.dry_run else 'LIVE (will make API calls)'}")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Days: {(end_date - start_date).days + 1}")
    
    if args.dry_run:
        print("\n[DRY-RUN MODE] No API calls will be made. Review the plan below.")
    else:
        print("\n[LIVE MODE] Will make actual API calls to Alpha Vantage.")
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    # Process each ticker
    total_stats = {
        'api_calls': 0,
        'articles_fetched': 0,
        'articles_relevant': 0,
        'articles_inserted': 0
    }
    
    for ticker in tickers:
        stats = await backfill_ticker(
            ticker, 
            start_date, 
            end_date, 
            dry_run=args.dry_run,
            force_full_range=args.force_full_range
        )
        for key in total_stats:
            total_stats[key] += stats[key]
    
    # Print summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total API calls: {total_stats['api_calls']}")
    if not args.dry_run:
        print(f"Total articles fetched: {total_stats['articles_fetched']}")
        print(f"Total relevant articles: {total_stats['articles_relevant']}")
        print(f"Total articles inserted: {total_stats['articles_inserted']}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

