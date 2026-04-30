from . import client_bp 
from app.services.client.accountService import submit_mental_survey_service
from app.services.client.check_Survey import check_survey_status_service
from flask import jsonify, request, session
from datetime import date

@client_bp.route("/mental-survey", methods=["POST"])
def handle_mental_survey():
    """
Submit mental survey
---
tags:
  - client
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - mood_score
      properties:
        mood_score:
          type: number
        notes:
          type: string
responses:
  201:
    description: Survey recorded
  400:
    description: Missing fields
  409:
    description: Already submitted
"""
    data = request.get_json()
    u_id = session.get('user_id') or data.get('user_id')
    score = data.get('mood_score')
    notes = data.get('notes')
    today = date.today().isoformat()

    if not u_id or score is None:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Prevent "double-dipping" if someone hits the API directly
        if check_survey_status_service(u_id, today):
            return jsonify({"error": "Survey already submitted for today"}), 409

        submit_mental_survey_service(u_id, score, notes, today)
        return jsonify({"message": "Survey recorded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500