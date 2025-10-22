from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from utils import CryptoPotatoScraper

websites = [
    "https://cryptopotato.com/tag/solana/",
    "https://finance.yahoo.com/quote/SOL-USD/",
]

# Initialize scrapers
# Change days_back to control how far back to search (1 = today only, 7 = last week, etc.)
crypto_potato_scraper = CryptoPotatoScraper(days_back=1)


def scrape_yahoo_finance(driver, soup):
    """Extract Solana price data from Yahoo Finance"""
    # TODO: Implement scraping logic
    print("Processing Yahoo Finance...")
    return {}

# Map domains to their processing functions
SCRAPERS = {
    "cryptopotato.com": crypto_potato_scraper.scrape_func,
    "finance.yahoo.com": scrape_yahoo_finance,
}

def scrape_website(driver, url):
    """Visit a website and scrape its content"""
    print(f"\nVisiting: {url}")
    driver.get(url)

    # Wait for page to load
    time.sleep(3)

    # Get page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract text content
    print(f"Title: {driver.title}")
    print(f"Page length: {len(soup.get_text())} characters")

    # Find and execute the appropriate scraper
    for domain, scraper_func in SCRAPERS.items():
        if domain in url:
            return scraper_func(driver, soup)

    print(f"No scraper found for {url}")
    return None

def main():
    # Set up Chrome driver
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment to run in headless mode
    options.add_argument('--incognito')
    options.add_argument('--disable-popup-blocking')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        for website in websites:
            data = scrape_website(driver, website)
            # Process the returned data as needed
            if data:
                print(f"Scraped data: {data}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()