"""
Relevance filtering and scoring for news articles.

Filters out noise like market research reports, law firm press releases,
and other non-investable content that doesn't represent genuine ticker-specific news.

Also scores articles based on relevance:
- High score: Company name + finance terms (e.g., "Apple Inc stock")
- Medium score: Company name or ticker symbol
- Lower score: Product names or other company terms
"""

from typing import List, Tuple
from config.news_queries import get_ticker_config

# Finance keywords that indicate financial/investment relevance
FINANCE_KEYWORDS = [
    "stock", "stocks", "shares", "share", "earnings", "revenue", "profit", "loss",
    "trading", "analyst", "price target", "downgrade", "upgrade", "dividend",
    "buyback", "ipo", "guidance", "quarterly", "annual", "financial", "market"
]


# Phrases that indicate noise/spam content (case-insensitive matching)
NOISE_PHRASES = [
    "market research report",
    "market research and forecast",
    "market size",
    "market forecast",
    "forecast report",
    "2025-2030",
    "2025-2035",
    "2024-2030",
    "2024-2035",
    "investors have opportunity to join",
    "fraud investigation with the schall law firm",
    "investor alert",
    "class action lawsuit",
    "pomerantz law firm",
    "deloitte technology fast 500",
    "fastest-growing company",
    "ranked number",
    "market research and forecast report",
    # Generic industry reports
    "market research and forecast report",
    "industry analysis report",
    "global market report",
    # Political/geopolitical noise (unless explicitly about the company)
    "murder of journalist",
    "saudi crown prince",
    "new sanctions",
    "ransomware operations",
    # PR spam patterns
    "announces partnership with",
    "announces collaboration with",
    # Generic biotech/pharma industry reports
    "market research report 2025",
    "market research report 2024",
]


def is_obviously_noise(text: str) -> bool:
    """
    Check if text contains obvious noise phrases.
    
    Args:
        text: Article title or description text
        
    Returns:
        True if text contains noise phrases, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in NOISE_PHRASES)


def matches_company_terms(text: str, symbol: str, terms: List[str]) -> bool:
    """
    Check if text contains company/ticker-specific terms.
    
    Args:
        text: Article title or description text
        symbol: Stock ticker symbol (e.g., 'AAPL')
        terms: List of company-specific search terms
        
    Returns:
        True if text matches company terms, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower()
    symbol_lower = symbol.lower()
    
    # Check for ticker symbol (with word boundaries or in parentheses)
    # Look for patterns like "AAPL", "(AAPL)", "[AAPL]", "AAPL stock", etc.
    import re
    symbol_pattern = rf'\b{symbol_lower}\b'
    if re.search(symbol_pattern, text_lower):
        return True
    
    # Check for company terms
    for term in terms:
        term_lower = term.lower()
        # Use word boundaries for better matching
        term_pattern = rf'\b{re.escape(term_lower)}\b'
        if re.search(term_pattern, text_lower):
            return True
    
    return False


def compute_relevance_score(article: dict, symbol: str) -> Tuple[bool, float]:
    """
    Compute relevance score for an article (0.0 to 1.0).
    
    Scoring:
    - 1.0: Company name + finance terms (e.g., "Apple Inc stock")
    - 0.8: Ticker symbol + finance terms (e.g., "AAPL stock")
    - 0.7: Company name alone (e.g., "Apple Inc")
    - 0.6: Ticker symbol alone (e.g., "AAPL")
    - 0.4: Product names + finance terms (e.g., "iPhone stock")
    - 0.3: Product names alone (e.g., "iPhone")
    - 0.0: No match or noise
    
    Args:
        article: Article dictionary with 'headline' and optionally 'raw_text' or 'description'
        symbol: Stock ticker symbol
        
    Returns:
        Tuple of (is_relevant: bool, relevance_score: float)
        is_relevant is True if score >= 0.3 (minimum threshold)
    """
    # Get ticker configuration
    try:
        config = get_ticker_config(symbol)
        terms = config["terms"]
        company_name = config.get("company_name", "")
    except KeyError:
        # If ticker not in config, be permissive (fallback)
        terms = [symbol]
        company_name = ""
    
    # Combine headline and description/raw_text for analysis
    headline = article.get("headline", "") or ""
    description = article.get("raw_text", "") or article.get("description", "") or ""
    combined_text = f"{headline} {description}".strip()
    
    if not combined_text:
        return (False, 0.0)
    
    # First, check for obvious noise - if noise, score is 0
    if is_obviously_noise(combined_text):
        return (False, 0.0)
    
    text_lower = combined_text.lower()
    symbol_lower = symbol.lower()
    
    # Check for finance keywords
    has_finance = any(keyword in text_lower for keyword in FINANCE_KEYWORDS)
    
    # Check for company name (exact match, highest priority)
    company_name_lower = company_name.lower() if company_name else ""
    has_company_name = False
    if company_name_lower:
        import re
        # Check for full company name
        company_pattern = rf'\b{re.escape(company_name_lower)}\b'
        has_company_name = bool(re.search(company_pattern, text_lower))
    
    # Check for ticker symbol
    import re
    symbol_pattern = rf'\b{symbol_lower}\b'
    has_ticker = bool(re.search(symbol_pattern, text_lower))
    
    # Check for product/other terms (lower priority)
    has_product_terms = False
    # Primary terms are company name and ticker, secondary are products
    primary_terms = [company_name] if company_name else []
    primary_terms.append(symbol)
    secondary_terms = [t for t in terms if t not in primary_terms]
    
    for term in secondary_terms:
        term_lower = term.lower()
        term_pattern = rf'\b{re.escape(term_lower)}\b'
        if re.search(term_pattern, text_lower):
            has_product_terms = True
            break
    
    # Score based on what we found
    score = 0.0
    
    if has_company_name and has_finance:
        score = 1.0  # Best: Company name + finance
    elif has_ticker and has_finance:
        score = 0.8  # Ticker + finance
    elif has_company_name:
        score = 0.7  # Company name alone
    elif has_ticker:
        score = 0.6  # Ticker alone
    elif has_product_terms and has_finance:
        score = 0.4  # Product + finance
    elif has_product_terms:
        score = 0.3  # Product alone (minimum threshold)
    else:
        # No match at all
        return (False, 0.0)
    
    # Minimum threshold: score >= 0.3 to be considered relevant
    is_relevant = score >= 0.3
    
    return (is_relevant, score)


def is_article_relevant_to_ticker(article: dict, symbol: str) -> bool:
    """
    Determine if an article is relevant to a specific ticker (backward compatibility).
    
    Uses compute_relevance_score() internally.
    
    Args:
        article: Article dictionary with 'headline' and optionally 'raw_text' or 'description'
        symbol: Stock ticker symbol
        
    Returns:
        True if article is relevant, False otherwise
    """
    is_relevant, _ = compute_relevance_score(article, symbol)
    return is_relevant

