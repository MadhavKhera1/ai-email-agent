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

    def create_event(self, title, date, time):
        try:
            event = {
                'summary': title,
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