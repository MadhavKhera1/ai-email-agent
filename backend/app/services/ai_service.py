import os
import time
from dotenv import load_dotenv
from google import genai

from app.utils.logger import get_logger

load_dotenv()
logger = get_logger("AI_SERVICE")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PRIMARY_MODEL = "gemini-2.5-flash-lite"
FALLBACK_MODEL = "gemini-2.5-flash"
MAX_ATTEMPTS = 3


class AIService:
    def generate_with_model(self, model_name, prompt):
        last_error = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text

            except Exception as e:
                last_error = e
                logger.warning(f"{model_name} attempt {attempt} failed: {e}")

                if attempt < MAX_ATTEMPTS:
                    time.sleep(0.7 * attempt)

        raise last_error

    def analyze_email(self, subject, body):
        prompt = f"""
            Analyze the following email and extract structured information.

            Subject: {subject}
            Body: {body}

            Return ONLY valid JSON in this exact format (no extra text, no explanation):

            {{
            "type": "meeting" or "interview" or "other",
            "date": "YYYY-MM-DD or null",
            "time": "HH:MM or null",
            "title": "short summary",
            "confidence": number between 0 and 1
            }}
        """

        try:
            raw = self.generate_with_model(PRIMARY_MODEL, prompt)

            cleaned = raw.replace("```json", "").replace("```", "").strip()

            return cleaned

        except Exception as primary_error:
            logger.warning("Primary model failed, trying fallback...")

            try:
                raw = self.generate_with_model(FALLBACK_MODEL, prompt)

                cleaned = raw.replace("```json", "").replace("```", "").strip()

                return cleaned

            except Exception as fallback_error:
                logger.error(f"AI failed completely: {fallback_error}")
                return None
            
    def generate_reply(self, subject, body):
        prompt = f"""
        You are a professional assistant.

        Write a polite email reply for the following email.

        Keep it short and professional.

        Email Subject: {subject}
        Email Body: {body}

        Reply:
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return "Thank you for your email. I will get back to you soon."  