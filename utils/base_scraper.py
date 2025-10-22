from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Abstract base class for all website scrapers"""

    @abstractmethod
    def scrape_func(self, driver, soup):
        """
        Main scraping function that extracts data from the page.

        Args:
            driver: Selenium WebDriver instance
            soup: BeautifulSoup parsed HTML

        Returns:
            dict: Dictionary containing scraped data
        """
        pass

    @abstractmethod
    def visit_and_get_article(self, driver, url):
        """
        Visit a specific article URL and extract its content.

        Args:
            driver: Selenium WebDriver instance
            url: URL of the article to visit

        Returns:
            list: List of dictionaries containing article data
                  Each dict should have 'title' and 'content' keys
        """
        pass
