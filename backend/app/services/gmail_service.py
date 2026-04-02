from app.services.gmail_client import GmailClient
from app.utils.logger import get_logger

logger = get_logger("GMAIL_SERVICE")


class GmailService:
    def __init__(self):
        self.client = GmailClient()

    def fetch_emails(self, limit=5):
        try:
            emails = self.client.get_messages(max_results=limit)
            logger.info(f"Fetched {len(emails)} emails from GmailService")
            return emails
        except Exception as e:
            logger.error(f"Error in GmailService: {e}")
            return []