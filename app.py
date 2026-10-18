from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image
import os, io, sqlite3, datetime
from backend.ocr_service import extract_text
from backend.ai_service import analyze_image, answer_question

load_dotenv()
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
DB_PATH = os.path.join(app.root_path, "instance", "eye_ai.db")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")

def save_scan(kind, result):
    with db() as conn:
        conn.execute("INSERT INTO scans(kind, result, created_at) VALUES (?, ?, ?)",
                     (kind, result, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))

def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/scan", methods=["POST"])
def scan():
    if "image" not in request.files:
        return jsonify(error="Please choose or capture an image."), 400
    file = request.files["image"]
    if not file.filename or not allowed(file.filename):
        return jsonify(error="Upload a PNG, JPG, JPEG, or WEBP image."), 400
    try:
        raw = file.read()
        image = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        return jsonify(error="The uploaded file is not a valid image."), 400

    text = extract_text(image)
    question = request.form.get("question", "").strip()
    result = analyze_image(image, text, question)
    if text and not result:
        result = "Text detected:\n" + text
    if not result:
        result = "Image received. Configure an AI API key in .env for AI image descriptions. " + (
            "OCR text: " + text if text else "No readable text was detected."
        )
    save_scan("Image scan", result[:4000])
    return jsonify(result=result, extracted_text=text)

@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()
    if not question:
        return jsonify(error="Please enter a question."), 400
    answer = answer_question(question)
    save_scan("Question", f"Q: {question}\n\nA: {answer}")
    return jsonify(answer=answer)

@app.route("/api/history")
def history():
    with db() as conn:
        rows = conn.execute("SELECT id, kind, result, created_at FROM scans ORDER BY id DESC LIMIT 30").fetchall()
    return jsonify([dict(row) for row in rows])

@app.route("/api/history/<int:scan_id>", methods=["DELETE"])
def delete_history(scan_id):
    with db() as conn:
        conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    return jsonify(ok=True)

@app.route("/api/health")
def health():
    return jsonify(ok=True, app="EYE AI")

@app.errorhandler(413)
def too_large(_):
    return jsonify(error="Image is too large. Please use an image under 8 MB."), 413

init_db()
if __name__ == "__main__":
    app.run(debug=True)
