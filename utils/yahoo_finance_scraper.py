from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_scraper import BaseScraper


class YahooFinanceScraper:
    """Scraper for CryptoPotato website"""

    def __init__(self, driver, days_back=1, num_articles=5, list_of_search_words=None):
        """
        Initialize the scraper.

        Args:
            days_back (int): Number of days back to check for articles (default: 1 = today only)
        """
        self.driver = driver
        self.days_back = days_back
        self.num_articles = num_articles
        self.base_url = "https://finance.yahoo.com/"
        self.list_of_search_words = list_of_search_words or ["Solana"]
    
    def scrape_website(self):
        """Visit a website and scrape its content"""
        print(f"\Starting from: {self.base_url}")
        for search_term in self.list_of_search_words:
            print(f"Searching for: {search_term}")
            self._scrape_website(search_term)
        

        # Find and execute the appropriate scraper
        # for domain, scraper_func in SCRAPERS.items():
        #     if domain in url:
        #         return scraper_func(self.driver, soup)

        # print(f"No scraper found for {url}")
        return None

    def _scrape_website(self, search_term):
        self._navigate_and_search(search_term)
        articles_to_visit = self._gather_links()
        article_texts = []
        for url in articles_to_visit:
            article_texts += self._visit_and_get_article(url)
        
        print(f"Scraped {len(article_texts)} articles from Yahoo Finance")
        print(article_texts)
        
    def _navigate_and_search(self, search_term):
        """Navigate to the website and perform search"""
        self.driver.get(self.base_url)
        # Wait until the search box is visible
        wait = WebDriverWait(self.driver, 5)
        search_box = search_box = wait.until(EC.visibility_of_element_located((By.ID, "ybar-sbq")))
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)
        
    
    def _gather_links(self):
        """Extract article links from Yahoo Finance search results"""
        print("Gathering article links from Yahoo Finance...")
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # Find all content divs that contain articles
        content_divs = soup.find_all('div', class_='content yf-lfbf5f')
        articles_to_visit = []

        for content_div in content_divs:
            if len(articles_to_visit) >= self.num_articles:
                break
            # Find the date in the footer
            footer_div = content_div.find('div', class_='footer yf-lfbf5f')
            if footer_div:
                publishing_div = footer_div.find('div', class_='publishing yf-m1e6lz')
                if publishing_div:
                    # Extract date text (e.g., "TheStreet • 3h ago")
                    date_text = publishing_div.get_text(strip=True)
                    # Split by bullet point and get the time part
                    if '•' in date_text:
                        date = date_text.split('•')[-1].strip()
                    else:
                        date = date_text

                    # Check if within date range
                    if not self._is_within_date_range(date):
                        break
                        
            
            # Find the link
            link_tag = content_div.find('a', class_='subtle-link fin-size-small titles noUnderline yf-106qqvl')
            if not link_tag:
                continue

            article_url = link_tag.get('href', '')
            if not article_url or not article_url.startswith('http'):
                continue
            articles_to_visit.append(article_url)

        timeframe = "today" if self.days_back == 1 else f"last {self.days_back} days"
        print(f"Found {len(articles_to_visit)} articles to visit ({timeframe})")
        print(articles_to_visit)
        return articles_to_visit

    def _visit_and_get_article(self, url):
        """Visit an article and extract its content"""
        print(f"Visiting article: {url}")

        article_texts = []
        self.driver.get(url)

        # Wait for page to load
        self.driver.implicitly_wait(5)

        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Extract title - Yahoo Finance uses h1 with class 'cover-title yf-1rjrr1'
        title_tag = soup.find('h1', class_='cover-title yf-1rjrr1')
        title = title_tag.get_text(strip=True) if title_tag else 'No title'

        # Extract content - Yahoo Finance uses div with class 'body yf-h0on0w'
        content_div = soup.find('div', class_='body yf-h0on0w')

        # Find all <p> elements within the content div
        if content_div:
            paragraphs = content_div.find_all('p', class_='yf-1090901')
            article_text = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            content = '\n'.join(article_text)
        else:
            content = 'No content'

        article_texts.append({'title': title, 'content': content})

        return article_texts

    def _is_within_date_range(self, date_str):
        """
        Check if the article was posted within the specified days_back range.

        Args:
            date_str (str): Date string from the article (e.g., "3h ago", "2d ago", "Oct 20, 2025")

        Returns:
            bool: True if within range, False otherwise
        """
        lowered_date_str = date_str.lower().strip()
        now = datetime.now()

        # Handle relative dates with abbreviated format (Yahoo Finance style)
        if 'just now' in lowered_date_str or 'm ago' in lowered_date_str:
            return True  # Minutes ago - always within range

        if 'h ago' in lowered_date_str:
            return True  # Hours ago - same day, so within range

        if 'd ago' in lowered_date_str:
            # Extract number of days (e.g., "2d ago" -> 2)
            try:
                days_ago = int(lowered_date_str.split('d')[0].strip())
                return days_ago < self.days_back
            except (ValueError, IndexError):
                return False

        # Also handle full text format for compatibility
        if 'hours ago' in lowered_date_str or 'hour ago' in lowered_date_str:
            return True

        if 'days ago' in lowered_date_str or 'day ago' in lowered_date_str:
            try:
                days_ago = int(date_str.split()[0])
                return days_ago < self.days_back
            except (ValueError, IndexError):
                return False

        # Handle absolute dates like "Oct 20, 2025"
        try:
            article_date = datetime.strptime(date_str, '%b %d, %Y')
            days_difference = (now - article_date).days

            # Article is within range if it's less than days_back days old
            return 0 <= days_difference < self.days_back
        except ValueError:
            # If parsing fails, return False
            return False
