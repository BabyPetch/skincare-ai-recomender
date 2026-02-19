from flask import Flask
from flask_cors import CORS

from config import Config
from services.ai_engine import DataLoader
from services.user_manager import UserManager

from routes.auth_routes import auth_bp, init_auth_routes
from routes.admin_routes import admin_bp, init_admin_routes
from routes.ai_routes import ai_bp, init_ai_routes
from routes.user_routes import user_bp, init_user_routes

from database.db import init_database

init_database()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # Initialize services
    user_manager = UserManager()
    ai = DataLoader()

    # Initialize routes with dependencies
    init_auth_routes(user_manager)
    init_admin_routes(user_manager)
    init_ai_routes(ai, user_manager)
    init_user_routes(user_manager)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(user_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
