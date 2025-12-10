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

from mongodb_subsystem import users_collection

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


class User(UserMixin):
    """Wrapper around a Mongo user document for Flask-Login."""

    def __init__(self, user_doc: dict):
        self.id = str(user_doc["_id"])
        self.username = user_doc["username"]
        self.password_hash = user_doc["password"]

    @property
    def is_active(self) -> bool:
        return True


@login_manager.user_loader
def load_user(user_id: str):
    """Given a user_id (string), return the corresponding User or None."""
    try:
        doc = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None
    if not doc:
        return None
    return User(doc)


def find_user_by_username(username: str):
    return users_collection.find_one({"username": username})


def create_user(username: str, password: str) -> bool:
    """Create a user if username not taken. Returns True if created."""
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

        user = User(user_doc)
        login_user(user)
        return redirect(url_for("pages.home"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/me")
def me():
    if current_user.is_authenticated:
        return {"username": current_user.username}
    return {"username": None}
