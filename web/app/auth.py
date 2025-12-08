from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    render_template,
    flash,
)
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user,
)
from bson import ObjectId

from .db import users_collection

# Blueprint for all auth-related routes
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Extensions – initialized in create_app()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # where @login_required will redirect


# ----------------- Flask-Login User wrapper -----------------


class User(UserMixin):
    """
    Lightweight wrapper around a MongoDB user document, for Flask-Login.
    """

    def __init__(self, user_doc: dict):
        self.id = str(user_doc["_id"])
        self.username = user_doc["username"]
        # store hash if needed; not used directly by Flask-Login
        self.password_hash = user_doc["password"]

    @property
    def is_active(self) -> bool:
        # For this project, everyone is active
        return True


@login_manager.user_loader
def load_user(user_id: str):
    """
    Given a user_id (string), return the corresponding User object.
    Called automatically by Flask-Login using the session.
    """
    try:
        doc = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None

    if not doc:
        return None

    return User(doc)


# ----------------- Helper DB functions -----------------


def find_user_by_username(username: str):
    return users_collection.find_one({"username": username})


def create_user(username: str, password: str) -> bool:
    """
    Create a new user with the given username and plaintext password.
    Returns True if created, False if username already exists.
    """
    if find_user_by_username(username):
        return False

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    users_collection.insert_one(
        {
            "username": username,
            "password": pw_hash,
        }
    )
    return True


# ----------------- Routes -----------------


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        if not create_user(username, password):
            flash("That username is already taken.", "error")
            return render_template("register.html")

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    # GET
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html")

        user_doc = find_user_by_username(username)
        if not user_doc:
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        if not bcrypt.check_password_hash(user_doc["password"], password):
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        # Success → log in via Flask-Login
        user = User(user_doc)
        login_user(user)

        # After login, go to main home page (pages.home)
        return redirect(url_for("pages.home"))

    # GET
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/me")
def me():
    """
    Small helper endpoint for debugging – shows current user.
    """
    if current_user.is_authenticated:
        return {"username": current_user.username}
    return {"username": None}
