# Environment Variables Template

Copy this to `backend/.env` and fill in your actual values:

```env
# Supabase Database Configuration
# Get these from your Supabase project dashboard → Settings → API
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# Alpha Vantage API (Required for news data)
# Get free API key at: https://www.alphavantage.co/support/#api-key
ALPHAVANTAGE_API_KEY=your-alpha-vantage-api-key-here

# OpenAI API (Optional - for additional sentiment enrichment)
# Alpha Vantage provides sentiment, but you can use OpenAI for extra analysis
# Get API key at: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-api-key-here
```

## Required Variables

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon/public key
- `ALPHAVANTAGE_API_KEY` - Alpha Vantage API key (for news)

## Optional Variables

- `OPENAI_API_KEY` - OpenAI API key (for sentiment enrichment if needed)

## Notes

- **NewsAPI is no longer used** - Removed in favor of Alpha Vantage
- Alpha Vantage provides built-in sentiment analysis, so OpenAI is optional
- All keys should be kept secret - never commit `.env` to git

