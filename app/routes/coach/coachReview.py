from . import coach_bp
from services.coach.rateCoaches import getReviews, postReview, clientKnowsCoach
from flask import session, request, jsonify

@coach_bp.route("/get_review", methods=["GET"])
def getCoachReview():
    """
    {
    "coach_avg_rating" : float
    "reviews" : [ {"review_id": int, "rating": int, "review_text": str, "reviewer_first_name": str, "reviewer_last_name" : str, "created_at": datetime(isoFormat), "updated_at": datetime(isoFormat)} ] (list of dictionaries)
    "coach_first_name" : str
    "coach_last_name": str
    }
    """
    try : 
        data = request.get_json()
        u_id = session.get("user_id")
        role = session.get("role")
        c_id = data.get("coach_id")
    
    
        if not u_id or not role:
            return jsonify({"error": "Unauthorized"}), 401
        if not c_id: 
            return jsonify({"error": "no coach provided"}), 500
    
        return jsonify(getReviews(c_id)), 200
    except Exception as e : 
        raise e 
@coach_bp.route("/leave_review", methods=["POST"])
def leaveCoachReview():
    """
    expects : 
    "coach_id" : int
    "rating" : int (1-5) must be an int
    "review_text": str
    """
    try: 
        u_id = session.get("user_id")
        role = session.get("role")
        data = request.get_json()
        c_id = data.get("coach_id")
    
        if not u_id or not role :
            return jsonify({"error": "Unauthorized"}), 401
        if not c_id:
            return jsonify({"error": "no coach provided"}), 500
        if  not (role == "client") or not clientKnowsCoach(u_id, c_id) : 
            return jsonify({"error": "only clients who have worked with a coach can leave a review"}) , 500
        
        rate = data.get("rating")
        if rate > 5 or rate < 1 or not isinstance(rate, int): 
            return jsonify({"error": "you must provide an integer value 1 <= rating <= 5"}) , 500
        review = data.get("review_text")
        u_id = int(u_id)
        role = session.get("role")
        postReview(u_id, c_id, rate, review)
        return jsonify({"message": "success"}), 200
    except Exception as e:
        raise e
