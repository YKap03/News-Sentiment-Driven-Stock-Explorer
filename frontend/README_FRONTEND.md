# Frontend Documentation

## Overview

React + TypeScript frontend for the News & Sentiment Driven Stock Explorer. Built with Vite and TailwindCSS.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables (copy `.env.example` to `.env.local`):
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Components

- **TickerSelector**: Dropdown to select stock ticker
- **DateRangePicker**: Date range selection
- **SummaryBar**: Summary statistics and ML insights
- **PriceSentimentChart**: Combined price and sentiment chart using Recharts
- **NewsFeed**: List of news articles with sentiment badges
- **ModelDetails**: ML model performance metrics

## Tech Stack

- React 18
- TypeScript
- Vite
- TailwindCSS
- Recharts (for charts)
- date-fns (for date formatting)

