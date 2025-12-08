from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@login_required
def home():
    """Main landing page after login."""
    return render_template("home.html")

@main_bp.route("/home")
@login_required
def home_redirect():
    """Optional /home route that just redirects to /."""
    return redirect(url_for("main.home"))

@main_bp.route("/ingredients")
@login_required
def ingredients():
    """Page where the user manages / enters their ingredients."""
    return render_template("ingredients.html")

@main_bp.route("/recipe")
@login_required
def recipe():
    """Recipe results page (for now just renders template)."""
    return render_template("recipe.html")

@main_bp.route("/result")
@login_required
def result_page():
    """
    Result page – expects ?recipe_id=<id> in the query string.
    If DB helpers are not implemented yet, this will just render
    the template with recipe=None.
    """
    recipe_id = request.args.get("recipe_id")
    recipe = None

    if recipe_id:
        try:
            # If you later implement find_recipe_by_id in db.py,
            # this will start working without changing this route.
            from .db import find_recipe_by_id
            recipe = find_recipe_by_id(recipe_id)
        except ImportError:
            # DB helpers not implemented yet
            recipe = None

    return render_template("result.html", recipe=recipe)
