from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from utils import OpenAIAnalyzer, YahooFinanceScraper, TelegramNotifier

# Initialize scrapers
# Change days_back to control how far back to search (1 = today only, 7 = last week, etc.)
# crypto_potato_scraper = CryptoPotatoScraper(days_back=2)

def main():
    load_dotenv()

    # Initialize OpenAI analyzer and Telegram notifier after loading env vars
    openai_analyzer = OpenAIAnalyzer()
    telegram_notifier = TelegramNotifier()

    # Set up Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--incognito')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Set timeouts to prevent hanging
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)
    topics = ["Solana", "BYDDY", "ASTS", "QUBT", "IONQ"]
    yahoo_finance_scraper = YahooFinanceScraper(driver, list_of_search_words=topics)
    
    SCRAPERS = [
        yahoo_finance_scraper
    ]
    
    summaries = []
    
    try:
        for scraper in SCRAPERS:
            for topic in topics:
                if openai_analyzer.is_analysis_cached(topic):
                    analysis = openai_analyzer.load_from_cache(topic)
                    summaries.append({"topic": topic, **analysis})
                else:
                    articles = scraper.scrape_website()
                    articles_list = articles.get(topic, [])
                    print(f"\nScraped {len(articles_list)} articles for topic: {topic}")
                    analysis = openai_analyzer.analyze_all_articles(articles_list, topic)
                    summaries.append({"topic": topic, **analysis})

        # Send all summaries to Telegram
        if summaries:
            print("\n" + "="*60)
            print("Sending summaries to Telegram...")
            telegram_notifier.send_multiple_summaries(summaries)
            print("="*60)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()