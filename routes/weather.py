"""Weather and smart suggestions API route."""
from flask import Blueprint, request, jsonify
from utils.weather_api import get_weather

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/api/weather", methods=["GET"])
def weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"success": False, "errors": ["City name is required"]}), 400
    if len(city) > 100:
        return jsonify({"success": False, "errors": ["City name too long"]}), 400

    data = get_weather(city)
    if "error" in data:
        return jsonify({"success": False, "errors": [data["error"]]}), 400
    data["success"] = True
    return jsonify(data)
