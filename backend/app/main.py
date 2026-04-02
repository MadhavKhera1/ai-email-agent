import json
from fastapi import FastAPI
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
from app.services.calendar_service import CalendarService


app = FastAPI()

gmail_service = GmailService()

ai_service = AIService()

calendar_service = CalendarService()


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

@app.get("/process-emails")
def process_emails():
    emails = gmail_service.fetch_emails()
    results=[]
    for email in emails:
        
        ai_raw = ai_service.analyze_email(
            email["subject"],
            email["body"]
        )

        try:
            ai_result = json.loads(ai_raw)
        except Exception as e:
            ai_result = {
                "error": "Invalid AI response",
                "details": str(e)
            }
        event_link = None

        if isinstance(ai_result, dict):
            if ai_result.get("type") in ["meeting", "interview"]:
                if ai_result.get("date") and ai_result.get("time"):
                    event_link = calendar_service.create_event(
                        ai_result["title"],
                        ai_result["date"],
                        ai_result["time"]
                    )

        results.append({
            "id":email["id"],
            "subject":email["subject"],
            "sender":email["sender"],
            "analysis":ai_result,
            "event_link":event_link
        })

    return{
        "processed":len(results),
        "results":results
    }
