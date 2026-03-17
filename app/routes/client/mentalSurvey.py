from . import client_bp 
from app.services.client.accountService import submit_mental_survey_service
from flask import jsonify, request, session
from datetime import date

@client_bp.route("/mental-survey", methods=["POST"])
def handle_mental_survey():
    data = request.get_json()
    
    # Grab the ID from the form data parsed from JSON
    u_id = session.get('user_id')
    score = data.get('mood_score')
    notes = data.get('notes')
    today = date.today().isoformat()

    try:
        submit_mental_survey_service(u_id, score, notes, today)
        return jsonify({"message": "Survey recorded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500