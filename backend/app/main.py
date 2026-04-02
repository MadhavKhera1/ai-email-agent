from fastapi import FastAPI
from app.services.gmail_service import GmailService

app = FastAPI()

gmail_service = GmailService()


@app.get("/")
def root():
    return {"message": "AI Email Agent Running 🚀"}


@app.get("/emails")
def get_emails():
    emails = gmail_service.fetch_emails()

    return {
        "count": len(emails),
        "emails": emails
    }