from . import coach_bp
from app.services.coach.rateCoaches import (
    getReviews,
    postReview,
    clientKnowsCoach,
    hasExistingReview,
)
from services.coach.getCoachInfo import getCoachInformation
from flask import session, request, jsonify


@coach_bp.route("/get_coach_info", methods=["GET"])
def getCoachInfo():
    """
    Response:
    {
        "first_name": str,
        "last_name": str,
        "price": number,
        "coach_description": str,
        "profile_picture": str,
        "weight": number,
        "height": number
    }
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
    Response:
    {
        "coach_avg_rating": float | None,
        "reviews": [
            {
                "review_id": int,
                "rating": int,
                "review_text": str,
                "reviewer_first_name": str,
                "reviewer_last_name": str,
                "created_at": str,
                "updated_at": str
            }
        ],
        "coach_first_name": str,
        "coach_last_name": str
    }
    """
    try:
        u_id = session.get("user_id")
        role = session.get("role")

        if not u_id or not role:
            return jsonify({"error": "Unauthorized"}), 401

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

        return jsonify(getReviews(c_id)), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        return jsonify({"error": "failed to fetch reviews"}), 500


@coach_bp.route("/leave_review", methods=["POST"])
def leaveCoachReview():
    """
    Expects:
    {
        "coach_id": int,
        "rating": int,
        "review_text": str
    }
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
