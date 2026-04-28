from . import coach_bp
from app.services.coach.rateCoaches import (
    getReviews,
    postReview,
    clientKnowsCoach,
    hasExistingReview,
)
from app.services.coach.getCoachInfo import getCoachInformation

from flask import session, request, jsonify


@coach_bp.route("/get_coach_info", methods=["GET"])
def getCoachInfo():
    """
Get coach information
---
tags:
  - coach
parameters:
  - name: coach_id
    in: query
    type: integer
    required: true
responses:
  200:
    description: Coach info
  400:
    description: Invalid coach_id
  401:
    description: Unauthorized
  404:
    description: Coach not found
    """
    u_id = session.get("user_id")
    role = session.get("role")

    c_id = request.args.get("coach_id")

    if not u_id or not role:
        return jsonify({"error": "Unauthorized"}), 401
    if c_id is None:
        return jsonify({"error": "no coach provided"}), 400

    try:
        c_id = int(c_id)
    except (TypeError, ValueError):
        return jsonify({"error": "coach_id must be an integer"}), 400

    try:
        result = getCoachInformation(c_id)
        if not result:
            return jsonify({"error": "coach not found"}), 404
        return jsonify(result[0] if isinstance(result, list) else result), 200
    except Exception:
        return jsonify({"error": "failed to fetch coach info"}), 500


@coach_bp.route("/get_review", methods=["GET"])
def getCoachReview():
    """
Get coach reviews
---
tags:
  - coach
parameters:
  - name: coach_id
    in: query
    type: integer
    required: true
responses:
  200:
    description: Reviews data
  400:
    description: Invalid coach_id
  401:
    description: Unauthorized
    """
    try:
        u_id = session.get("user_id")
        role = session.get("role")

        c_id = request.args.get("coach_id")

        if c_id is None:
            data = request.get_json(silent=True) or {}
            c_id = data.get("coach_id")

        if c_id is None:
            return jsonify({"error": "no coach provided"}), 400

        try:
            c_id = int(c_id)
        except (TypeError, ValueError):
            return jsonify({"error": "coach_id must be an integer"}), 400

        review_data = getReviews(c_id)

        can_review = False
        if u_id and role == "client":
            can_review = clientKnowsCoach(u_id, c_id) and not hasExistingReview(
                u_id, c_id
            )

        review_data["can_review"] = can_review

        return jsonify(review_data), 200

    except Exception:
        return jsonify({"error": "failed to fetch reviews"}), 500


@coach_bp.route("/leave_review", methods=["POST"])
def leaveCoachReview():
    """
Leave a review for a coach
---
tags:
  - coach
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - coach_id
        - rating
      properties:
        coach_id:
          type: integer
        rating:
          type: integer
        review_text:
          type: string
responses:
  200:
    description: Review submitted
  400:
    description: Invalid input
  401:
    description: Unauthorized
  403:
    description: Not allowed to review
  409:
    description: Already reviewed
    """
    try:
        u_id = session.get("user_id")
        role = session.get("role")

        if not u_id or not role:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}

        c_id = data.get("coach_id")
        if c_id is None:
            return jsonify({"error": "no coach provided"}), 400

        try:
            c_id = int(c_id)
        except (TypeError, ValueError):
            return jsonify({"error": "coach_id must be an integer"}), 400

        if role != "client":
            return jsonify({"error": "only clients can leave a review"}), 403

        try:
            u_id = int(u_id)
        except (TypeError, ValueError):
            return jsonify({"error": "invalid user session"}), 401

        if not clientKnowsCoach(u_id, c_id):
            return (
                jsonify(
                    {
                        "error": "only clients who have worked with a coach can leave a review"
                    }
                ),
                403,
            )

        if hasExistingReview(u_id, c_id):
            return jsonify({"error": "you have already reviewed this coach"}), 409

        rate = data.get("rating")
        if not isinstance(rate, int) or rate < 1 or rate > 5:
            return (
                jsonify(
                    {"error": "you must provide an integer value 1 <= rating <= 5"}
                ),
                400,
            )

        review = data.get("review_text", "")
        if review is None:
            review = ""

        if not isinstance(review, str):
            return jsonify({"error": "review_text must be a string"}), 400

        postReview(u_id, c_id, rate, review.strip())
        return jsonify({"message": "success"}), 200

    except Exception:
        return jsonify({"error": "failed to leave review"}), 500
