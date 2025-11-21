-- Migration script to add relevance_score column to news_articles table
-- Run this in the Supabase SQL Editor if the column doesn't exist yet

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

