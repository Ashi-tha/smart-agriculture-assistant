"""
Smart Agriculture Assistant — Flask Entry Point
Run: python app.py
"""
import os
from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv

load_dotenv()

from utils.db import init_db
from routes.crop      import crop_bp
from routes.yield_pred import yield_bp
from routes.disease   import disease_bp
from routes.weather   import weather_bp
from routes.history   import history_bp

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max upload

# Register blueprints
app.register_blueprint(crop_bp)
app.register_blueprint(yield_bp)
app.register_blueprint(disease_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(history_bp)

# Initialize database
init_db()

# ── Page routes ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/crop")
def crop_page():
    return render_template("crop.html")

@app.route("/yield")
def yield_page():
    return render_template("yield.html")

@app.route("/disease")
def disease_page():
    return render_template("disease.html")

@app.route("/weather")
def weather_page():
    return render_template("weather.html")

@app.route("/history")
def history_page():
    return render_template("history.html")

# ── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404

@app.errorhandler(413)
def too_large(e):
    from flask import jsonify
    return jsonify({"success": False, "errors": ["File too large (max 5MB)"]}), 413


if __name__ == "__main__":
    print("🌾 Smart Agriculture Assistant starting...")
    print("📡 Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host="0.0.0.0", port=5000)
