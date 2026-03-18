from flask import jsonify, request, session
from . import coach_bp
from app.services.coach.search_coaches import search_coaches

@coach_bp.route("/search", methods=["POST"])
def search_coaches_route():
    data = request.get_json()
    name = data.get("name", "")
    filters = data.get("tags", [])
    try:
        coaches = search_coaches(name, filters)
        return jsonify({"coaches": coaches}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500