from . import onboard_bp
from flask import jsonify, session, request
from datetime import datetime
from app.services.onboarding import onboardUser


@onboard_bp.route("/", methods=["POST"])
def onboardSurvey():
    try:
        data = request.get_json() or {}

        u_id = session.get("user_id")
        role = session.get("role")

        if not u_id or not role:
            return jsonify({"error": "Unauthorized"}), 401

        u_id = int(u_id)

        date = datetime.fromisoformat(data.get("dob")) if data.get("dob") is not None else datetime.now()
        gw = data.get("goal_weight") if data.get("goal_weight") is not None else data.get("weight")
        pfp = data.get("profile_picture")
        weight = data.get("weight")
        height = data.get("height")

        required_fields = [weight, height, data.get("dob")]
        if any(field is None for field in required_fields):
            return jsonify({"error": "weight, height, date of birth are required field"}), 400

        if role == "client":
            onboardUser.onboardClientSurvey(
                u_id,
                pfp,
                weight,
                height,
                gw,
                date
            )
            return jsonify({"message": "Onboarding completed successfully"}), 200

        elif role == "coach":
            desc = data.get("coach_description")
            price = data.get("price")

            required_fields_coach = [desc, price]
            if any(field is None for field in required_fields_coach):
                return jsonify({"error": "description and price are required field"}), 400

            onboardUser.onboardClientSurvey(
                u_id,
                pfp,
                weight,
                height,
                gw,
                date
            )

            onboardUser.onboardCoachSurvey(
                u_id,
                desc,
                price
            )

            n_c = int(data.get("num_cert") or 0)

            cert_names = data.get("cert_name", [])
            provider_names = data.get("provider_name", [])
            descriptions = data.get("description", [])
            issued_dates = data.get("issued_date", [])
            expires_dates = data.get("expires_date", [])

            for i in range(n_c):
                onboardUser.insertCoachCert(
                    u_id,
                    cert_names[i],
                    provider_names[i],
                    descriptions[i],
                    datetime.fromisoformat(issued_dates[i]) if issued_dates[i] else None,
                    datetime.fromisoformat(expires_dates[i]) if expires_dates[i] else None,
                )

            n_d = int(data.get("num_days") or 0)

            days_of_week = data.get("day_of_week", [])
            start_times = data.get("start_time", [])
            end_times = data.get("end_time", [])
            recurring_list = data.get("recurring", [])
            active_list = data.get("active", [])

            for i in range(n_d):
                onboardUser.coachAvailability(
                    u_id,
                    days_of_week[i],
                    start_times[i],
                    end_times[i],
                    recurring_list[i],
                    active_list[i]
                )

            return jsonify({"message": "Onboarding completed successfully"}), 200

        else:
            return jsonify({"error": "Invalid role"}), 400

    except Exception as e:
        raise e