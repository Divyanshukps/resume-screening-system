cat > app.py <<'PY'
import os
import re

from flask import Flask, jsonify, render_template, request

from screener import extract_text, guess_candidate_name, rank_resumes
from screener.parser import ALLOWED_EXTENSIONS
from screener.preprocess import BACKEND

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify(
        status="ok",
        nlp_backend=BACKEND
    )


@app.post("/api/rank")
def rank():
    jd = request.form.get("job_description", "").strip()
    files = request.files.getlist("resumes")

    if not jd:
        return jsonify(error="Please provide a job description."), 400

    if not files or all(not f.filename for f in files):
        return jsonify(error="Please upload at least one resume."), 400

    resumes = []
    skipped = []

    for f in files:
        if not f.filename:
            continue

        ext = os.path.splitext(f.filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            skipped.append({
                "file": f.filename,
                "reason": "Unsupported file type"
            })
            continue

        try:
            text = extract_text(f.filename, f.read())

        except Exception as exc:
            skipped.append({
                "file": f.filename,
                "reason": f"Could not read file ({type(exc).__name__})"
            })
            continue

        if not text or not text.strip():
            skipped.append({
                "file": f.filename,
                "reason": "No readable text found"
            })
            continue

        resumes.append({
            "name": guess_candidate_name(text, f.filename),
            "filename": f.filename,
            "text": text
        })

    if not resumes:
        return jsonify(
            error="No readable resumes were found.",
            skipped=skipped
        ), 400

    ranking = rank_resumes(jd, resumes)

    return jsonify(
        count=len(ranking),
        ranking=ranking,
        skipped=skipped
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )
PY
