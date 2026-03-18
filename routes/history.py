"""Prediction history API route."""
from flask import Blueprint, request, jsonify
from utils.db import get_history, delete_prediction

history_bp = Blueprint("history", __name__)


@history_bp.route("/api/history", methods=["GET"])
def get_predictions():
    limit = min(int(request.args.get("limit", 50)), 200)
    records = get_history(limit)
    return jsonify({"success": True, "count": len(records), "records": records})


@history_bp.route("/api/history/<int:pred_id>", methods=["DELETE"])
def delete_record(pred_id):
    delete_prediction(pred_id)
    return jsonify({"success": True, "deleted_id": pred_id})
