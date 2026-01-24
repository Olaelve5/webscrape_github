import requests
from bs4 import BeautifulSoup

def run_scraper():
    # Target URL (specifically designed for testing scrapers)
    url = 'http://quotes.toscrape.com/'
    
    print(f"Fetching {url}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract the first quote found on the page
        quote = soup.find('span', class_='text').text
        author = soup.find('small', class_='author').text
        
        print("--- SUCCESS ---")
        print(f"Quote: {quote}")
        print(f"Author: {author}")
    else:
        print(f"Failed to retrieve page. Status code: {response.status_code}")

if __name__ == "__main__":
    run_scraper()