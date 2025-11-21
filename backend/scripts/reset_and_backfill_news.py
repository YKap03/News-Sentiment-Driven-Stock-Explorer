"""
Reset news_articles table and repopulate with last 30 days of relevant articles.

This script:
1. Clears ALL articles from news_articles table
2. Backfills with last 30 days of ticker-relevant news from Alpha Vantage
3. Only stores articles that pass relevance filtering

WARNING: This will permanently delete all existing articles!
"""
import sys
import argparse
import asyncio
from pathlib import Path
from datetime import date, timedelta

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from db import crud_supabase
from db.supabase_client import get_supabase
from scripts.backfill_news import backfill_ticker
from config.news_queries import get_tracked_tickers


def clear_all_articles(dry_run: bool = True) -> int:
    """
    Clear all articles from the news_articles table.
    
    Args:
        dry_run: If True, only show what would be deleted
        
    Returns:
        Number of articles that would be/were deleted
    """
    supabase = get_supabase()
    
    # First, count articles
    response = supabase.table("news_articles").select("id", count="exact").execute()
    total_count = response.count if hasattr(response, 'count') else 0
    
    # Get sample articles to show
    sample_response = supabase.table("news_articles").select("ticker_symbol, published_at, headline").limit(5).execute()
    sample_articles = sample_response.data if sample_response.data else []
    
    print("=" * 80)
    print("Clear All Articles")
    print("=" * 80)
    print(f"Mode: {'DRY-RUN (no deletions)' if dry_run else 'LIVE (will delete all articles)'}")
    print(f"Total articles in database: {total_count}")
    
    if sample_articles:
        print("\nSample articles:")
        for i, article in enumerate(sample_articles, 1):
            headline = article.get("headline", "N/A")[:60]
            pub_date = article.get("published_at", "N/A")
            ticker = article.get("ticker_symbol", "N/A")
            print(f"  {i}. [{ticker}] {pub_date}: {headline}...")
    
    if total_count == 0:
        print("\n[INFO] Database is already empty. Nothing to delete.")
        return 0
    
    if not dry_run:
        print(f"\n[WARNING] This will DELETE ALL {total_count} articles from the database!")
        print("[WARNING] This action cannot be undone!")
        
        # Delete all articles
        print("\n[DELETING] All articles...")
        try:
            # Delete in batches to avoid timeouts
            batch_size = 1000
            deleted = 0
            
            while True:
                # Get a batch of IDs
                batch_response = supabase.table("news_articles").select("id").limit(batch_size).execute()
                batch_ids = [row["id"] for row in batch_response.data] if batch_response.data else []
                
                if not batch_ids:
                    break
                
                # Delete the batch
                supabase.table("news_articles").delete().in_("id", batch_ids).execute()
                deleted += len(batch_ids)
                print(f"  Deleted batch: {deleted}/{total_count} articles")
                
                # Check if we're done
                if len(batch_ids) < batch_size:
                    break
            
            print(f"\n[COMPLETE] Deleted {deleted} articles")
            return deleted
        except Exception as e:
            print(f"\n[ERROR] Failed to delete articles: {e}")
            raise
    else:
        print(f"\n[DRY-RUN] Would delete {total_count} articles")
        return total_count


async def repopulate_last_30_days(tickers: list = None, dry_run: bool = False) -> dict:
    """
    Repopulate news_articles with last 30 days of relevant articles.
    
    Args:
        tickers: List of tickers to backfill (None = all tracked tickers)
        dry_run: If True, don't actually fetch articles
        
    Returns:
        Dictionary with backfill statistics
    """
    # Calculate last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    print("\n" + "=" * 80)
    print("Repopulate Last 30 Days")
    print("=" * 80)
    print(f"Date range: {start_date} to {end_date} (30 days)")
    print(f"Mode: {'DRY-RUN (no API calls)' if dry_run else 'LIVE (will fetch articles)'}")
    print(f"[NOTE] Rate limiting: 1 minute wait between API calls (stays under 5 calls/min limit)")
    
    # Get tickers
    if tickers is None:
        tickers = get_tracked_tickers()
    
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Estimated time: ~{len(tickers)} minutes (1 call per minute)")
    print()
    
    total_stats = {
        'api_calls': 0,
        'articles_fetched': 0,
        'articles_relevant': 0,
        'articles_inserted': 0
    }
    
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] Processing {ticker}...")
        
        stats = await backfill_ticker(
            ticker,
            start_date,
            end_date,
            dry_run=dry_run,
            force_full_range=True  # Always use full range for fresh backfill
        )
        for key in total_stats:
            total_stats[key] += stats[key]
        
        # Wait 1 minute between calls (except after the last ticker)
        if not dry_run and i < len(tickers):
            print(f"\n[WAITING] 1 minute before next API call (staying under 5 calls/min limit)...")
            await asyncio.sleep(60)  # Wait 1 minute
            print(f"[RESUMING] Continuing with next ticker...\n")
    
    return total_stats


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Reset news_articles table and repopulate with last 30 days",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what will happen (dry-run):
  python -m scripts.reset_and_backfill_news --dry-run
  
  # Actually reset and repopulate:
  python -m scripts.reset_and_backfill_news --no-dry-run
  
  # Reset and repopulate specific tickers:
  python -m scripts.reset_and_backfill_news --tickers AAPL,MSFT,TSLA --no-dry-run
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
    
    # Step 1: Clear all articles
    print("STEP 1: Clear All Articles")
    print("=" * 80)
    
    if not args.dry_run:
        print("\n[WARNING] This will PERMANENTLY DELETE ALL articles from the database!")
        print("[WARNING] After deletion, we will repopulate with last 30 days from Alpha Vantage.")
        response = input("\nAre you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    deleted_count = clear_all_articles(dry_run=args.dry_run)
    
    if args.dry_run:
        print("\n[DRY-RUN] No articles were actually deleted.")
        print("Run with --no-dry-run to perform the reset and backfill.")
        return
    
    # Step 2: Repopulate with last 30 days
    print("\n\nSTEP 2: Repopulate with Last 30 Days")
    print("=" * 80)
    
    backfill_stats = await repopulate_last_30_days(tickers=tickers, dry_run=False)
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Articles deleted: {deleted_count}")
    print(f"Articles fetched: {backfill_stats['articles_fetched']}")
    print(f"Relevant articles: {backfill_stats['articles_relevant']}")
    print(f"Articles inserted: {backfill_stats['articles_inserted']}")
    print(f"API calls made: {backfill_stats['api_calls']}")
    print("=" * 80)
    
    print("\n✅ Reset and backfill complete!")
    print("\nNext steps:")
    print("1. Verify articles in database (check Supabase)")
    print("2. Train model: python train_model.py")
    print("3. Test API: curl http://localhost:8000/api/summary?ticker=AAPL")


if __name__ == "__main__":
    asyncio.run(main())

