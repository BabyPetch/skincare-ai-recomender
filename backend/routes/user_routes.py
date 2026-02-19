from flask import Blueprint, jsonify

user_bp = Blueprint("user", __name__)

def init_user_routes(user_manager):

    @user_bp.route('/api/user/<email>', methods=['GET'])
    def get_user(email):
        user = user_manager.get_user_with_history(email)
        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
