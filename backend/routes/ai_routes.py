from flask import Blueprint, request, jsonify

ai_bp = Blueprint("ai", __name__)

PRICE_RANGES = {
    "low":    (0,     500),
    "medium": (500,   1500),
    "high":   (1500,  100000),
    "any":    (0,     100000),
}

def init_ai_routes(ai_engine, user_manager):

    @ai_bp.route('/api/recommend', methods=['POST'])
    def recommend():
        data      = request.json
        skin_type = data.get('skin_type', 'all')
        concerns  = data.get('concerns', [])
        price_key = data.get('price_range', 'any')
        email     = data.get('email')
        context   = data.get('context', {})
        min_p, max_p = PRICE_RANGES.get(price_key, (0, 100000))

        result = ai_engine.recommend_products(
            skin_type=skin_type, concerns=concerns,
            min_price=min_p, max_price=max_p, context=context,
            top_n=100,  # ← ส่งทั้งหมดไม่จำกัด
        )
        if email:
            user_manager.add_history(email, skin_type, concerns, result[:5])
        return jsonify(result)


    @ai_bp.route('/api/routine', methods=['POST'])
    def routine():
        data      = request.json
        skin_type = data.get('skin_type', 'all')
        concerns  = data.get('concerns', [])
        price_key = data.get('price_range', 'any')
        context   = data.get('context', {})
        min_p, max_p = PRICE_RANGES.get(price_key, (0, 100000))

        result = ai_engine.recommend_routine(
            skin_type=skin_type, concerns=concerns,
            min_price=min_p, max_price=max_p, context=context,
        )
        return jsonify(result)


    @ai_bp.route('/api/recommend-all', methods=['POST'])
    def recommend_all():
        data      = request.json
        skin_type = data.get('skin_type', 'all')
        concerns  = data.get('concerns', [])
        price_key = data.get('price_range', 'any')
        email     = data.get('email')
        context   = data.get('context', {})
        min_p, max_p = PRICE_RANGES.get(price_key, (0, 100000))

        rec = ai_engine.recommend_products(
            skin_type=skin_type, concerns=concerns,
            min_price=min_p, max_price=max_p, context=context,
            top_n=100,  # ← ส่งทั้งหมด frontend จัด pagination เอง
        )
        routine = ai_engine.recommend_routine(
            skin_type=skin_type, concerns=concerns,
            min_price=min_p, max_price=max_p, context=context,
        )
        # บันทึก history แค่ top 5
        if email:
            user_manager.add_history(email, skin_type, concerns, rec[:5], routine)
        return jsonify({"recommend": rec, "routine": routine})


    @ai_bp.route('/api/search', methods=['GET'])
    def search():
        q = request.args.get('q', '').strip().lower()
        if not q:
            return jsonify([])
        return jsonify(ai_engine.search_products(q))