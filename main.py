from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from utils import CryptoPotatoScraper, OpenAIAnalyzer, YahooFinanceScraper

# Initialize scrapers
# Change days_back to control how far back to search (1 = today only, 7 = last week, etc.)
# crypto_potato_scraper = CryptoPotatoScraper(days_back=2)

def main():
    load_dotenv()

    # Initialize OpenAI analyzer after loading env vars
    openai_analyzer = OpenAIAnalyzer()

    # Set up Chrome driver
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment to run in headless mode
    options.add_argument('--incognito')
    options.add_argument('--disable-popup-blocking')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yahoo_finance_scraper = YahooFinanceScraper(driver)
    
    SCRAPERS = [
        yahoo_finance_scraper,
        # crypto_potato_scraper,
    ]
    
    try:
        all_analyses = []
        for scraper in SCRAPERS:
            scraper.scrape_website()
        # # Process the returned data as needed
        # if data:
        #     print(f"Scraped {len(data)} articles from {website}")

        #     # Analyze articles for this website
        #     print(f"\nAnalyzing {len(data)} articles from {website}...")
        #     analysis = openai_analyzer.analyze_all_articles(data, website)
        #     all_analyses.append({
        #         'website': website,
        #         'analysis': analysis
        #     })

        # # Display results
        # if all_analyses:
        #     print("\n" + "="*80)
        #     print("ANALYSIS RESULTS")
        #     print("="*80)
        #     for item in all_analyses:
        #         print(f"\nWebsite: {item['website']}")
        #         print(f"Summary: {item['analysis']['summary']}")
        #         print(f"Sentiment: {item['analysis']['sentiment']}")
        #         print("-"*80)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()