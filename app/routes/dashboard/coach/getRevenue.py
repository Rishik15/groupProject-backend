from . import dashboard_coach_bp
from flask import session
from app.services.auth.checkUser import checkUserExists
from app.services.dashboard.coach.getRevenueMonth import getRevenueLast6Months


@dashboard_coach_bp.route("/revenue", methods=["GET"])
def revenue():
    """
Get coach revenue
---
tags:
  - dashboard-coach
responses:
  200:
    description: Revenue data
  401:
    description: Unauthorized
"""
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    coach_id = session.get("user_id")

    if not checkUserExists(user_id=coach_id):
        return {"error": "Unauthorized"}, 401

    data = getRevenueLast6Months(coach_id)

    return {"revenue": data}, 200
