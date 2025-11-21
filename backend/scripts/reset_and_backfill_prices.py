"""
Reset daily_prices table and repopulate with stock price data for 10/21/2025 to 11/20/2025.

This script:
1. Clears ALL price data from daily_prices table
2. Fetches price data for 10/21/2025 to 11/20/2025 for all tickers using yfinance
3. Stores the fresh price data

WARNING: This will permanently delete all existing price data!
"""
import sys
import argparse
from pathlib import Path
from datetime import date, timedelta

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from db import crud_supabase
from db.supabase_client import get_supabase
from ingest.yfinance_client import fetch_price_data
from config.news_queries import get_tracked_tickers


def clear_all_prices(dry_run: bool = True) -> int:
    """
    Clear all price data from the daily_prices table.
    
    Args:
        dry_run: If True, only show what would be deleted
        
    Returns:
        Number of price records that would be/were deleted
    """
    supabase = get_supabase()
    
    # First, count price records
    response = supabase.table("daily_prices").select("id", count="exact").execute()
    total_count = response.count if hasattr(response, 'count') else 0
    
    # Get sample records to show
    sample_response = supabase.table("daily_prices").select("ticker_symbol, date, close").limit(5).order("date", desc=True).execute()
    sample_prices = sample_response.data if sample_response.data else []
    
    # Get date range
    date_range_response = supabase.table("daily_prices").select("date").order("date", desc=False).limit(1).execute()
    oldest_date = date_range_response.data[0]["date"] if date_range_response.data else "N/A"
    
    date_range_response = supabase.table("daily_prices").select("date").order("date", desc=True).limit(1).execute()
    newest_date = date_range_response.data[0]["date"] if date_range_response.data else "N/A"
    
    print("=" * 80)
    print("Clear All Price Data")
    print("=" * 80)
    print(f"Mode: {'DRY-RUN (no deletions)' if dry_run else 'LIVE (will delete all price data)'}")
    print(f"Total price records in database: {total_count}")
    print(f"Date range: {oldest_date} to {newest_date}")
    
    if sample_prices:
        print("\nSample price records:")
        for i, price in enumerate(sample_prices, 1):
            ticker = price.get("ticker_symbol", "N/A")
            price_date = price.get("date", "N/A")
            close_price = price.get("close", "N/A")
            print(f"  {i}. [{ticker}] {price_date}: ${close_price}")
    
    if total_count == 0:
        print("\n[INFO] Database is already empty. Nothing to delete.")
        return 0
    
    if not dry_run:
        print(f"\n[WARNING] This will DELETE ALL {total_count} price records from the database!")
        print("[WARNING] This action cannot be undone!")
        
        # Delete all price records
        print("\n[DELETING] All price records...")
        try:
            # Delete in batches to avoid timeouts
            batch_size = 1000
            deleted = 0
            
            while True:
                # Get a batch of IDs
                batch_response = supabase.table("daily_prices").select("id").limit(batch_size).execute()
                batch_ids = [row["id"] for row in batch_response.data] if batch_response.data else []
                
                if not batch_ids:
                    break
                
                # Delete the batch
                supabase.table("daily_prices").delete().in_("id", batch_ids).execute()
                deleted += len(batch_ids)
                print(f"  Deleted batch: {deleted}/{total_count} records")
                
                # Check if we're done
                if len(batch_ids) < batch_size:
                    break
            
            print(f"\n[COMPLETE] Deleted {deleted} price records")
            return deleted
        except Exception as e:
            print(f"\n[ERROR] Failed to delete price records: {e}")
            raise
    else:
        print(f"\n[DRY-RUN] Would delete {total_count} price records")
        return total_count


