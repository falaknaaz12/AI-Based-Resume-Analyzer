"""
app.py
AI-Based Resume Analyzer - Main Flask Application

Run with:
    python app.py

Then open http://127.0.0.1:5000 in your browser.
"""

import os
import uuid
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
from werkzeug.utils import secure_filename

from utils.parser import extract_text, allowed_file
from utils.extractor import parse_resume
from utils.analyzer import analyze_resume
from utils.matcher import match_resume_to_job, compute_final_ats_score

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.secret_key = "resume-analyzer-secret-key-change-in-production"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory store for the most recent analysis result per session.
# (Simple approach suitable for a college project / single-user demo.
#  For production/multi-user use, replace with a database.)
ANALYSIS_STORE = {}


@app.route("/")
def home():
    """Landing / home page describing the application."""
    return render_template("index.html")


@app.route("/about")
def about():
    """About page describing the project."""
    return render_template("about.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Upload page: accepts a resume file and an optional job description."""
    if request.method == "GET":
        return render_template("upload.html")

    # --- POST: handle file upload ---
    if "resume" not in request.files:
        flash("No file part in the request. Please choose a file.", "danger")
        return redirect(url_for("upload"))

    file = request.files["resume"]

    if file.filename == "":
        flash("No file selected. Please choose a PDF or DOCX resume.", "danger")
        return redirect(url_for("upload"))

    if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
        flash("Invalid file type. Only PDF and DOCX files are supported.", "danger")
        return redirect(url_for("upload"))

    # Save file with a unique name to avoid collisions
    original_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{original_name}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(file_path)

    job_description = request.form.get("job_description", "").strip()

    try:
        raw_text = extract_text(file_path)

        if not raw_text or len(raw_text.split()) < 10:
            flash(
                "Could not extract enough text from this file. Please make "
                "sure the resume is not a scanned image and try again.",
                "danger",
            )
            return redirect(url_for("upload"))

        resume_data = parse_resume(raw_text)
        analysis = analyze_resume(resume_data)

        job_match_result = None
        if job_description and len(job_description.split()) >= 5:
            job_match_result = match_resume_to_job(resume_data, job_description)

        final_score, score_breakdown, score_explanation = compute_final_ats_score(
            analysis["base_ats_score"], analysis["score_breakdown"], job_match_result
        )

        result_id = uuid.uuid4().hex
        ANALYSIS_STORE[result_id] = {
            "original_filename": original_name,
            "analyzed_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "resume_data": resume_data,
            "analysis": analysis,
            "job_match_result": job_match_result,
            "final_score": final_score,
            "score_breakdown": score_breakdown,
            "score_explanation": score_explanation,
            "had_job_description": bool(job_match_result),
        }
        session["last_result_id"] = result_id

    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("upload"))
    except Exception as exc:  # noqa: BLE001 - surface unexpected errors to user
        flash(f"An unexpected error occurred while analyzing your resume: {exc}", "danger")
        return redirect(url_for("upload"))
    finally:
        # Clean up the uploaded file from disk after processing
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

    return redirect(url_for("result", result_id=result_id))


@app.route("/result/<result_id>")
def result(result_id):
    """Analysis result / dashboard page."""
    data = ANALYSIS_STORE.get(result_id)
    if not data:
        flash("This analysis result was not found or has expired. Please upload again.", "warning")
        return redirect(url_for("upload"))

    return render_template("result.html", result_id=result_id, **data)


@app.errorhandler(413)
def file_too_large(_error):
    flash("File is too large. Please upload a file smaller than 8 MB.", "danger")
    return redirect(url_for("upload"))


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("index.html"), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
