import os
from flask import Blueprint, request, jsonify, session, current_app
from .ml_client import get_recommendation, replace_ingredient
from .db import insert_recipe, find_recipe_by_id

api_bp = Blueprint("api", __name__, url_prefix="/api")
@api_bp.route("/recommend", methods=["POST"])
def api_recommend():
    payload = request.json or {}
    # store user query (optional)
    # call ML client (placeholder)
    recipe = get_recommendation(payload)
    rid = insert_recipe(recipe)
    recipe["_id"] = str(rid)
    return jsonify({"recipe":recipe})

@api_bp.route("/replace", methods=["POST"])
def api_replace():
    data = request.json or {}
    recipe_id = data.get("recipe_id")
    frm = data.get("from")
    to = data.get("to")
    if not recipe_id or not frm or not to:
        return jsonify({"error":"need recipe_id/from/to"}), 400

    recipe = find_recipe_by_id(recipe_id)
    if not recipe:
        # possibly the client passed the whole recipe object
        recipe = data.get("recipe")
        if not recipe:
            return jsonify({"error":"recipe not found"}), 404

    new_recipe = replace_ingredient(recipe, frm, to)
    # if persisted, update persisted doc (simple behavior for in-memory)
    insert_recipe(new_recipe)
    return jsonify({"recipe": new_recipe})
