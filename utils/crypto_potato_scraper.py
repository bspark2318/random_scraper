from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
from .base_scraper import BaseScraper


class CryptoPotatoScraper(BaseScraper):
    """Scraper for CryptoPotato website"""

    def __init__(self, days_back=1):
        """
        Initialize the scraper.

        Args:
            days_back (int): Number of days back to check for articles (default: 1 = today only)
        """
        self.days_back = days_back

    def scrape_func(self, driver, soup):
        """Extract Solana news from CryptoPotato"""
        print("Processing CryptoPotato...")

        # Find all article containers
        article_divs = soup.find_all('div', class_='cp-post')
        articles_to_visit = []

        for article in article_divs:
            # Find the link
            link_tag = article.find('a')
            if not link_tag:
                continue
            article_url = link_tag.get('href', '')
            # Find the date
            date_tag = article.find('span', class_='post-date')
            date = date_tag.get_text(strip=True) if date_tag else 'No date'

            # Check if posted within the specified days back
            within_range = self._is_within_date_range(date)

            if within_range:
                articles_to_visit.append(article_url)

        timeframe = "today" if self.days_back == 1 else f"last {self.days_back} days"
        print(f"Articles to visit ({timeframe}): {len(articles_to_visit)}")
        articles = []
        for url in articles_to_visit:
             articles += self.visit_and_get_article(driver, url)
        
        return articles

    def visit_and_get_article(self, driver, url):
        """Visit an article and extract its content"""
        print(f"Visiting article: {url}")

        article_texts = []
        driver.get(url)

        # Wait for page to load
        time.sleep(2)

        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract title and content
        title_tag = soup.find('h1', class_='post-title')
        title = title_tag.get_text(strip=True) if title_tag else 'No title'

        content_div = soup.find('div', class_='post-details-content')

        # Find all <p> elements within the content div
        if content_div:
            paragraphs = content_div.find_all('p')
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
            date_str (str): Date string from the article (e.g., "5 hours ago", "Oct 20, 2025")

        Returns:
            bool: True if within range, False otherwise
        """
        lowered_date_str = date_str.lower()
        now = datetime.now()

        # Handle relative dates
        if 'just now' in lowered_date_str or 'minutes ago' in lowered_date_str or 'minute ago' in lowered_date_str:
            return True  # Always within range

        if 'hours ago' in lowered_date_str or 'hour ago' in lowered_date_str:
            return True  # Same day, so within range

        if 'days ago' in lowered_date_str or 'day ago' in lowered_date_str:
            # Extract number of days
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
