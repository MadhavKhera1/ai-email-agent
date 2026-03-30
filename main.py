from accounts.gmail_client import GmailClient
from utils.logger import get_logger

logger = get_logger("MAIN")

def main():
    logger.info("Starting Gmail test...")

    gmail = GmailClient()
    emails = gmail.get_messages()

    for email in emails:
        print("\n--- EMAIL ---")
        print(f"From: {email['sender']}")
        print(f"Subject: {email['subject']}")

if __name__ == "__main__":
    main()