"""Yield Prediction API route."""
from flask import Blueprint, request, jsonify
import joblib
import numpy as np
from utils.preprocess import validate_yield_input, CROPS, CROP_INFO, CROP_EMOJIS
from utils.db import save_prediction

yield_bp = Blueprint("yield_pred", __name__)

_model = None
_scaler = None
_le = None

def _load():
    global _model, _scaler, _le
    if _model is None:
        _model  = joblib.load("models/yield_model.pkl")
        _scaler = joblib.load("models/yield_scaler.pkl")
        _le     = joblib.load("models/yield_label_encoder.pkl")


@yield_bp.route("/api/yield", methods=["POST"])
def predict_yield():
    data = request.get_json() or request.form.to_dict()
    inputs, errors = validate_yield_input(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    try:
        _load()
        crop_enc = _le.transform([inputs["crop"]])[0]
        feat = np.array([[crop_enc, inputs["area"], inputs["rainfall"],
                          inputs["temperature"], inputs["fertilizer"]]])
        feat_s = _scaler.transform(feat)
        y_pred = float(_model.predict(feat_s)[0])

        total_yield = round(y_pred * inputs["area"], 1)
        info = CROP_INFO.get(inputs["crop"], {})

        result = {
            "success": True,
            "crop": inputs["crop"],
            "emoji": CROP_EMOJIS.get(inputs["crop"], "🌱"),
            "yield_per_hectare": round(y_pred, 1),
            "total_yield": total_yield,
            "area": inputs["area"],
            "unit": "kg/hectare",
            "season": info.get("season", "—"),
            "inputs_summary": {
                "area":        f"{inputs['area']} hectares",
                "rainfall":    f"{inputs['rainfall']} mm",
                "temperature": f"{inputs['temperature']}°C",
                "fertilizer":  f"{inputs['fertilizer']} kg/ha",
            }
        }
        save_prediction("yield", inputs, {
            "yield_per_hectare": result["yield_per_hectare"],
            "total_yield": result["total_yield"]
        })
        return jsonify(result)

    except FileNotFoundError:
        return jsonify({
            "success": False,
            "errors": ["Model not trained yet. Please run: python train/train_yield.py"]
        }), 503
    except Exception as e:
        return jsonify({"success": False, "errors": [str(e)]}), 500


@yield_bp.route("/api/yield/crops", methods=["GET"])
def list_crops():
    return jsonify({"crops": CROPS})
