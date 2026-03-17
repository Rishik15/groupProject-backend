from . import topCoaches_bp
from flask import jsonify
from app.services.coach.topCoaches.topFiveCoaches import  getTopFiveCoaches


@topCoaches_bp.route("/", methods=["GET"])
def topFiveCoaches():
    return jsonify(getTopFiveCoaches())
