from . import client_bp
from app.services.client.check_Survey import check_survey_status_service
from flask import jsonify, request, session
from datetime import date

@client_bp.route("/mental-survey/check", methods=["GET"])
def check_survey():
    """
Check if mental survey taken today
---
tags:
  - client
responses:
  200:
    description: Survey status
    schema:
      type: object
      properties:
        taken_today:
          type: boolean
  400:
    description: Missing user_id
"""
    u_id = session.get('user_id') 
    today = date.today().isoformat()

    if not u_id:
        return jsonify({"error": "User ID is required"}), 400

    has_taken = check_survey_status_service(u_id, today)
    return jsonify({"taken_today": has_taken}), 200