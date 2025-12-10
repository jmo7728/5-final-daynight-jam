# app/pages.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required
from ml_subsystem import get_recommendation

pages_bp = Blueprint("pages", __name__)


# ─────────────────────────────────────────────────────────────
# Shopping List Routes
# ─────────────────────────────────────────────────────────────

@pages_bp.route("/shopping-list")
@login_required
def shopping_list():
    """Shopping list page."""
    items = session.get("shopping_list", [])
    return render_template("shopping_list.html", items=items)


@pages_bp.route("/shopping-list/add", methods=["POST"])
@login_required
def add_to_shopping_list():
    """Add item(s) to shopping list."""
    data = request.json or {}
    items = data.get("items", [])
    
    if not items and data.get("item"):
        items = [data.get("item")]
    
    current_list = session.get("shopping_list", [])
    
    for item in items:
        item_clean = item.strip()
        if item_clean and item_clean not in [i["name"] for i in current_list]:
            current_list.append({
                "name": item_clean,
                "checked": False,
                "quantity": data.get("quantity", "")
            })
    
    session["shopping_list"] = current_list
    return jsonify({"success": True, "count": len(current_list)})


@pages_bp.route("/shopping-list/remove", methods=["POST"])
@login_required
def remove_from_shopping_list():
    """Remove item from shopping list."""
    data = request.json or {}
    item_name = data.get("item", "")
    
    current_list = session.get("shopping_list", [])
    current_list = [i for i in current_list if i["name"] != item_name]
    
    session["shopping_list"] = current_list
    return jsonify({"success": True, "count": len(current_list)})


@pages_bp.route("/shopping-list/toggle", methods=["POST"])
@login_required
def toggle_shopping_item():
    """Toggle item checked status."""
    data = request.json or {}
    item_name = data.get("item", "")
    
    current_list = session.get("shopping_list", [])
    for item in current_list:
        if item["name"] == item_name:
            item["checked"] = not item["checked"]
            break
    
    session["shopping_list"] = current_list
    return jsonify({"success": True})


@pages_bp.route("/shopping-list/clear", methods=["POST"])
@login_required
def clear_shopping_list():
    """Clear all items from shopping list."""
    session["shopping_list"] = []
    return jsonify({"success": True})


@pages_bp.route("/shopping-list/clear-checked", methods=["POST"])
@login_required
def clear_checked_items():
    """Clear only checked items from shopping list."""
    current_list = session.get("shopping_list", [])
    current_list = [i for i in current_list if not i["checked"]]
    session["shopping_list"] = current_list
    return jsonify({"success": True, "count": len(current_list)})


# ─────────────────────────────────────────────────────────────
# Main Pages
# ─────────────────────────────────────────────────────────────

@pages_bp.route("/")
@login_required
def home():
    """Main landing page after login."""
    return render_template("home.html")


@pages_bp.route("/ingredients")
@login_required
def ingredients():
    """Ingredients input / management page."""
    return render_template("ingredients.html")


def _parse_csv(raw: str) -> list[str]:
    """
    Helper: turn 'eggs, chicken' into ['eggs', 'chicken'].
    Lowercases and trims whitespace.
    """
    if not raw:
        return []
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


@pages_bp.route("/recipe", methods=["GET", "POST"])
@login_required
def recipe():
    """
    Recipe results page.

    - POST: user came from the ingredients page → call ML client
      with their ingredients and render a recipe.

    - GET: user opened /recipe directly → show "no recipe yet" state.
    """
    # POST: handle form submission from ingredients.html
    if request.method == "POST":
        raw_ingredients = request.form.get("ingredients", "")
        raw_tools = request.form.get("tools", "")
        raw_exclude = request.form.get("exclude", "")
        
        include = _parse_csv(raw_ingredients)
        tools = _parse_csv(raw_tools)
        exclude = _parse_csv(raw_exclude)

        if not include:
            flash("Please enter at least one ingredient.", "error")
            return redirect(url_for("pages.ingredients"))

        # Build payload for the ML client
        payload = {
            "include": include,
            "exclude": exclude,
            "tools": tools,
        }

        # Call ML client
        try:
            result = get_recommendation(payload) or {}
        except Exception as e:
            # Handle ML client errors
            flash(f"Could not get recommendation: {str(e)}", "error")
            return render_template(
                "recipe.html",
                include=include,
                tools=tools,
                exclude=exclude,
                recipe=None,
                other_suggestions=[],
            )

        # Two possible shapes of result:
        # 1) A dict with "best_recipes" and "other_suggestions"
        # 2) A single recipe dict
        recipe_obj = None
        other_suggestions = []

        if isinstance(result, dict) and "best_recipes" in result:
            best_recipes = result.get("best_recipes") or []
            recipe_obj = best_recipes[0] if best_recipes else None
            other_suggestions = result.get("other_suggestions") or []
        else:
            # Assume it's  a single recipe dict
            recipe_obj = result or None

        return render_template(
            "recipe.html",
            include=include,
            tools=tools,
            exclude=exclude,
            recipe=recipe_obj,
            other_suggestions=other_suggestions,
        )

    # GET: no POST data → no recipe yet
    return render_template(
        "recipe.html",
        include=[],
        tools=[],
        exclude=[],
        recipe=None,
        other_suggestions=[],
    )