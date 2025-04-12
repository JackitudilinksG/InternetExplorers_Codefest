from dotenv import load_dotenv
import os
import time
from datetime import datetime, timedelta
from polygon import RESTClient
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

load_dotenv()
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

client = RESTClient(api_key=POLYGON_API_KEY)

# Set the date range
start_date = "2023-01-01"
end_date = "2025-04-04"

# Convert to datetime objects
start = datetime.strptime(start_date, "%Y-%m-%d")
end = datetime.strptime(end_date, "%Y-%m-%d")

# Initialize sentiment count list
sentiment_count = []

# Process in 7-day batches to reduce API calls
batch_size = 7  # days
current_start = start

while current_start < end:
    # Calculate batch end date
    batch_end = min(current_start + timedelta(days=batch_size), end)
    
    # Format dates for API call
    batch_start_str = current_start.strftime("%Y-%m-%d")
    batch_end_str = batch_end.strftime("%Y-%m-%d")
    
    try:
        # Fetch news for the entire batch period
        batch_news = list(client.list_ticker_news(
            "CRWD",
            published_utc_gte=batch_start_str,
            published_utc_lt=batch_end_str,
            limit=1000  # Increased limit to get more data per call
        ))
        
        # Process each day in the batch
        current_date = current_start
        while current_date < batch_end:
            date_str = current_date.strftime("%Y-%m-%d")
            daily_sentiment = {
                'date': date_str,
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
            
            # Filter and process articles for the current day
            for article in batch_news:
                if article.published_utc.startswith(date_str):
                    if hasattr(article, 'insights') and article.insights:
                        for insight in article.insights:
                            if insight.sentiment == 'positive':
                                daily_sentiment['positive'] += 1
                            elif insight.sentiment == 'negative':
                                daily_sentiment['negative'] += 1
                            elif insight.sentiment == 'neutral':
                                daily_sentiment['neutral'] += 1
            
            sentiment_count.append(daily_sentiment)
            current_date += timedelta(days=1)
        
        # Move to next batch
        current_start = batch_end
        
        # Rate limiting: 5 calls per minute = 12 seconds between calls
        time.sleep(12)
        
    except Exception as e:
        print(f"Error processing batch {batch_start_str} to {batch_end_str}: {str(e)}")
        time.sleep(60)  # Wait longer if there's an error
        continue

# Convert to DataFrame
df_sentiment = pd.DataFrame(sentiment_count)

# Convert 'date' column to datetime
df_sentiment['date'] = pd.to_datetime(df_sentiment['date'])

# Set the date as the index
df_sentiment.set_index('date', inplace=True)

# Plotting the data
plt.figure(figsize=(20, 10))
plt.plot(df_sentiment['positive'], label='Positive', color='green')
plt.plot(df_sentiment['negative'], label='Negative', color='red')
plt.plot(df_sentiment['neutral'], label='Neutral', color='grey', linestyle='--')
plt.title('Sentiment Over Time')
plt.xlabel('Date')
plt.ylabel('Count')
plt.legend()
plt.grid(True)

# Format the x-axis to display dates better
plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gcf().autofmt_xdate()

# Saving the plot as an image file
plt.savefig('sentiment_over_time.png')
plt.show()