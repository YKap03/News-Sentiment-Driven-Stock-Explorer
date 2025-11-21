"""
Alpha Vantage Market News & Sentiment API client.

Fetches news articles with built-in sentiment analysis from Alpha Vantage.
Uses ticker-focused queries and relevance filtering to ensure we only
get articles that are genuinely about the specific ticker/company.

Documentation: https://www.alphavantage.co/documentation/#news-sentiment
"""
import httpx
import os
import time
import asyncio
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Import ticker configuration and relevance filtering
from config.news_queries import get_ticker_config
from config.relevance_filter import compute_relevance_score

load_dotenv()

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Rate limiting: Alpha Vantage free tier allows 5 API calls per minute
# We use 60 seconds (1 minute) between calls to be safe and stay well under the limit
# This ensures we make at most 1 call per minute (well under the 5 calls/minute limit)
ALPHAVANTAGE_MIN_DELAY_SECONDS = 60.0  # 60 seconds = 1 call per minute (safe for 5 calls/min limit)

# Track last request time for rate limiting
_last_request_time: Optional[float] = None


async def _rate_limit():
    """Apply rate limiting between Alpha Vantage requests."""
    global _last_request_time
    
    if _last_request_time is not None:
        elapsed = time.time() - _last_request_time
        if elapsed < ALPHAVANTAGE_MIN_DELAY_SECONDS:
            await asyncio.sleep(ALPHAVANTAGE_MIN_DELAY_SECONDS - elapsed)
    
    _last_request_time = time.time()


async def fetch_ticker_news(
    symbol: str,
    start_date: date,
    end_date: date,
    company_name: str = None,
    limit: int = 1000
) -> List[Dict]:
    """
    Fetch ticker-focused news articles from Alpha Vantage.
    
    Alpha Vantage NEWS_SENTIMENT endpoint provides:
    - News articles related to a ticker
    - Built-in sentiment scores
    - Article metadata
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        start_date: Start date (Alpha Vantage may not support date filtering directly)
        end_date: End date
        company_name: Optional company name (not used by Alpha Vantage, but kept for compatibility)
        limit: Maximum number of articles to fetch (default: 1000)
        
    Returns:
        List of article dictionaries with keys: ticker_symbol, published_at,
        headline, source, url, raw_text, is_relevant, relevance_score, sentiment_score
    """
    if not ALPHAVANTAGE_API_KEY:
        raise ValueError("ALPHAVANTAGE_API_KEY not set in environment")
    
    # Apply rate limiting
    await _rate_limit()
    
    articles = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Alpha Vantage NEWS_SENTIMENT endpoint
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": symbol,  # Comma-separated list of tickers
                "apikey": ALPHAVANTAGE_API_KEY,
                "limit": min(limit, 1000)  # Alpha Vantage limit
            }
            
            response = await client.get(ALPHAVANTAGE_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")
            
            if "Note" in data:
                # Rate limit message
                raise ValueError(f"Alpha Vantage Rate Limit: {data['Note']}")
            
            if "Information" in data:
                # API key or subscription issue
                raise ValueError(f"Alpha Vantage Info: {data['Information']}")
            
            # Extract feed data
            feed = data.get("feed", [])
            
            if not feed:
                print(f"    [INFO] No articles found for {symbol}")
                return articles
            
            print(f"    [INFO] Alpha Vantage returned {len(feed)} articles for {symbol}")
            print(f"    [WARNING] Alpha Vantage NEWS_SENTIMENT only returns RECENT articles (last few days)")
            print(f"    [WARNING] Historical date ranges (e.g., 2024-01-01 to 2024-12-31) may return 0 articles")
            
            # Process each article
            for article_data in feed:
                try:
                    # Parse published date
                    # Alpha Vantage format: "20240101T120000" (YYYYMMDDTHHMMSS)
                    published_str = article_data.get("time_published", "")
                    try:
                        if len(published_str) >= 15 and "T" in published_str:
                            # Alpha Vantage format: "20240101T120000"
                            year = int(published_str[0:4])
                            month = int(published_str[4:6])
                            day = int(published_str[6:8])
                            hour = int(published_str[9:11]) if len(published_str) > 9 else 0
                            minute = int(published_str[11:13]) if len(published_str) > 11 else 0
                            second = int(published_str[13:15]) if len(published_str) > 13 else 0
                            published_at = datetime(year, month, day, hour, minute, second)
                        elif len(published_str) >= 8:
                            # Fallback: just date part "20240101"
                            year = int(published_str[0:4])
                            month = int(published_str[4:6])
                            day = int(published_str[6:8])
                            published_at = datetime(year, month, day)
                        else:
                            # Try ISO format as last resort
                            published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                    except Exception as e:
                        print(f"    [WARN] Could not parse date '{published_str}': {e}")
                        continue
                    
                    # Filter by date range
                    article_date = published_at.date()
                    if article_date < start_date or article_date > end_date:
                        continue
                    
                    # Build article dict
                    article_dict = {
                        "ticker_symbol": symbol,
                        "published_at": published_at,
                        "headline": article_data.get("title", ""),
                        "source": article_data.get("source", "Unknown"),
                        "url": article_data.get("url", ""),
                        "raw_text": article_data.get("summary", "") or article_data.get("banner_image", "") or ""
                    }
                    
                    # Alpha Vantage provides sentiment scores directly
                    # Extract sentiment from ticker_sentiment array
                    ticker_sentiments = article_data.get("ticker_sentiment", [])
                    sentiment_score = None
                    sentiment_label = None
                    
                    for ticker_sent in ticker_sentiments:
                        if ticker_sent.get("ticker", "").upper() == symbol.upper():
                            # Alpha Vantage sentiment: "Bullish", "Somewhat-Bullish", "Neutral", "Somewhat-Bearish", "Bearish"
                            sentiment_label_av = ticker_sent.get("ticker_sentiment_label", "Neutral")
                            relevance_score_av = float(ticker_sent.get("relevance_score", "0"))
                            
                            # Convert Alpha Vantage sentiment to our scale (-1.0 to 1.0)
                            sentiment_map = {
                                "Bullish": 0.75,
                                "Somewhat-Bullish": 0.4,
                                "Neutral": 0.0,
                                "Somewhat-Bearish": -0.4,
                                "Bearish": -0.75
                            }
                            sentiment_score = sentiment_map.get(sentiment_label_av, 0.0)
                            sentiment_label = sentiment_label_av
                            break
                    
                    # If no ticker-specific sentiment, use overall sentiment
                    if sentiment_score is None:
                        overall_sentiment = article_data.get("overall_sentiment_label", "Neutral")
                        sentiment_map = {
                            "Bullish": 0.75,
                            "Somewhat-Bullish": 0.4,
                            "Neutral": 0.0,
                            "Somewhat-Bearish": -0.4,
                            "Bearish": -0.75
                        }
                        sentiment_score = sentiment_map.get(overall_sentiment, 0.0)
                        sentiment_label = overall_sentiment
                    
                    # Compute our relevance score (for weighting)
                    is_relevant, relevance_score = compute_relevance_score(article_dict, symbol)
                    article_dict["is_relevant"] = is_relevant
                    article_dict["relevance_score"] = float(relevance_score)
                    
                    # Add Alpha Vantage sentiment (if available)
                    article_dict["sentiment_score"] = sentiment_score
                    article_dict["sentiment_label"] = sentiment_label
                    
                    articles.append(article_dict)
                    
                except Exception as e:
                    print(f"    [WARN] Error processing article: {e}")
                    continue
            
            # Log filtering statistics
            total_fetched = len(articles)
            relevant_count = sum(1 for a in articles if a.get("is_relevant", False))
            if total_fetched > 0:
                print(f"    [INFO] Processed {total_fetched} articles, {relevant_count} relevant ({100*relevant_count/total_fetched:.1f}%)")
            elif len(feed) > 0:
                # We got articles from Alpha Vantage but they were all filtered out by date
                sample_dates = []
                for article_data in feed[:5]:
                    time_pub = article_data.get("time_published", "")
                    if time_pub:
                        try:
                            if len(time_pub) >= 8:
                                year = int(time_pub[0:4])
                                month = int(time_pub[4:6])
                                day = int(time_pub[6:8])
                                sample_dates.append(f"{year}-{month:02d}-{day:02d}")
                        except:
                            pass
                if sample_dates:
                    print(f"    [WARNING] All {len(feed)} articles were filtered out (not in date range {start_date} to {end_date})")
                    print(f"    [WARNING] Sample article dates from Alpha Vantage: {', '.join(sample_dates[:3])}")
                    print(f"    [WARNING] Alpha Vantage only provides RECENT articles, not historical data")
            
        except httpx.HTTPError as e:
            print(f"    [ERROR] HTTP error fetching from Alpha Vantage: {e}")
            raise
        except Exception as e:
            print(f"    [ERROR] Error fetching from Alpha Vantage: {e}")
            raise
    
    return articles


# Backward compatibility alias
async def fetch_news(
    symbol: str,
    start_date: date,
    end_date: date,
    company_name: str = None
) -> List[Dict]:
    """
    Backward-compatible alias for fetch_ticker_news.
    """
    return await fetch_ticker_news(symbol, start_date, end_date, company_name)

