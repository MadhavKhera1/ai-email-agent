from app.services.gmail_client import GmailClient
from app.utils.logger import get_logger
import base64
from email.mime.text import MIMEText

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
        
    def create_draft(self, to_email, subject, body):
        try:
            message = MIMEText(body)

            message['to'] = to_email
            message['subject'] = f"Re: {subject}"

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            draft = {
                'message': {
                    'raw': raw_message
                }
            }

            draft = self.client.service.users().drafts().create(
                userId='me',
                body=draft
            ).execute()

            print("Draft created successfully")
            return draft

        except Exception as e:
            print(f"Draft creation error: {e}")
            return None