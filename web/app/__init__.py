from flask import Flask
from .db import init_db_client
from .auth import auth_bp, bcrypt, login_manager
from .api import api_bp
from .pages import pages_bp

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["SECRET_KEY"] = "dev-secret-key"  # TODO: switch to .env

    # 1. Initialize DB client
    init_db_client(app)

    # 2. Initialize auth-related extensions
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # 3. Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(pages_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
