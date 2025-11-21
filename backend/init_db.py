"""
Initialize database: create tables and seed initial tickers using Supabase.
"""
from db.supabase_client import get_supabase
from db import crud_supabase


def seed_tickers():
    """Seed initial tickers."""
    supabase = get_supabase()
    
    # Common tech stocks
    tickers = [
        ("AAPL", "Apple Inc."),
        ("MSFT", "Microsoft Corporation"),
        ("GOOGL", "Alphabet Inc."),
        ("AMZN", "Amazon.com Inc."),
        ("META", "Meta Platforms Inc."),
        ("TSLA", "Tesla Inc."),
        ("NVDA", "NVIDIA Corporation"),
        ("JPM", "JPMorgan Chase & Co."),
        ("V", "Visa Inc."),
        ("JNJ", "Johnson & Johnson")
    ]
    
    for symbol, name in tickers:
        existing = crud_supabase.get_ticker_by_symbol(symbol)
        if not existing:
            crud_supabase.create_ticker(symbol, name)
            print(f"Added ticker: {symbol} - {name}")
        else:
            print(f"Ticker {symbol} already exists")
    
    print("Tickers seeded successfully")


if __name__ == "__main__":
    print("Initializing database with Supabase...")
    print("\nNOTE: Make sure you've run the SQL script in Supabase SQL Editor first!")
    print("The SQL script is located at: backend/db/init_supabase_tables.sql\n")
    
    try:
        seed_tickers()
        print("\nDatabase initialization complete!")
        print("\nNext steps:")
        print("1. Run 'python train_model.py' to train the ML model")
        print("2. Start the API with 'uvicorn app:app --reload'")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. You've created the tables using the SQL script in Supabase SQL Editor")
        print("2. Your SUPABASE_URL and SUPABASE_KEY are set correctly in .env")
        print("3. Row Level Security policies allow operations (or disable RLS for development)")
