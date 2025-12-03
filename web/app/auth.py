from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from .db import users_collection

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

class User(UserMixin):
    def __init__(self, user_dict):
        self.id = str(user_dict["_id"])
        self.username = user_dict["username"]
        self.password_hash = user_dict["password"]

@login_manager.user_loader
def load_user(user_id):
    user_dict = users_collection.find_one({"_id": user_id})
    if user_dict:
        return User(user_dict)
    return None

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users_collection.find_one({"username": username}):
            flash("Username already exists")
            return redirect(url_for("auth.register"))
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        users_collection.insert_one({"username": username, "password": pw_hash})
        flash("User created! Please login.")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_dict = users_collection.find_one({"username": username})
        if user_dict and bcrypt.check_password_hash(user_dict["password"], password):
            user = User(user_dict)
            login_user(user)
            return redirect(url_for("pages.home"))
        flash("Invalid username or password")
        return redirect(url_for("auth.login"))
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
