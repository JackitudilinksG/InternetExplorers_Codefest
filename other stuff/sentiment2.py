from dotenv import load_dotenv
import os
import time
from polygon import RESTClient
import google.generativeai as genai

load_dotenv()

# Configure APIs
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
client = RESTClient(api_key=POLYGON_API_KEY)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def analyze_sentiment(ticker, title, date):
    prompt = f"""Analyze this news headline regarding {ticker}. Respond with ONLY one word: 
    Positive, Negative, or Neutral. Use Neutral if uncertain. No explanations or punctuation.
    
    Headline: {title}
    Date: {date}
    Company: {ticker}"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip().split()[0].capitalize()
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return "Neutral"

# Configuration
ticker = "TSLA"
start_date = "2025-03-01"
end_date = "2025-04-12"

try:
    # Fetch news articles
    news_articles = client.list_ticker_news(
        ticker, 
        params={
            "published_utc.gte": start_date,
            "published_utc.lt": end_date,
            "include_insights": "true"
        }, 
        order="desc", 
        limit=100
    )

    # Process articles with dual rate limiting
    for article in news_articles:
        try:
            # Get sentiment analysis
            sentiment = analyze_sentiment(
                ticker,
                article.title,
                article.published_utc
            )
            
            # Display results
            print(f"\n{ticker} - {article.published_utc}")
            print(f"Title: {article.title}")
            print(f"Sentiment: {sentiment}")
            print("---")
            
        except Exception as e:
            print(f"Processing Error: {str(e)}")
        
        # Rate limiting for both Polygon and Gemini
        time.sleep(12)  # 12 seconds between requests

except Exception as e:
    print(f"Critical Error: {str(e)}")
    print("Waiting 60 seconds before retrying...")
    time.sleep(60)