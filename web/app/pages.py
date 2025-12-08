from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .ml_client import get_recommendation

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/")
@login_required
def home():
    """Home page with project overview"""
    return render_template("home.html")

@pages_bp.route("/ingredients")
@login_required
def ingredients():
    """Page to manage user's available ingredients"""
    return render_template("ingredients.html")

def parse_ingredients(raw: str) -> list[str]:
    """Split a comma-separated string into a list of lowercased ingredients."""
    if not raw:
        return []
    return [item.strip().lower() for item in raw.split(",") if item.strip()]

@pages_bp.route("/recipe", methods=["GET", "POST"])
@login_required
def recipe():
    """
    Recipe results page.
    - GET: user came here directly -> show empty state.
    - POST: user submitted ingredients -> call ML client and show results.
    """
    if request.method == "POST":
        raw = request.form.get("ingredients", "")
        include = parse_ingredients(raw)

        if not include:
            flash("Please enter at least one ingredient.")
            return redirect(url_for("pages.ingredients"))

        # Later you can add cuisine / allergies / flavors here.
        payload = {
            "include": include,
            # "cuisine": request.form.get("cuisine") or "Generic",
            # "exclude": [...],
            # "taste": ...,
            # "diet": ...,
        }

        result = get_recommendation(payload) or {}
        best_recipes = result.get("best_recipes", [])
        other_suggestions = result.get("other_suggestions", [])

        # Show the first "best" recipe
        recipe_obj = best_recipes[0] if best_recipes else None

        return render_template(
            "recipe.html",
            include=include,
            recipe=recipe_obj,
            other_suggestions=other_suggestions,
        )

    # GET request: nothing submitted yet
    return render_template(
        "recipe.html",
        include=[],
        recipe=None,
        other_suggestions=[],
    )