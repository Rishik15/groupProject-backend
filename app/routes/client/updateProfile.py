from . import client_bp 
from app.services.client.update_Profile import update_client_metrics
from flask import jsonify, request, session

@client_bp.route("/update-metrics", methods=["PUT"]) 
def handle_update_metrics():
    data = request.get_json()
    u_id = session.get('user_id') or data.get('user_id')
    
    if not u_id:
        return jsonify({"error": "User ID is required"}), 400

    weight = data.get('weight')
    height = data.get('height')
    goal_weight = data.get('goal_weight')

    if weight is None and height is None and goal_weight is None:
        return jsonify({"error": "No update fields provided"}), 400

    try:
        update_client_metrics(u_id, weight, height, goal_weight)
        return jsonify({"message": "Profile metrics updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500