import time
from app.main import run_email_agent

print("Worker started...")

while True:
    try:
        print("Running scheduled email check...")
        run_email_agent()
        print("Sleeping for 3 minutes...\n")
        time.sleep(180)  # 3 minutes

    except Exception as e:
        print(f"Worker error: {e}")
        time.sleep(60)