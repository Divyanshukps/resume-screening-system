"""Flask app: web UI at / and REST API at /api/rank."""
from flask import Flask, jsonify, render_template, request

from screener import extract_text, guess_candidate_name, rank_resumes
from screener.parser import ALLOWED_EXTENSIONS
from screener.preprocess import BACKEND

import os

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB per request


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify(status="ok", nlp_backend=BACKEND)


@app.post("/api/rank")
def rank():
    """
    multipart/form-data
      job_description : text
      resumes         : one or more files (.pdf, .docx, .txt)
    """
    jd = request.form.get("job_description", "").strip()
    files = request.files.getlist("resumes")

    if not jd:
        return jsonify(error="Please provide a job description."), 400
    if not files or all(f.filename == "" for f in files):
        return jsonify(error="Please upload at least one resume."), 400

    resumes, skipped = [], []
    for f in files:
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            skipped.append({"file": f.filename, "reason": "unsupported file type"})
            continue
        try:
            text = extract_text(f.filename, f.read())
        except Exception as exc:  # corrupt / password-protected file
            skipped.append({"file": f.filename, "reason": f"could not read ({exc.__class__.__name__})"})
            continue
        if not text.strip():
            skipped.append({"file": f.filename, "reason": "no readable text (scanned image?)"})
            continue
        resumes.append(
            {"name": guess_candidate_name(text, f.filename), "filename": f.filename, "text": text}
        )

    if not resumes:
        return jsonify(error="No readable resumes were found.", skipped=skipped), 400

    ranking = rank_resumes(jd, resumes)
    return jsonify(count=len(ranking), ranking=ranking, skipped=skipped)


if __name__ == "__main__":
    # Local / Codespaces: python app.py   (set FLASK_DEBUG=1 for auto-reload)
    # Production (Docker / Hugging Face) uses gunicorn instead, see Dockerfile.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
