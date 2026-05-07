from datetime import date
from flask import jsonify, request, session

from . import client_bp
from app.services.client.accountService import submit_mental_survey_service
from app.services.client.check_Survey import check_survey_status_service


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
            weight:
              type: number
            sleep_hours:
              type: number
    responses:
      201:
        description: Survey recorded
      400:
        description: Missing fields
      409:
        description: Already submitted
    """
    data = request.get_json() or {}

    user_id = session.get("user_id") or data.get("user_id")
    mood_score = data.get("mood_score")
    notes = data.get("notes")
    weight = data.get("weight")
    sleep_hours = data.get("sleep_hours")
    today = date.today().isoformat()

    if not user_id or mood_score is None:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        if check_survey_status_service(user_id, today):
            return jsonify({"error": "Survey already submitted for today"}), 409

        submit_mental_survey_service(
            user_id=user_id,
            score=mood_score,
            notes=notes,
            today=today,
            weight=weight,
            sleep_hours=sleep_hours,
        )

        return jsonify({"message": "Survey recorded successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
