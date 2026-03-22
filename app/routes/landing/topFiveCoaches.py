from . import topCoaches_bp
from flask import jsonify
from app.services.coach.topCoaches.topFiveCoaches import  getTopFiveCoaches


@topCoaches_bp.route("/", methods=["GET"])
def topFiveCoaches():
    try: 
        return jsonify(getTopFiveCoaches()),  200
    except Exception as e: 
        return {"error": str(e)}, 500 
