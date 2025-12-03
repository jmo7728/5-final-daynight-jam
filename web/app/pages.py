from flask import Blueprint, render_template
from flask_login import login_required

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/")
@login_required
def home():
    return render_template("home.html")

@pages_bp.route("/recipe")
@login_required
def recipe():
    return render_template("recipe.html")
