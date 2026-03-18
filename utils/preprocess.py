"""Shared preprocessing utilities."""
import numpy as np

CROPS = [
    "rice", "maize", "chickpea", "kidneybeans", "pigeonpeas",
    "mothbeans", "mungbean", "blackgram", "lentil", "pomegranate",
    "banana", "mango", "grapes", "watermelon", "muskmelon",
    "apple", "orange", "papaya", "coconut", "cotton", "jute", "coffee"
]

CROP_EMOJIS = {
    "rice": "🌾", "maize": "🌽", "chickpea": "🫘", "kidneybeans": "🫘",
    "pigeonpeas": "🫘", "mothbeans": "🫘", "mungbean": "🫘", "blackgram": "🫘",
    "lentil": "🫘", "pomegranate": "🍎", "banana": "🍌", "mango": "🥭",
    "grapes": "🍇", "watermelon": "🍉", "muskmelon": "🍈", "apple": "🍎",
    "orange": "🍊", "papaya": "🥭", "coconut": "🥥", "cotton": "🌿",
    "jute": "🌿", "coffee": "☕"
}

CROP_INFO = {
    "rice":        {"season": "Kharif", "water": "High", "soil": "Clayey loam"},
    "maize":       {"season": "Kharif/Rabi", "water": "Medium", "soil": "Well-drained loam"},
    "chickpea":    {"season": "Rabi", "water": "Low", "soil": "Sandy loam"},
    "kidneybeans": {"season": "Kharif", "water": "Medium", "soil": "Loamy"},
    "pigeonpeas":  {"season": "Kharif", "water": "Low-Medium", "soil": "Deep black"},
    "mothbeans":   {"season": "Kharif", "water": "Very Low", "soil": "Sandy"},
    "mungbean":    {"season": "Kharif/Zaid", "water": "Low", "soil": "Loamy sand"},
    "blackgram":   {"season": "Kharif", "water": "Low-Medium", "soil": "Loam"},
    "lentil":      {"season": "Rabi", "water": "Low", "soil": "Sandy loam"},
    "pomegranate": {"season": "Perennial", "water": "Low", "soil": "Well-drained"},
    "banana":      {"season": "Perennial", "water": "High", "soil": "Rich loam"},
    "mango":       {"season": "Perennial", "water": "Low-Medium", "soil": "Deep alluvial"},
    "grapes":      {"season": "Perennial", "water": "Medium", "soil": "Sandy loam"},
    "watermelon":  {"season": "Zaid/Summer", "water": "Medium", "soil": "Sandy loam"},
    "muskmelon":   {"season": "Summer", "water": "Medium", "soil": "Sandy loam"},
    "apple":       {"season": "Perennial", "water": "Medium", "soil": "Well-drained loam"},
    "orange":      {"season": "Perennial", "water": "Medium", "soil": "Alluvial"},
    "papaya":      {"season": "Perennial", "water": "Medium", "soil": "Rich loam"},
    "coconut":     {"season": "Perennial", "water": "High", "soil": "Laterite/loam"},
    "cotton":      {"season": "Kharif", "water": "Medium", "soil": "Black cotton"},
    "jute":        {"season": "Kharif", "water": "High", "soil": "Alluvial"},
    "coffee":      {"season": "Perennial", "water": "Medium", "soil": "Red laterite"},
}


def validate_crop_input(data):
    """Validate and extract crop recommendation inputs."""
    errors = []
    fields = {
        "N": (0, 150), "P": (0, 150), "K": (0, 210),
        "temperature": (0, 50), "humidity": (0, 100),
        "ph": (0, 14), "rainfall": (0, 400)
    }
    result = {}
    for field, (lo, hi) in fields.items():
        val = data.get(field)
        try:
            val = float(val)
            if not (lo <= val <= hi):
                errors.append(f"{field} must be between {lo} and {hi}")
            result[field] = val
        except (TypeError, ValueError):
            errors.append(f"{field} is required and must be a number")
    return result, errors


def validate_yield_input(data):
    """Validate and extract yield prediction inputs."""
    errors = []
    result = {}
    crop = data.get("crop", "").lower().strip()
    if crop not in CROPS:
        errors.append(f"Unknown crop: {crop}")
    result["crop"] = crop

    num_fields = {
        "area": (0.1, 1000),
        "rainfall": (0, 500),
        "temperature": (0, 50),
        "fertilizer": (0, 500),
    }
    for field, (lo, hi) in num_fields.items():
        val = data.get(field)
        try:
            val = float(val)
            if not (lo <= val <= hi):
                errors.append(f"{field} must be between {lo} and {hi}")
            result[field] = val
        except (TypeError, ValueError):
            errors.append(f"{field} is required and must be a number")
    return result, errors
