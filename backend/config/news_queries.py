"""
Ticker-specific news query configuration.

Defines search terms and query strategies for each tracked ticker to ensure
we fetch relevant, ticker-specific news articles rather than generic business news.
"""

# Mainstream finance/business news domains to prioritize
TRUSTED_DOMAINS = [
    "reuters.com",
    "wsj.com",
    "bloomberg.com",
    "marketwatch.com",
    "cnbc.com",
    "finance.yahoo.com",
    "investopedia.com",
    "fool.com",
    "barrons.com",
    "thestreet.com",
    "benzinga.com",
    "seekingalpha.com",
    "bloomberg.com",
    "ft.com",
    "businesswire.com",
    "prnewswire.com"
]

# Finance-related keywords to include in queries
FINANCE_KEYWORDS = [
    "stock", "shares", "earnings", "results", "revenue",
    "guidance", "profit", "losses", "IPO", "dividend",
    "buyback", "downgrade", "upgrade", "analyst", "price target",
    "quarterly", "annual", "financial", "trading", "market"
]

# Ticker-specific search configuration
TICKER_QUERY_MAP = {
    "AAPL": {
        "company_name": "Apple Inc",
        "terms": ["Apple", "Apple Inc", "AAPL", "iPhone", "MacBook", "iPad", "Apple stock", "Tim Cook"]
    },
    "MSFT": {
        "company_name": "Microsoft",
        "terms": ["Microsoft", "MSFT", "Windows", "Azure", "Xbox", "Microsoft stock", "Satya Nadella"]
    },
    "GOOGL": {
        "company_name": "Alphabet",
        "terms": ["Google", "Alphabet", "GOOGL", "GOOG", "YouTube", "Google stock", "Sundar Pichai"]
    },
    "AMZN": {
        "company_name": "Amazon",
        "terms": ["Amazon", "AMZN", "AWS", "Amazon stock", "Jeff Bezos", "Andy Jassy"]
    },
    "META": {
        "company_name": "Meta Platforms",
        "terms": ["Meta", "Facebook", "META", "Instagram", "WhatsApp", "Meta stock", "Mark Zuckerberg"]
    },
    "TSLA": {
        "company_name": "Tesla",
        "terms": ["Tesla", "TSLA", "Tesla stock", "Elon Musk", "Model 3", "Model Y", "Model S", "Model X"]
    },
    "NVDA": {
        "company_name": "NVIDIA",
        "terms": ["NVIDIA", "NVDA", "Nvidia", "NVIDIA stock", "Jensen Huang", "GPU", "AI chips"]
    },
    "JPM": {
        "company_name": "JPMorgan Chase",
        "terms": ["JPMorgan", "JPM", "JPMorgan Chase", "JPM stock", "Jamie Dimon"]
    },
    "V": {
        "company_name": "Visa",
        "terms": ["Visa", "V", "Visa Inc", "Visa stock", "credit card", "payment"]
    },
    "JNJ": {
        "company_name": "Johnson & Johnson",
        "terms": ["Johnson & Johnson", "JNJ", "J&J", "JNJ stock", "pharmaceutical"]
    }
}


def get_ticker_config(symbol: str) -> dict:
    """
    Get configuration for a ticker symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        
    Returns:
        Dictionary with 'company_name' and 'terms' keys
        
    Raises:
        KeyError: If ticker is not in the configuration
    """
    symbol_upper = symbol.upper()
    if symbol_upper not in TICKER_QUERY_MAP:
        raise KeyError(f"Ticker {symbol} not found in TICKER_QUERY_MAP. Add it to config/news_queries.py")
    return TICKER_QUERY_MAP[symbol_upper]


def build_ticker_query_terms(symbol: str) -> str:
    """
    Build ticker query terms for news APIs.
    
    Returns company-specific terms that can be used for news searches.
    Note: Alpha Vantage handles query building internally, but this can be used
    for other APIs or documentation purposes.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Comma-separated string of search terms
    """
    config = get_ticker_config(symbol)
    terms = config["terms"]
    
    # Return comma-separated terms (for documentation/reference)
    return ", ".join(terms)


def get_tracked_tickers() -> list:
    """Get list of all tracked ticker symbols."""
    return list(TICKER_QUERY_MAP.keys())

