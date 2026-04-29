from flask import jsonify, request, session
from . import coach_bp
from app.services.coach.update_Availability import update_coach_availability

@coach_bp.route("/availability/update", methods=["POST"])
def update_availability_route():
    """
Update coach availability
---
tags:
  - coach
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      properties:
        num_days:
          type: integer
        day_of_week:
          type: array
          items:
            type: string
        start_time:
          type: array
          items:
            type: string
        end_time:
          type: array
          items:
            type: string
        recurring:
          type: array
          items:
            type: boolean
        active:
          type: array
          items:
            type: boolean
responses:
  200:
    description: Availability updated
  401:
    description: Unauthorized
    """
    u_id = session.get("user_id")
    role = session.get("role")

    if not u_id or role != "coach":
        return jsonify({"error": "Unauthorized. Coach access only."}), 401

    data = request.get_json() 
    
    num_days = int(data.get("num_days", 0))
    days = data.get("day_of_week", [])
    starts = data.get("start_time", [])
    ends = data.get("end_time", [])
    recurring = data.get("recurring", [])
    active = data.get("active", [])

    try:
        update_coach_availability(u_id, num_days, days, starts, ends, recurring, active)
        
        return jsonify({
            "message": "Weekly availability updated successfully",
            "count": num_days
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500