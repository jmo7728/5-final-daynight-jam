from flask import Flask
from .auth import auth_bp, bcrypt, login_manager
from .pages import pages_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"

    bcrypt.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
