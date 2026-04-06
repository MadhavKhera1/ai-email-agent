from googleapiclient.discovery import build
from app.services.gmail_client import GmailClient
from app.utils.logger import get_logger

logger = get_logger("CALENDAR_SERVICE")


class CalendarService:
    def __init__(self):
        # reuse authentication
        self.gmail_client = GmailClient()
        self.service = build(
            'calendar',
            'v3',
            credentials=self.gmail_client.service._http.credentials
        )

    def create_event(self, title, date, time, email_id):
        try:
            #Step 1: Check if event already exists
            existing_events = self.service.events().list(
                calendarId='primary',
                q=email_id
            ).execute()

            if existing_events.get("items"):
                logger.info(f"Event already exists for email_id: {email_id}, skipping...")
                return None

            #Step 2: Create event
            event = {
                'summary': title,
                "description": f"Created by AI Agent | Email ID: {email_id}",
                'start': {
                    'dateTime': f"{date}T{time}:00+05:30",
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': f"{date}T{time}:00+05:30",
                    'timeZone': 'Asia/Kolkata',
                },
            }

            event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            logger.info(f"Event created: {event.get('htmlLink')}")
            return event.get('htmlLink')

        except Exception as e:
            logger.error(f"Calendar error: {e}")
            return None