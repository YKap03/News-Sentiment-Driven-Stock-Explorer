"""
SQLAlchemy models for Supabase Postgres database.
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, ForeignKey, UniqueConstraint, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import date, datetime

Base = declarative_base()


class Ticker(Base):
    """Stock ticker symbols and names."""
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)


class DailyPrice(Base):
    """Daily stock price data."""
    __tablename__ = "daily_prices"

    id = Column(Integer, primary_key=True, index=True)
    ticker_symbol = Column(String, ForeignKey("tickers.symbol"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)

    __table_args__ = (
        UniqueConstraint('ticker_symbol', 'date', name='uq_ticker_date'),
    )


class NewsArticle(Base):
    """News articles with sentiment scores."""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    ticker_symbol = Column(String, ForeignKey("tickers.symbol"), nullable=False, index=True)
    published_at = Column(DateTime, nullable=False, index=True)
    headline = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    url = Column(Text, nullable=True)
    sentiment_score = Column(Numeric(5, 3), nullable=True)  # -1.0 to 1.0
    sentiment_label = Column(String, nullable=True)  # 'Positive', 'Neutral', 'Negative'
    raw_text = Column(Text, nullable=True)
    is_relevant = Column(Boolean, default=True, nullable=False, index=True)  # True if article is relevant to the ticker
    relevance_score = Column(Numeric(3, 2), nullable=True)  # 0.0 to 1.0, relevance weight for scoring


class DailyFeature(Base):
    """Precomputed ML features per day."""
    __tablename__ = "daily_features"

    id = Column(Integer, primary_key=True, index=True)
    ticker_symbol = Column(String, ForeignKey("tickers.symbol"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    sentiment_avg = Column(Numeric(5, 3), nullable=True)
    sentiment_rolling_mean_3d = Column(Numeric(5, 3), nullable=True)
    return_1d = Column(Numeric(10, 6), nullable=True)
    volatility_5d = Column(Numeric(10, 6), nullable=True)
    future_3d_return_positive = Column(Integer, nullable=True)  # 0 or 1

    __table_args__ = (
        UniqueConstraint('ticker_symbol', 'date', name='uq_feature_ticker_date'),
    )

