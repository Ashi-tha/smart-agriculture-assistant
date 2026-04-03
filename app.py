"""
Smart Agriculture Assistant — Flask Entry Point
Run: python app.py
"""
import os
from flask import Flask, render_template, send_from_directory, session, request, redirect, url_for, jsonify
from dotenv import load_dotenv

load_dotenv()

from utils.db import init_db, get_user_by_id
from routes.crop      import crop_bp
from routes.yield_pred import yield_bp
from routes.disease   import disease_bp
from routes.weather   import weather_bp
from routes.history   import history_bp
from routes.market    import market_bp
from routes.analytics import analytics_bp
from routes.auth      import auth_bp

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max upload
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# Register blueprints
app.register_blueprint(crop_bp)
app.register_blueprint(yield_bp)
app.register_blueprint(disease_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(history_bp)
app.register_blueprint(market_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(auth_bp)


# Initialize database
init_db()

_PUBLIC_PATHS = frozenset({"/login", "/register"})


@app.before_request
def require_login():
    if request.path.startswith("/static"):
        return None
    if request.path in _PUBLIC_PATHS:
        return None
    if session.get("user_id"):
        return None
    if request.path.startswith("/api/"):
        return jsonify(
            {"success": False, "errors": ["Authentication required. Please sign in."]}
        ), 401
    return redirect(url_for("auth.login", next=request.path))


@app.context_processor
def inject_current_user():
    try:
        uid = session.get("user_id")
        if not uid:
            return {"current_user": None}
        user = get_user_by_id(uid)
        if not user:
            session.clear()
            return {"current_user": None}
        return {"current_user": user}
    except Exception:
        return {"current_user": None}

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


def _find_free_port(start: int = 5000, attempts: int = 20) -> int:
    """Pick a free TCP port (avoids 'Address already in use' when 5000 is busy)."""
    import socket

    for port in range(start, start + attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
            return port
        except OSError:
            continue
    return start


if __name__ == "__main__":
    preferred = int(os.environ.get("PORT", "5000"))
    port = _find_free_port(preferred)
    if port != preferred:
        print(f"Note: port {preferred} was busy; using {port} instead.")
    print("Smart Agriculture Assistant starting...")
    print(f"Open http://127.0.0.1:{port} in your browser")
    # Disable watchdog reloader to avoid repeated restarts on some Windows setups.
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=port)
