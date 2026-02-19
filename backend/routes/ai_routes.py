from flask import Blueprint, request, jsonify

ai_bp = Blueprint("ai", __name__)

def init_ai_routes(ai_engine, user_manager):

    @ai_bp.route('/api/recommend', methods=['POST'])
    def recommend():
        data = request.json

        skin_type = data.get('skin_type', 'all')
        concerns = data.get('concerns', [])
        price_key = data.get('price_range', 'any')
        email = data.get('email')

        price_ranges = {
            "low": (0, 500),
            "medium": (500, 1500),
            "high": (1500, 100000),
            "any": (0, 100000)
        }

        min_p, max_p = price_ranges.get(price_key, (0, 100000))

        recommendations = ai_engine.recommend_products(
            skin_type=skin_type,
            concerns=concerns,
            min_price=min_p,
            max_price=max_p
        )

        if email:
            user_manager.add_history(email, skin_type, concerns, recommendations)

        return jsonify(recommendations)