def repopulate_last_30_days(tickers: list = None, dry_run: bool = False) -> dict:
    """
    Repopulate daily_prices with price data for the specified date range.
    
    Args:
        tickers: List of tickers to backfill (None = all tracked tickers)
        dry_run: If True, don't actually fetch prices
        
    Returns:
        Dictionary with backfill statistics
    """
    # Use specific date range: 10/21/2025 to 11/20/2025
    start_date = date(2025, 10, 21)
    end_date = date(2025, 11, 20)
    
    print("\n" + "=" * 80)
    print("Repopulate Price Data")
    print("=" * 80)
    print(f"Date range: {start_date} to {end_date} (30 days)")
    print(f"Mode: {'DRY-RUN (no API calls)' if dry_run else 'LIVE (will fetch prices)'}")
    print(f"[NOTE] Using yfinance to fetch price data")
    
    # Get tickers
    if tickers is None:
        tickers = get_tracked_tickers()
    
    print(f"Tickers: {', '.join(tickers)}")
    print()
    
    total_inserted = 0
    total_failed = 0
    stats_by_ticker = {}
    
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] Processing {ticker}...")
        
        if dry_run:
            print(f"  [DRY-RUN] Would fetch prices for {ticker} from {start_date} to {end_date}")
            stats_by_ticker[ticker] = {"inserted": 0, "failed": False}
            continue
        
        try:
            # Fetch price data
            print(f"  [INFO] Fetching prices for {ticker} from {start_date} to {end_date}...")
            prices = fetch_price_data(ticker, start_date, end_date)
            
            if not prices:
                print(f"  [WARN] No price data fetched for {ticker}")
                print(f"  [WARN] This might be because:")
                print(f"    - Dates are in the future (yfinance can't fetch future prices)")
                print(f"    - Market was closed for the entire date range")
                print(f"    - Ticker symbol is invalid")
                stats_by_ticker[ticker] = {"inserted": 0, "failed": True}
                total_failed += 1
                continue
            
            # Check if we got data for the requested date range
            if prices:
                actual_dates = [p["date"] for p in prices if isinstance(p.get("date"), date)]
                if actual_dates:
                    min_date = min(actual_dates)
                    max_date = max(actual_dates)
                    print(f"  [INFO] Fetched {len(prices)} price records")
                    print(f"  [INFO] Actual date range: {min_date} to {max_date}")
                    if min_date != start_date or max_date != end_date:
                        print(f"  [WARN] Date range differs from requested ({start_date} to {end_date})")
                else:
                    print(f"  [INFO] Fetched {len(prices)} price records")
            
            # Insert into database
            crud_supabase.upsert_prices(prices)
            
            inserted_count = len(prices)
            total_inserted += inserted_count
            stats_by_ticker[ticker] = {"inserted": inserted_count, "failed": False}
            
            print(f"  [DONE] Inserted {inserted_count} price records")
            
        except Exception as e:
            print(f"  [ERROR] Failed to fetch/insert prices for {ticker}: {e}")
            stats_by_ticker[ticker] = {"inserted": 0, "failed": True}
            total_failed += 1
            continue
    
    return {
        "total_inserted": total_inserted,
        "total_failed": total_failed,
        "by_ticker": stats_by_ticker
    }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Reset daily_prices table and repopulate with price data for 10/21/2025 to 11/20/2025",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what will happen (dry-run):
  python -m scripts.reset_and_backfill_prices --dry-run
  
  # Actually reset and repopulate (10/21/2025 to 11/20/2025):
  python -m scripts.reset_and_backfill_prices --no-dry-run
  
  # Reset and repopulate specific tickers:
  python -m scripts.reset_and_backfill_prices --tickers AAPL,MSFT,TSLA --no-dry-run
        """
    )
    
    parser.add_argument(
        '--tickers',
        type=str,
        default=None,
        help='Comma-separated list of tickers (default: all tracked tickers)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Dry-run mode: preview without making changes (default: True)'
    )
    parser.add_argument(
        '--no-dry-run',
        dest='dry_run',
        action='store_false',
        help='Disable dry-run mode and actually reset/backfill'
    )
    
    args = parser.parse_args()
    
    # Parse tickers
    tickers = None
    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(',')]
    
    # Step 1: Clear all price data
    print("STEP 1: Clear All Price Data")
    print("=" * 80)
    
    if not args.dry_run:
        print("\n[WARNING] This will PERMANENTLY DELETE ALL price data from the database!")
        print("[WARNING] After deletion, we will repopulate with price data for 10/21/2025 to 11/20/2025 from yfinance.")
        response = input("\nAre you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    deleted_count = clear_all_prices(dry_run=args.dry_run)
    
    if args.dry_run:
        print("\n[DRY-RUN] No price data was actually deleted.")
        print("Run with --no-dry-run to perform the reset and backfill.")
        return
    
    # Step 2: Repopulate with last 30 days
    print("\n\nSTEP 2: Repopulate with Last 30 Days")
    print("=" * 80)
    
    backfill_stats = repopulate_last_30_days(tickers=tickers, dry_run=False)
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Price records deleted: {deleted_count}")
    print(f"Price records inserted: {backfill_stats['total_inserted']}")
    print(f"Tickers failed: {backfill_stats['total_failed']}")
    
    if backfill_stats['by_ticker']:
        print("\nBy ticker:")
        for ticker, stats in backfill_stats['by_ticker'].items():
            status = "✓" if not stats['failed'] else "✗"
            print(f"  {status} {ticker}: {stats['inserted']} records")
    
    print("=" * 80)
    
    print("\n✅ Reset and backfill complete!")
    print(f"\nPrice data has been reset and repopulated for date range: 10/21/2025 to 11/20/2025")
    print("\nNext steps:")
    print("1. Verify prices in database (check Supabase)")
    print("2. Train model: python train_model.py")
    print("3. Test API: curl http://localhost:8000/api/summary?ticker=AAPL&start_date=2025-10-21&end_date=2025-11-20")


if __name__ == "__main__":
    main()

