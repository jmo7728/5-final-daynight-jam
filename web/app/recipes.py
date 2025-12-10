import requests
from flask import Blueprint, request, jsonify
from ...mongodb_subsystem.db import get_db

recipes_bp = Blueprint("recipes", __name__, url_prefix="/recipes")

ML_URL = "http://ml-service:8000/recommend"  


@recipes_bp.get("/recommend")
def recommend():
    ingredients = request.args.get("ingredients", "")
    cookware = request.args.get("cookware", "")
    allergies = request.args.get("allergies", "")
    flavor = request.args.get("flavor", "")

    payload = {
        "ingredients": ingredients.split(",") if ingredients else [],
        "cookware": cookware.split(",") if cookware else [],
        "allergies": allergies.split(",") if allergies else [],
        "flavor": flavor
    }

    try:
        ml_response = requests.post(ML_URL, json=payload, timeout=8)
        ml_data = ml_response.json()
    except Exception as e:
        return jsonify({"error": "ML service unreachable", "details": str(e)}), 503

    return jsonify({
        "input": payload,
        "recommendation": ml_data
    }), 200
