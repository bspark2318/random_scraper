import os
import requests


class TelegramNotifier:
    """Sends notifications to Telegram"""

    def __init__(self, bot_token=None, chat_id=None):
        """
        Initialize the Telegram notifier.

        Args:
            bot_token (str, optional): Telegram bot token. If not provided, uses TELEGRAM_BOT_TOKEN env variable.
            chat_id (str, optional): Telegram chat ID. If not provided, uses TELEGRAM_CHAT_ID env variable.
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')

        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram bot token and chat ID must be provided either as arguments or environment variables")

    def send_message(self, message):
        """
        Send a message to Telegram.

        Args:
            message (str): Message to send

        Returns:
            bool: True if successful, False otherwise
        """
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print("✓ Message sent to Telegram")
                return True
            else:
                print(f"✗ Failed to send Telegram message: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error sending Telegram message: {e}")
            return False

    def send_summary(self, topic, summary, sentiment):
        """
        Send a formatted analysis summary to Telegram.

        Args:
            topic (str): Topic name
            summary (str): Analysis summary
            sentiment (str): Sentiment (bullish/bearish/neutral)

        Returns:
            bool: True if successful, False otherwise
        """
        # Format sentiment with emoji
        sentiment_emoji = {
            "bullish": "📈",
            "bearish": "📉",
            "neutral": "➡️"
        }
        emoji = sentiment_emoji.get(sentiment.lower(), "")

        message = f"""
🔔 *{topic} Analysis*

*Sentiment:* {emoji} {sentiment.upper()}

*Summary:*
{summary}

_Generated at {self._get_timestamp()}_
        """.strip()

        return self.send_message(message)

    def send_multiple_summaries(self, summaries):
        """
        Send multiple analysis summaries as one message.

        Args:
            summaries (list): List of dicts with 'topic', 'summary', 'sentiment' keys

        Returns:
            bool: True if successful, False otherwise
        """
        if not summaries:
            return False

        message_parts = ["📊 *Market Analysis Summary*\n"]

        for item in summaries:
            sentiment = item.get('sentiment', 'unknown')
            sentiment_emoji = {
                "bullish": "📈",
                "bearish": "📉",
                "neutral": "➡️"
            }.get(sentiment.lower(), "")

            message_parts.append(f"\n*{item.get('topic', 'Unknown')}* {sentiment_emoji}")
            message_parts.append(f"Sentiment: {sentiment.upper()}")
            message_parts.append(f"{item.get('summary', 'No summary available')}\n")
            message_parts.append("─" * 30)

        message_parts.append(f"\n_Generated at {self._get_timestamp()}_")
        message = "\n".join(message_parts)

        return self.send_message(message)

    def _get_timestamp(self):
        """Get current timestamp as formatted string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
