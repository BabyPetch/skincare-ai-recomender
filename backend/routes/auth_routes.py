from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__)

def init_auth_routes(user_manager):

    @auth_bp.route('/api/login', methods=['POST'])
    def login():
        data = request.json
        success, result = user_manager.login(
            data.get('email'),
            data.get('password')
        )

        if success:
            return jsonify({'message': 'Login successful', 'user': result})
        return jsonify({'error': result}), 401

    @auth_bp.route('/api/register', methods=['POST'])
    def register():
        data = request.json
        success, message = user_manager.register(
            data.get('name'),
            data.get('email'),
            data.get('password'),
            data.get('birthdate')
        )

        if success:
            return jsonify({'message': message}), 201
        return jsonify({'error': message}), 400
