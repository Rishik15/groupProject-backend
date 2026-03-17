from . import topCoaches_bp
from flask import jsonify
from app.services.coach.topCoaches import topFiveCoaches


@topCoaches_bp.route("/", methods=["GET"])
def topFiveCoaches():
    jsonify(topFiveCoaches.topFiveCoaches())
