"""OCR helper. Tesseract is optional; without it the app continues without OCR."""
import pytesseract

def extract_text(image):
    try:
        return pytesseract.image_to_string(image).strip()
    except Exception:
        return ""
