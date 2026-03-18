"""Crop Recommendation API route."""
from flask import Blueprint, request, jsonify
import joblib
import numpy as np
import os
from utils.preprocess import validate_crop_input, CROP_EMOJIS, CROP_INFO, CROPS
from utils.db import save_prediction

crop_bp = Blueprint("crop", __name__)

# Load model lazy (only once)
_model = None
_scaler = None

def _load():
    global _model, _scaler
    if _model is None:
        _model  = joblib.load("models/crop_model.pkl")
        _scaler = joblib.load("models/crop_scaler.pkl")

@crop_bp.route("/api/crop", methods=["POST"])
def recommend_crop():
    data = request.get_json() or request.form.to_dict()
    inputs, errors = validate_crop_input(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    try:
        _load()
        feat = np.array([[
            inputs["N"], inputs["P"], inputs["K"],
            inputs["temperature"], inputs["humidity"],
            inputs["ph"], inputs["rainfall"]
        ]])
        feat_s = _scaler.transform(feat)

        # Get probabilities for all classes
        proba = _model.predict_proba(feat_s)[0]
        classes = _model.classes_

        # Top 3 crops sorted by confidence
        top3_idx = np.argsort(proba)[::-1][:3]
        recommendations = []
        for idx in top3_idx:
            crop = classes[idx]
            info = CROP_INFO.get(crop, {})
            recommendations.append({
                "crop":        crop,
                "confidence":  round(float(proba[idx]) * 100, 1),
                "emoji":       CROP_EMOJIS.get(crop, "🌱"),
                "season":      info.get("season", "—"),
                "water_need":  info.get("water", "—"),
                "soil_type":   info.get("soil", "—"),
            })

        result = {
            "success":         True,
            "recommendations": recommendations,
            "best_crop":       recommendations[0]["crop"],
            "reasoning": {
                "N":           f"Nitrogen: {inputs['N']} kg/ha",
                "P":           f"Phosphorus: {inputs['P']} kg/ha",
                "K":           f"Potassium: {inputs['K']} kg/ha",
                "temperature": f"Temperature: {inputs['temperature']}°C",
                "humidity":    f"Humidity: {inputs['humidity']}%",
                "ph":          f"Soil pH: {inputs['ph']}",
                "rainfall":    f"Rainfall: {inputs['rainfall']} mm",
            }
        }
        save_prediction("crop", inputs, {"best_crop": result["best_crop"],
                                         "top3": [r["crop"] for r in recommendations]})
        return jsonify(result)

    except FileNotFoundError:
        return jsonify({
            "success": False,
            "errors": ["Model not trained yet. Please run: python train/train_crop.py"]
        }), 503
    except Exception as e:
        return jsonify({"success": False, "errors": [str(e)]}), 500


@crop_bp.route("/api/crop/crops", methods=["GET"])
def list_crops():
    return jsonify({"crops": CROPS})
