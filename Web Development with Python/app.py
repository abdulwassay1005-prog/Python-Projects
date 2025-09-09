from flask import Flask, render_template, request, redirect, url_for, flash
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# -----------------------------
# Site Content (Edit to update)
# -----------------------------
PROFILE = {
    "name": "Abdul Wassay",
    "tagline": "WordPress Developer · Junior Python Developer · Operations Manager @ Skills4U",
    "bio": "I build responsive, fast WordPress sites and dabble in Python. Currently Operations Manager at Skills4U.",
    "location": "Peshawar, Pakistan",
    "email": "abdulwassay1005@gmail.com",
    "phone": "0328-5658709",
    "linkedin": "https://www.linkedin.com/in/abdul-wassay-5794a924a",
    "resume_url": "#",  # put a link to your PDF resume here if you have one
    "skills_tech": ["WordPress", "Python (basic)", "Prompt Engineering"],
    "skills_soft": ["Time Management", "Strong Communication", "Confidence", "Effective Multi‑tasking"],
    "education": [
        {"title": "BSCS (Unofficially graduated)", "org": "CECOS University", "years": "2021–2025"},
    ],
    "certifications": [
        {"title": "Introduction to Programming Using Python", "org": "CECOS University", "date": "Nov 2024"},
    ],
    "languages": ["Urdu (fluent)", "English (fluent)"]
}

PROJECTS = [
    {
        "title": "Real‑Time Peach Disease Detection & Diagnosis",
        "description": "A deep‑learning app using YOLO and CNNs to detect diseases on peach plants and suggest treatments.",
        "tags": ["Computer Vision", "YOLO", "TensorFlow"],
        "link": "#"
    },
    {
        "title": "Skills4U Website",
        "description": "A responsive, speed‑optimized WordPress site for Skills4U with custom pages and analytics.",
        "tags": ["WordPress", "SEO", "Performance"],
        "link": "#"
    }
]

NAV = [
    {"title": "Home", "endpoint": "home"},
    {"title": "Projects", "endpoint": "projects"},
    {"title": "About", "endpoint": "about"},
    {"title": "Contact", "endpoint": "contact"},
]

# Ensure data directory exists for contact messages
os.makedirs("data", exist_ok=True)
MESSAGES_JSON = os.path.join("data", "messages.json")
if not os.path.exists(MESSAGES_JSON):
    with open(MESSAGES_JSON, "w", encoding="utf-8") as f:
        json.dump([], f)

# -----------------------------
# Routes
# -----------------------------
@app.context_processor
def inject_globals():
    return {"PROFILE": PROFILE, "NAV": NAV}

@app.route("/")
def home():
    return render_template("index.html", projects=PROJECTS[:3])

@app.route("/projects")
def projects():
    return render_template("projects.html", projects=PROJECTS)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("contact"))
        entry = {
            "name": name,
            "email": email,
            "message": message,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
        # Append to JSON file
        try:
            with open(MESSAGES_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            data.append(entry)
            with open(MESSAGES_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            flash("Thanks! Your message was sent.", "success")
        except Exception as e:
            flash(f"Couldn't save your message: {e}", "danger")
        return redirect(url_for("contact"))
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)