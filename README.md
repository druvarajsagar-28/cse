# EYE AI — Smart Vision Assistant

A beginner-friendly camera-based AI prototype for scanning images, extracting text, asking questions, and reading results aloud. This is **not** a real electronic contact lens.

## Features
- Capture an image using a webcam or upload PNG/JPG/JPEG/WEBP.
- Optional OCR text extraction with Tesseract.
- Optional AI image understanding and question answering through the OpenAI API.
- Browser text-to-speech.
- SQLite scan history with delete controls.
- Responsive dark-themed interface.

## Requirements
- Python 3.10 or newer
- A modern browser
- Internet connection and OpenAI API key for AI-powered answers (optional for starting the app)
- Tesseract OCR installed separately for OCR (optional)

## Run in VS Code

### 1. Open the project folder
Extract the ZIP and open the `eye_ai` folder in Visual Studio Code.

### 2. Create and activate a virtual environment

**Windows PowerShell**
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:
```bat
py -m venv .venv
.venv\\Scripts\\activate.bat
```

### 3. Install Python dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Configure AI (optional)
Copy `.env.example` to a new file named `.env` and add your API key:
```env
OPENAI_API_KEY=your_real_api_key
OPENAI_MODEL=gpt-4.1-mini
```
Keep `.env` private. Do not upload it to GitHub or share your API key.

Without an API key, the website and history work, but AI analysis and question answering display a setup message.

### 5. Install OCR (optional)
Install the Tesseract OCR engine for your operating system, then ensure the `tesseract` command is available on PATH. If Tesseract is not installed, the rest of the application still runs, but OCR text extraction will be blank.

### 6. Start the app
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your browser. Camera permissions normally work on localhost. Click **Start camera**, allow permission, then **Capture**, or upload an image.

## Project structure
```text
eye_ai/
├── app.py
├── backend/
│   ├── __init__.py
│   ├── ai_service.py
│   └── ocr_service.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── uploads/
├── instance/
├── .env.example
├── requirements.txt
└── README.md
```

## Privacy and safety
- The app analyzes an image only after you press **Analyze with AI**.
- When an API key is configured, images/questions are sent to the configured AI provider for processing.
- Scan results are stored in a local SQLite database until deleted.
- Do not scan or upload private documents without permission.
- This is a student prototype, not a medical or safety device.
- **Never put homemade electronics or a homemade lens in or on your eye.** Any real contact-lens research requires qualified biomedical, optics, and eye-safety professionals.

## Troubleshooting
- **Camera won't start:** Allow camera permission, use `http://127.0.0.1:5000`, or upload an image instead.
- **AI setup message:** Check that `.env` exists and contains a valid API key; restart the app after changes.
- **OCR is blank:** Install Tesseract OCR and check that it is on PATH.
- **Dependency install errors:** Upgrade pip using `python -m pip install --upgrade pip`.
