from flask import Flask, request, jsonify
from flask_cors import CORS
from services.ai_engine import SkincareAI
from services.user_manager import UserManager

app = Flask(__name__)
CORS(app)

# --- Initialize Services ---
# สร้างลูกน้องเตรียมไว้ทำงาน
ai_engine = SkincareAI()
user_manager = UserManager()

# --- Routes ---

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        skin_type = data.get('skinType', 'All')
        concerns = data.get('concerns', [])
        age = data.get('age', 25)

        # สั่งให้ AI ทำงาน
        recommendations = ai_engine.recommend(skin_type, concerns, age)
        
        return jsonify({'success': True, 'recommendations': recommendations})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    success, result = user_manager.login(data['email'], data['password'])
    if success:
        return jsonify({"success": True, "user": result})
    return jsonify({"success": False, "message": result}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    success, message = user_manager.register(
        data['name'], 
        data['email'], 
        data['password'], 
        data.get('birthdate', '2000-01-01')
    )
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)