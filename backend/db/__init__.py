"""Database models and CRUD operations using Supabase."""
from db.supabase_client import get_supabase
from db import crud_supabase

__all__ = [
    "get_supabase",
    "crud_supabase"
]

