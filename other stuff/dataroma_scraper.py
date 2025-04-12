import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_dataroma():
    url = "https://www.dataroma.com/m/rt.php"
    
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Make the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table containing the data
        table = soup.find('table')
        
        if not table:
            print("No table found on the page")
            return None
        
        # Extract headers
        headers = [th.text.strip() for th in table.find_all('th')]
        
        # Extract rows
        data = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cols = row.find_all('td')
            if cols:
                row_data = [col.text.strip() for col in cols]
                data.append(row_data)
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        
        # Save to CSV with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'dataroma_data_{timestamp}.csv'
        df.to_csv(filename, index=False)
        
        print(f"Data successfully scraped and saved to {filename}")
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    scrape_dataroma() 