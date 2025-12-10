from flask import Flask
from mongodb_subsystem import init_mongo
from .auth import auth_bp, bcrypt, login_manager
from .api import api_bp
from .pages import pages_bp

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    init_mongo()
    app.config["SECRET_KEY"] = "dev-secret-key"  # TODO: move to .env later

    # Initialize extensions
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)   # /auth/login, /auth/register, /auth/logout
    app.register_blueprint(api_bp)    # /api/...
    app.register_blueprint(pages_bp)  # "/", "/recipe", etc.

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
