"""Optional OpenAI integration. The app still runs without an API key."""
import os
import base64
import io

def _client():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=key)
    except Exception:
        return None

def analyze_image(image, extracted_text="", question=""):
    client = _client()
    if not client:
        return ""
    try:
        from PIL import Image
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        prompt = (
            "Describe the image accurately in simple English. Identify visible objects and "
            "read/ explain any visible text. If a question is included, answer it carefully. "
            "If uncertain, say so. Do not guess private or sensitive details.\n"
            f"User question: {question or 'Describe this image.'}\n"
            f"OCR text (may contain errors): {extracted_text[:3000]}"
        )
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=[{"role": "user", "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{encoded}"}
            ]}]
        )
        return response.output_text.strip()
    except Exception as exc:
        return f"AI analysis failed: {exc}. Check your API key, model access, and internet connection."

def answer_question(question):
    client = _client()
    if not client:
        return ("AI answering is not configured yet. Add your OPENAI_API_KEY to the .env file "
                "and restart the app. Your question was: " + question)
    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input="Answer this question in simple English. Show steps for maths when relevant. "
                  "If unsure, state the limitation.\n\nQuestion: " + question
        )
        return response.output_text.strip()
    except Exception as exc:
        return f"AI answer failed: {exc}. Check your API key, model access, and internet connection."
