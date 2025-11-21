-- SQL script to create tables in Supabase
-- Run this in the Supabase SQL Editor

-- Create tickers table
CREATE TABLE IF NOT EXISTS tickers (
    id SERIAL PRIMARY KEY,
    symbol TEXT UNIQUE NOT NULL,
    name TEXT
);

CREATE INDEX IF NOT EXISTS idx_tickers_symbol ON tickers(symbol);

-- Create daily_prices table
CREATE TABLE IF NOT EXISTS daily_prices (
    id SERIAL PRIMARY KEY,
    ticker_symbol TEXT NOT NULL REFERENCES tickers(symbol),
    date DATE NOT NULL,
    open NUMERIC(10, 2) NOT NULL,
    high NUMERIC(10, 2) NOT NULL,
    low NUMERIC(10, 2) NOT NULL,
    close NUMERIC(10, 2) NOT NULL,
    volume BIGINT NOT NULL,
    UNIQUE(ticker_symbol, date)
);

CREATE INDEX IF NOT EXISTS idx_daily_prices_ticker ON daily_prices(ticker_symbol);
CREATE INDEX IF NOT EXISTS idx_daily_prices_date ON daily_prices(date);

-- Create news_articles table
CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    ticker_symbol TEXT NOT NULL REFERENCES tickers(symbol),
    published_at TIMESTAMP NOT NULL,
    headline TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT,
    sentiment_score NUMERIC(5, 3),
    sentiment_label TEXT,
    raw_text TEXT,
    is_relevant BOOLEAN DEFAULT true,
    relevance_score NUMERIC(3, 2)
);

CREATE INDEX IF NOT EXISTS idx_news_articles_ticker ON news_articles(ticker_symbol);
CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON news_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_news_articles_sentiment ON news_articles(sentiment_score) WHERE sentiment_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_news_articles_relevant ON news_articles(is_relevant) WHERE is_relevant = true;

-- Create daily_features table (optional, for ML)
CREATE TABLE IF NOT EXISTS daily_features (
    id SERIAL PRIMARY KEY,
    ticker_symbol TEXT NOT NULL REFERENCES tickers(symbol),
    date DATE NOT NULL,
    sentiment_avg NUMERIC(5, 3),
    sentiment_rolling_mean_3d NUMERIC(5, 3),
    return_1d NUMERIC(10, 6),
    volatility_5d NUMERIC(10, 6),
    future_3d_return_positive INTEGER,
    UNIQUE(ticker_symbol, date)
);

CREATE INDEX IF NOT EXISTS idx_daily_features_ticker ON daily_features(ticker_symbol);
CREATE INDEX IF NOT EXISTS idx_daily_features_date ON daily_features(date);

-- Enable Row Level Security (RLS) - optional, but recommended
ALTER TABLE tickers ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE news_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_features ENABLE ROW LEVEL SECURITY;

-- Create policies to allow all operations (adjust as needed for your security requirements)
CREATE POLICY "Allow all operations on tickers" ON tickers FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on daily_prices" ON daily_prices FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on news_articles" ON news_articles FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on daily_features" ON daily_features FOR ALL USING (true) WITH CHECK (true);

