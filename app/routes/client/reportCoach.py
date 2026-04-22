from . import client_bp
from flask import jsonify, request, session
from app.services.client.report_Coach import create_user_report

@client_bp.route("/reportCoach", methods=["POST"])
def reportCoach():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    coach_id = data.get("coach_id")
    formReason = data.get("reason")
    formDescription = data.get("description") 

    if not coach_id:
        return jsonify({"error": "Coach ID is required"}), 400
        
    if not formReason or not formReason.strip():
        return jsonify({"error": "A reason category must be selected"}), 400
        
    if not formDescription or not formDescription.strip():
        return jsonify({"error": "Please provide details in the description field"}), 400

    # Format the combined text for the DB
    full_reason = f"Category: {formReason}\nDetails: {formDescription}"

    try:
        create_user_report(
            reporter_id=int(user_id),
            reported_id=int(coach_id),
            reason_text=full_reason
        )
        return jsonify({"message": "Report submitted successfully."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500