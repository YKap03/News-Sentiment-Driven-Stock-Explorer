-- Migration script to add is_relevant and relevance_score columns to news_articles table
-- Run this in the Supabase SQL Editor if the columns don't exist yet

-- Add is_relevant column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'news_articles' AND column_name = 'is_relevant'
    ) THEN
        ALTER TABLE news_articles ADD COLUMN is_relevant BOOLEAN DEFAULT true;
        
        -- Set all existing articles to relevant by default
        -- (You may want to re-run relevance filtering on existing data)
        UPDATE news_articles SET is_relevant = true WHERE is_relevant IS NULL;
        
        -- Make column NOT NULL after setting defaults
        ALTER TABLE news_articles ALTER COLUMN is_relevant SET NOT NULL;
        
        -- Create index for faster filtering
        CREATE INDEX IF NOT EXISTS idx_news_articles_relevant 
        ON news_articles(is_relevant) WHERE is_relevant = true;
        
        RAISE NOTICE 'Added is_relevant column to news_articles table';
    ELSE
        RAISE NOTICE 'Column is_relevant already exists';
    END IF;
END $$;

-- Add relevance_score column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'news_articles' AND column_name = 'relevance_score'
    ) THEN
        ALTER TABLE news_articles ADD COLUMN relevance_score NUMERIC(3, 2);
        
        -- Set default relevance_score for existing articles
        -- Articles with is_relevant=true get 0.7 (medium), false get 0.0
        UPDATE news_articles 
        SET relevance_score = CASE 
            WHEN is_relevant = true THEN 0.7 
            ELSE 0.0 
        END
        WHERE relevance_score IS NULL;
        
        RAISE NOTICE 'Added relevance_score column to news_articles table';
    ELSE
        RAISE NOTICE 'Column relevance_score already exists';
    END IF;
END $$;

