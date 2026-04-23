from flask import Blueprint, request, jsonify, session
from app.services.coach.add_certs import add_coach_certification
from . import coach_bp

@coach_bp.route("/certificates", methods=["POST"])
def add_cert():

    coach_id = session.get("user_id")

    data = request.get_json()

    role = data.get("role")

    if role != "coach":
        return jsonify({"error": "Forbidden. Coach role required to add new certifications!"}), 403
    
    try:
        result = add_coach_certification(coach_id, data)
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

