"""
Date helper utilities for calculating default date ranges.
"""
from datetime import date, timedelta


def get_last_30_days_range() -> tuple[date, date]:
    """
    Get the date range for the last 30 days.
    
    Returns:
        Tuple of (start_date, end_date) where:
        - start_date: 30 days ago
        - end_date: today
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    return start_date, end_date


def get_last_n_days_range(n_days: int = 30) -> tuple[date, date]:
    """
    Get the date range for the last N days.
    
    Args:
        n_days: Number of days to go back (default: 30)
        
    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=n_days)
    return start_date, end_date

