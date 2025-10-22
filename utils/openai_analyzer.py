import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI

class OpenAIAnalyzer:
    """Handles article analysis using OpenAI API"""

    def __init__(self, api_key=None, cache_dir="cache"):
        """
        Initialize the OpenAI analyzer.

        Args:
            api_key (str, optional): OpenAI API key. If not provided, uses OPENAI_API_KEY env variable.
            cache_dir (str): Directory to store cached responses. Default is "cache".
        """
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_KEY'))
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_filename(self, website_name):
        """Generate cache filename based on website and today's date"""
        today = datetime.now().strftime("%Y-%m-%d")
        safe_website_name = website_name.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "_")
        return self.cache_dir / f"{safe_website_name}_{today}.json"

    def _load_from_cache(self, website_name):
        """Load analysis from cache if it exists for today"""
        cache_file = self._get_cache_filename(website_name)
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None

    def _save_to_cache(self, website_name, analysis):
        """Save analysis to cache"""
        cache_file = self._get_cache_filename(website_name)
        with open(cache_file, 'w') as f:
            json.dump(analysis, f, indent=2)

    def analyze_all_articles(self, articles, website_name):
        """
        Analyze all articles together for an overall summary and sentiment.

        Args:
            articles (list): List of dictionaries with 'title' and 'content' keys
            website_name (str): Name/URL of the website for caching purposes

        Returns:
            dict: Dictionary containing 'summary', 'sentiment', and 'reasoning' keys
        """
        # Check cache first
        cached_result = self._load_from_cache(website_name)
        if cached_result:
            print(f"Using cached analysis for {website_name}")
            return cached_result
        # Combine all articles into one text block
        combined_text = ""
        for i, article in enumerate(articles, 1):
            combined_text += f"\n\nArticle {i}:\nTitle: {article['title']}\nContent: {article['content']}\n"

        prompt = f"""Analyze the following collection of cryptocurrency articles about Solana:

{combined_text}

Please provide:
1. A one-paragraph summary no more than 400 words MAX that synthesizes the key themes and information across ALL articles
2. An overall sentiment analysis for stock evaluation (bullish/bearish/neutral) with reasoning

Format your response as:
Summary: [your summary here]

Sentiment: [bullish/bearish/neutral]
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in cryptocurrency markets. Provide concise, accurate analysis that synthesizes multiple sources."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )

            analysis = response.choices[0].message.content
            result = self._parse_response(analysis)

            # Save to cache
            self._save_to_cache(website_name, result)

            return result

        except Exception as e:
            print(f"Error analyzing articles: {e}")
            return {"summary": "Error analyzing articles", "sentiment": "unknown"}


    def _parse_response(self, response_text):
        """Parse the OpenAI response into structured data"""
        lines = response_text.strip().split('\n')

        summary = ""
        sentiment = ""

        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith("Summary:"):
                current_section = "summary"
                summary = line.replace("Summary:", "").strip()
            elif line.startswith("Sentiment:"):
                current_section = "sentiment"
                sentiment = line.replace("Sentiment:", "").strip()
            elif line and current_section == "summary":
                summary += " " + line
            
        return {
            "summary": summary.strip(),
            "sentiment": sentiment.strip(),
        }
