from flask import Blueprint, request, jsonify, session
from app.services.coach.add_certs import add_coach_certification
from . import coach_bp

@coach_bp.route("/certificates", methods=["POST"])
def add_cert():
    """
Add coach certification
---
tags:
  - coach
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - role
        - cert_name
        - provider_name
      properties:
        role:
          type: string
        cert_name:
          type: string
        provider_name:
          type: string
        description:
          type: string
        issued_date:
          type: string
          format: date
        expires_date:
          type: string
          format: date
responses:
  201:
    description: Certification added
  403:
    description: Forbidden
    """
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

