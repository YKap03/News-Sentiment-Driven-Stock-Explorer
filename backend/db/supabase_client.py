"""
Supabase client initialization and configuration.
"""
import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL environment variable is not set. "
        "Please create a .env file in the backend/ directory with:\n"
        "SUPABASE_URL=https://your-project.supabase.co\n"
        "SUPABASE_KEY=your-anon-key"
    )

if not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_KEY environment variable is not set. "
        "Please create a .env file in the backend/ directory with:\n"
        "SUPABASE_URL=https://your-project.supabase.co\n"
        "SUPABASE_KEY=your-anon-key"
    )

# Initialize Supabase client lazily to avoid import-time errors
_supabase_client: Optional[Client] = None

def get_supabase() -> Client:
    """Get the Supabase client instance (lazy initialization)."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

