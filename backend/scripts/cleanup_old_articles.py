"""
Cleanup script to remove old articles that are outside the desired date range.

This script helps clean up old NewsAPI articles or any articles outside
the last 30 days (or a configurable range) to ensure only recent,
relevant articles remain in the database.
"""
import sys
import argparse
from pathlib import Path
from datetime import date, timedelta
from typing import Optional

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from db import crud_supabase
from utils.date_helpers import get_last_30_days_range


def cleanup_old_articles(
    ticker_symbol: Optional[str] = None,
    days_to_keep: int = 30,
    dry_run: bool = True,
    delete_articles_without_sentiment: bool = False
) -> dict:
    """
    Clean up old articles outside the specified date range.
    
    Args:
        ticker_symbol: Specific ticker to clean (None = all tickers)
        days_to_keep: Number of days to keep (default: 30)
        dry_run: If True, only show what would be deleted
        delete_articles_without_sentiment: If True, also delete articles without sentiment scores
        
    Returns:
        Dictionary with cleanup statistics
    """
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=days_to_keep)
    
    print("=" * 80)
    print("Article Cleanup Script")
    print("=" * 80)
    print(f"Mode: {'DRY-RUN (no deletions)' if dry_run else 'LIVE (will delete articles)'}")
    print(f"Date range to KEEP: {start_date} to {end_date} ({days_to_keep} days)")
    print(f"Articles OUTSIDE this range will be deleted")
    if delete_articles_without_sentiment:
        print(f"Articles WITHOUT sentiment scores will also be deleted")
    print()
    
    # Get tickers to process
    if ticker_symbol:
        tickers = [ticker_symbol.upper()]
    else:
        all_tickers = crud_supabase.get_tickers()
        tickers = [t["symbol"] for t in all_tickers]
    
    print(f"Processing {len(tickers)} ticker(s): {', '.join(tickers)}")
    print()
    
    total_deleted = 0
    total_kept = 0
    stats_by_ticker = {}
    
    for ticker in tickers:
        print(f"Processing {ticker}...")
        
        # Get ALL articles for this ticker (not filtered by date)
        # We'll filter in code to find old ones
        all_articles = crud_supabase.get_articles(
            ticker, 
            date(2020, 1, 1),  # Very old start date to get everything
            date.today() + timedelta(days=1),  # Future date to get everything
            relevant_only=False  # Get all articles, not just relevant ones
        )
        
        print(f"  Total articles in database: {len(all_articles)}")
        
        articles_to_delete = []
        articles_to_keep = []
        
        for article in all_articles:
            # Parse published date
            pub_date_str = article.get("published_at")
            pub_date = None
            
            try:
                if isinstance(pub_date_str, str):
                    # Extract date part
                    date_part = pub_date_str.split("T")[0].split(" ")[0]
                    pub_date = date.fromisoformat(date_part)
                elif isinstance(pub_date_str, date):
                    pub_date = pub_date_str
            except Exception as e:
                print(f"    [WARN] Could not parse date '{pub_date_str}': {e}")
                # If we can't parse the date, we'll keep it (safer)
                articles_to_keep.append(article)
                continue
            
            if pub_date is None:
                articles_to_keep.append(article)
                continue
            
            # Check if article is outside date range
            if pub_date < start_date or pub_date > end_date:
                articles_to_delete.append((article, pub_date, "outside_date_range"))
                continue
            
            # Check if article has no sentiment score (optional)
            if delete_articles_without_sentiment:
                sentiment_score = article.get("sentiment_score")
                if sentiment_score is None:
                    articles_to_delete.append((article, pub_date, "no_sentiment"))
                    continue
            
            # Keep this article
            articles_to_keep.append(article)
        
        print(f"  Articles to KEEP: {len(articles_to_keep)}")
        print(f"  Articles to DELETE: {len(articles_to_delete)}")
        
        # Show breakdown by reason
        if articles_to_delete:
            by_reason = {}
            for article, pub_date, reason in articles_to_delete:
                by_reason[reason] = by_reason.get(reason, 0) + 1
            
            print(f"  Breakdown:")
            for reason, count in by_reason.items():
                print(f"    - {reason}: {count}")
            
            # Show sample dates
            sample_dates = sorted([pub_date for _, pub_date, _ in articles_to_delete[:5]])
            if sample_dates:
                print(f"  Sample dates to delete: {sample_dates}")
        
        stats_by_ticker[ticker] = {
            "total": len(all_articles),
            "to_keep": len(articles_to_keep),
            "to_delete": len(articles_to_delete)
        }
        
        # Delete articles if not dry-run
        if not dry_run and articles_to_delete:
            print(f"  [DELETING] {len(articles_to_delete)} articles...")
            
            # Delete by ID (Supabase)
            from db.supabase_client import get_supabase
            supabase = get_supabase()
            article_ids = [article["id"] for article, _, _ in articles_to_delete]
            
            # Delete in batches
            batch_size = 100
            deleted_count = 0
            for i in range(0, len(article_ids), batch_size):
                batch = article_ids[i:i + batch_size]
                try:
                    result = supabase.table("news_articles").delete().in_("id", batch).execute()
                    deleted_count += len(batch)
                    print(f"    Deleted batch {i//batch_size + 1}: {len(batch)} articles")
                except Exception as e:
                    print(f"    [ERROR] Failed to delete batch: {e}")
            
            print(f"  [DONE] Deleted {deleted_count} articles")
            total_deleted += deleted_count
        else:
            total_deleted += len(articles_to_delete)
        
        total_kept += len(articles_to_keep)
        print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total articles to KEEP: {total_kept}")
    print(f"Total articles to DELETE: {total_deleted}")
    
    if dry_run:
        print("\n[DRY-RUN] No articles were actually deleted.")
        print("Run with --no-dry-run to perform the deletion.")
    else:
        print(f"\n[COMPLETE] Deleted {total_deleted} articles.")
    
    return {
        "total_kept": total_kept,
        "total_deleted": total_deleted,
        "by_ticker": stats_by_ticker
    }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Clean up old articles outside the last N days",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (preview what would be deleted):
  python -m scripts.cleanup_old_articles --days 30 --dry-run
  
  # Delete articles older than 30 days:
  python -m scripts.cleanup_old_articles --days 30 --no-dry-run
  
  # Delete articles older than 60 days for a specific ticker:
  python -m scripts.cleanup_old_articles --ticker AAPL --days 60 --no-dry-run
  
  # Also delete articles without sentiment scores:
  python -m scripts.cleanup_old_articles --days 30 --delete-no-sentiment --no-dry-run
        """
    )
    
    parser.add_argument(
        '--ticker',
        type=str,
        default=None,
        help='Specific ticker to clean (default: all tickers)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to keep (default: 30)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Dry-run mode: preview without deleting (default: True)'
    )
    parser.add_argument(
        '--no-dry-run',
        dest='dry_run',
        action='store_false',
        help='Disable dry-run mode and actually delete articles'
    )
    parser.add_argument(
        '--delete-no-sentiment',
        action='store_true',
        help='Also delete articles that have no sentiment score'
    )
    
    args = parser.parse_args()
    
    if not args.dry_run:
        print("\n[WARNING] This will PERMANENTLY DELETE articles from the database!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    cleanup_old_articles(
        ticker_symbol=args.ticker,
        days_to_keep=args.days,
        dry_run=args.dry_run,
        delete_articles_without_sentiment=args.delete_no_sentiment
    )


if __name__ == "__main__":
    main()

