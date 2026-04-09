import json
from fastapi import FastAPI
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
from app.services.calendar_service import CalendarService
from app.core.db import init_db
from app.utils.db_helper import is_email_processed, mark_email_processed
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Request
from app.services.telegram_service import send_telegram_message
from app.utils.db_helper import save_log

gmail_service = GmailService()

ai_service = AIService()

calendar_service = CalendarService()

init_db()

scheduler = BackgroundScheduler()

def start_scheduler():
    def safe_run():
        try:
            run_email_agent()
        except Exception as e:
            print(f"Scheduler error: {e}")

    scheduler.add_job(safe_run, "interval", minutes=3)
    scheduler.start()

def get_logs_from_db():
    from app.core.db import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT email_id, subject, type, confidence, action, created_at
        FROM logs
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    logs = []
    for row in rows:
        logs.append({
            "email_id": row[0],
            "subject": row[1],
            "type": row[2],
            "confidence": row[3],
            "action": row[4],
            "created_at": row[5]
        })

    return logs

@asynccontextmanager
async def lifespan(app):
    print("Starting scheduler...")
    start_scheduler()
    yield
    print("Shutting down scheduler...")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

def run_email_agent():
    print("Running scheduled email check...")

    emails = gmail_service.fetch_emails()

    for email in emails:

        if is_email_processed(email["id"]):
            continue

        mark_email_processed(email["id"])

        ai_raw = ai_service.analyze_email(
            email["subject"],
            email["body"]
        )

        try:
            ai_result = json.loads(ai_raw)
        except Exception:
            continue

        if isinstance(ai_result, dict):
            confidence = ai_result.get("confidence", 1)  # fallback safe
            if ai_result.get("type") in ["meeting", "interview"] and confidence >= 0.7:
                if ai_result.get("date") and ai_result.get("time"):
                    calendar_service.create_event(
                        ai_result["title"],
                        ai_result["date"],
                        ai_result["time"],
                        email["id"]
                    )

                    send_telegram_message(
                        f"📅 {ai_result['type'].capitalize()} Scheduled!\n"
                        f"Title: {ai_result['title']}\n"
                        f"Date: {ai_result['date']}\n"
                        f"Time: {ai_result['time']}\n"
                        f"Confidence: {confidence}"
                    )

                    save_log(
                        email["id"],
                        email["subject"],
                        ai_result.get("type"),
                        confidence,
                        "scheduled"
                    )

                    # Generate reply
                    reply_text = ai_service.generate_reply(
                        email["subject"],
                        email["body"],
                        ai_result.get("type")
                    )

                    # Create Gmail draft
                    if reply_text:
                        gmail_service.create_draft(
                            email["sender"],
                            email["subject"],
                            reply_text
                        )

                else:
                    # Missing date/time → skip
                    save_log(
                        email["id"],
                        email["subject"],
                        ai_result.get("type"),
                        confidence,
                        "skipped_missing_data"
                    )
            else:
                # Missing date/time → skip
                save_log(
                    email["id"],
                    email["subject"],
                    ai_result.get("type"),
                    confidence,
                    "skipped"
                )

@app.api_route("/", methods=["GET", "HEAD"])
def root(request: Request):
    return {"message": "AI Email Agent Running"}


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

        #skipping already processed mails
        if is_email_processed(email["id"]):
            continue

        #storing email id after processing
        mark_email_processed(email["id"])
        
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

@app.get("/logs")
def get_logs():
    return {
        "count": len(get_logs_from_db()),
        "logs": get_logs_from_db()
    }