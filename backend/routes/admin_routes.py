from flask import Blueprint, jsonify

admin_bp = Blueprint("admin", __name__)

def init_admin_routes(user_manager):

    @admin_bp.route('/api/admin/users', methods=['GET'])
    def get_all_users():
        users = user_manager.get_all_users()
        return jsonify(users)

    @admin_bp.route('/api/admin/users/<email>', methods=['DELETE'])
    def delete_user(email):
        success, message = user_manager.delete_user(email)
        return jsonify({'message' if success else 'error': message})
