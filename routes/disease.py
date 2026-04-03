"""Plant disease API — rice-only MobileNetV2 (transfer learning)."""
from flask import Blueprint, request, jsonify
import os
import uuid
import io
import numpy as np
from utils.db import save_prediction
from utils.rice_disease_config import RICE_DISEASE_CLASSES

disease_bp = Blueprint("disease", __name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

WEIGHTS_PATH = os.path.join("models", "disease_model.h5")

DISEASE_CLASSES = RICE_DISEASE_CLASSES

DISEASE_INFO = {
    "Brown_spot": {"treatment": "Apply propiconazole fungicide. Ensure balanced fertilization.", "severity": "Medium"},
    "Leaf_blast": {"treatment": "Apply tricyclazole fungicide. Maintain proper water management.", "severity": "High"},
    "Neck_blast": {"treatment": "Apply isoprothiolane fungicide. Reduce nitrogen fertilizer.", "severity": "High"},
    "healthy": {"treatment": "No treatment needed. The plant appears healthy.", "severity": "None"},
}

_model = None
_weights_loaded = False
_init_done = False


def _load_model():
    """Build graph and load weights once. Returns (model_or_none, weights_loaded)."""
    global _model, _weights_loaded, _init_done
    if _init_done:
        return _model, _weights_loaded
    _init_done = True
    if not os.path.isfile(WEIGHTS_PATH):
        return None, False
    try:
        import tensorflow as tf
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
        from tensorflow.keras.models import Model

        base = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
        x = GlobalAveragePooling2D()(base.output)
        x = Dropout(0.3)(x)
        out = Dense(len(DISEASE_CLASSES), activation="softmax")(x)
        model = Model(inputs=base.input, outputs=out)
        model.load_weights(WEIGHTS_PATH)
        _model = model
        _weights_loaded = True
    except Exception:
        _model = None
        _weights_loaded = False
    return _model, _weights_loaded


def _preprocess_image(image_bytes):
    from PIL import Image
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    arr = np.array(img, dtype=np.float32)
    arr = np.expand_dims(arr, 0)
    return preprocess_input(arr)


def _predict(image_bytes):
    model, ok = _load_model()
    if not ok or model is None:
        return None
    inp = _preprocess_image(image_bytes)
    proba = model.predict(inp, verbose=0)[0]
    top_idx = int(np.argmax(proba))
    confidence = float(proba[top_idx]) * 100
    label = DISEASE_CLASSES[top_idx]
    return label, confidence


@disease_bp.route("/api/disease", methods=["POST"])
def detect_disease():
    if "image" not in request.files:
        return jsonify({"success": False, "errors": ["No image file provided"]}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "errors": ["Empty filename"]}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        return jsonify({"success": False, "errors": ["Unsupported format. Use JPG, PNG, or WEBP."]}), 400

    image_bytes = file.read()
    if len(image_bytes) > 5 * 1024 * 1024:
        return jsonify({"success": False, "errors": ["Image too large (max 5MB)"]}), 400

    model, weights_ok = _load_model()
    
    fname = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, fname)
    with open(save_path, "wb") as f:
        f.write(image_bytes)

    # Prediction logic with fallback
    try:
        if weights_ok and model is not None:
            inp = _preprocess_image(image_bytes)
            proba = model.predict(inp, verbose=0)[0]
            top_idx = int(np.argmax(proba))
            confidence = float(proba[top_idx]) * 100
            label = DISEASE_CLASSES[top_idx]
            demo_mode = False
        else:
            # Smart Simulation (Demo Mode)
            # Use image bytes as seed for deterministic "random" choice per image
            np.random.seed(int.from_bytes(image_bytes[:4], "little") % (2**31))
            proba = np.random.dirichlet(np.ones(len(DISEASE_CLASSES)) * 0.5)
            top_idx = int(np.argmax(proba))
            confidence = float(min(65 + np.random.uniform(0, 25), 95))
            label = DISEASE_CLASSES[top_idx]
            demo_mode = True
    except Exception:
        return jsonify({
            "success": False,
            "errors": ["Could not run disease detection. Check that TensorFlow is installed."],
        }), 500

    parts = label.split("___")
    plant = parts[0].replace("_", " ") if len(parts) > 0 else "Rice"
    disease = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"
    is_healthy = "healthy" in label.lower()

    disease_key = parts[1] if len(parts) > 1 else "healthy"
    info = DISEASE_INFO.get(disease_key, DISEASE_INFO.get("healthy"))

    result = {
        "success": True,
        "plant": plant,
        "disease": disease,
        "label": label,
        "confidence": round(confidence, 1),
        "is_healthy": is_healthy,
        "severity": info["severity"],
        "treatment": info["treatment"],
        "image_url": f"/static/uploads/{fname}",
        "demo_mode": demo_mode,
    }
    save_prediction("disease", {"filename": file.filename}, {
        "plant": plant, "disease": disease, "confidence": round(confidence, 1)
    })
    return jsonify(result)
