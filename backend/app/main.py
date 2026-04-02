from fastapi import FastAPI
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService

app = FastAPI()

gmail_service = GmailService()

ai_service = AIService()


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

@app.get("/ai-test")
def ai_test():
    subject = "Interview scheduled with ABC Company"
    body = "Your interview is scheduled on April 5 at 3 PM."

    result = ai_service.analyze_email(subject, body)

    return {"result": result}