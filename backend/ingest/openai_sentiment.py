"""
OpenAI-based sentiment analysis for news articles.
"""
import os
from typing import List, Dict, Tuple
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def analyze_sentiment_batch(articles: List[Dict]) -> List[Tuple[float, str]]:
    """
    Analyze sentiment for a batch of articles using OpenAI.
    
    Args:
        articles: List of article dicts with 'headline' and optionally 'raw_text'
        
    Returns:
        List of (sentiment_score, sentiment_label) tuples
        sentiment_score: float between -1.0 (negative) and 1.0 (positive)
        sentiment_label: 'Positive', 'Neutral', or 'Negative'
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in environment")
    
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    results = []
    
    # Process articles in smaller batches to avoid token limits
    batch_size = 10
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        
        # Build prompt
        texts = []
        for article in batch:
            text = article.get("raw_text", "") or article.get("headline", "")
            texts.append(text[:500])  # Limit length
        
        prompt = """Analyze the sentiment of the following news headlines/articles about stocks. 
For each item, respond with ONLY a JSON array of objects, each with:
- "score": a number between -1.0 (very negative) and 1.0 (very positive)
- "label": one of "Positive", "Neutral", or "Negative"

Items:
""" + "\n".join([f"{j+1}. {text}" for j, text in enumerate(texts)])

        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial sentiment analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            # Try to parse JSON response
            import json
            try:
                # Remove markdown code blocks if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                parsed = json.loads(content)
                
                for item in parsed:
                    score = float(item.get("score", 0.0))
                    label = item.get("label", "Neutral")
                    results.append((score, label))
            except json.JSONDecodeError:
                # Fallback: analyze individually
                for article in batch:
                    score, label = await analyze_sentiment_single(article)
                    results.append((score, label))
                    
        except Exception as e:
            print(f"Error in batch sentiment analysis: {e}")
            # Fallback to individual analysis
            for article in batch:
                try:
                    score, label = await analyze_sentiment_single(article)
                    results.append((score, label))
                except:
                    results.append((0.0, "Neutral"))
    
    return results


async def analyze_sentiment_single(article: Dict) -> Tuple[float, str]:
    """
    Analyze sentiment for a single article.
    
    Returns:
        (sentiment_score, sentiment_label) tuple
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in environment")
    
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    text = article.get("raw_text", "") or article.get("headline", "")
    text = text[:1000]  # Limit length
    
    prompt = f"""Analyze the sentiment of this financial news headline/article about stocks.

Text: {text}

Respond with ONLY a JSON object with:
- "score": a number between -1.0 (very negative) and 1.0 (very positive)
- "label": one of "Positive", "Neutral", or "Negative"
"""
    
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial sentiment analyst. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        import json
        parsed = json.loads(content)
        score = float(parsed.get("score", 0.0))
        label = parsed.get("label", "Neutral")
        return (score, label)
    except Exception as e:
        print(f"Error in single sentiment analysis: {e}")
        return (0.0, "Neutral")

