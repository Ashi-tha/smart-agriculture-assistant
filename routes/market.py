"""Market Data and Profitability Route."""
from flask import Blueprint, request, jsonify, render_template
from utils.market_api import get_market_data

market_bp = Blueprint("market", __name__)


@market_bp.route("/market", methods=["GET"])
def market_page():
    return render_template("market.html")


@market_bp.route("/api/market", methods=["POST"])
def market_api():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "errors": ["Invalid JSON"]}), 400

    crop = data.get("crop", "").strip()
    state = data.get("state", "").strip()

    if not crop:
        return jsonify({"success": False, "errors": ["Crop type is required"]}), 400
    if not state:
        return jsonify({"success": False, "errors": ["State is required"]}), 400

    result = get_market_data(crop, state)
    if "error" in result:
        return jsonify({"success": False, "errors": [result["error"]]}), 400

    return jsonify(result)
