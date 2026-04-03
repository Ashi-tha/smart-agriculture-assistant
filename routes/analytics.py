"""
Crop Health Analytics Route — AgriSense.
Integrates Image Quality Assessment and Health Classification.
"""
from flask import Blueprint, request, jsonify, render_template
import os
import uuid
from utils.analytics_engine import AnalyticsEngine
from utils.db import save_prediction

analytics_bp = Blueprint("analytics", __name__)
engine = AnalyticsEngine()

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@analytics_bp.route("/analytics")
def analytics():
    return render_template("analytics.html")

@analytics_bp.route("/api/analytics", methods=["POST"])
def analyze_crop():
    if "image" not in request.files:
        return jsonify({"success": False, "errors": ["No image file provided"]}), 400

    file = request.files["image"]
    crop_type = request.form.get("crop_type", "Other")
    growth_stage = request.form.get("growth_stage", "Unknown")
    
    if file.filename == "":
        return jsonify({"success": False, "errors": ["Empty filename"]}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        return jsonify({"success": False, "errors": ["Unsupported format. Use JPG, PNG, or WEBP."]}), 400

    image_bytes = file.read()
    
    # 1. Image Quality Assessment
    quality = engine.validate_quality(image_bytes)
    
    # 2. Health Classification
    health = engine.predict_health(image_bytes)
    
    # Save image for display
    fname = f"analytics_{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, fname)
    with open(save_path, "wb") as f:
        f.write(image_bytes)

    result = {
        "success": True,
        "quality": quality,
        "health": health,
        "crop_type": crop_type,
        "growth_stage": growth_stage,
        "image_url": f"/static/uploads/{fname}"
    }

    # Optional: Save to DB
    save_prediction("analytics", {"crop": crop_type, "stage": growth_stage}, {
        "health_status": health['status'],
        "confidence": health['confidence'],
        "quality_score": quality['metrics']['quality_score']
    })

    return jsonify(result)
