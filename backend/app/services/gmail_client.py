import os
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.utils.logger import get_logger

logger = get_logger("GMAIL_CLIENT")

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar'
]


class GmailClient:
    def __init__(self):
        self.service = self.authenticate()

    def authenticate(self):
        creds = None

        # Load token if exists
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # Refresh or login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        logger.info("Gmail authentication successful")
        return build('gmail', 'v1', credentials=creds)

    def extract_body(self, payload):
        """Extract email body (handles multipart + plain text)"""
        body = ""

        try:
            # Multipart emails
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')

            # Single part emails
            data = payload.get('body', {}).get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        except Exception as e:
            logger.warning(f"Error extracting body: {e}")

        return body

    def get_messages(self, max_results=5):
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q="category:primary OR category:promotions"
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()

                payload = msg_data.get('payload', {})
                headers = payload.get('headers', [])

                subject = ""
                sender = ""

                for header in headers:
                    if header['name'] == 'Subject':
                        subject = header['value']
                    elif header['name'] == 'From':
                        sender = header['value']

                body = self.extract_body(payload)

                emails.append({
                    "id": msg['id'],
                    "subject": subject,
                    "sender": sender,
                    "body": body
                })

            logger.info(f"Fetched {len(emails)} emails")
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []