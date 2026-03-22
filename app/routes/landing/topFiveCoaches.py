from . import landing_bp
from flask import jsonify
from app.services.coach.topCoaches.topFiveCoaches import getTopFiveCoaches


@landing_bp.route("/topCoaches", methods=["GET"])
def topFiveCoaches():
    try:
        return jsonify(getTopFiveCoaches()), 200
    except Exception as e:
        return {"error": str(e)}, 500
