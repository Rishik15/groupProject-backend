from . import onboard_bp
# from app.services.
from flask import jsonify, session, request
from datetime import datetime
from app.services.onboarding import onboardUser

@onboard_bp.route("/", methods=["POST"])
def onboardSurvey():
    try:    
        data = request.get_json()

        u_id = session.get("user_id")
        role = session.get("role")

        if not u_id or not role:
            return jsonify({"error": "Unauthorized"}), 401
        u_id = int(u_id)


        date = data.get("dob").fromisoformat() if data.get("dob") is not None else datetime.now() 
        gw = data.get("goal_weight") if data.get("goal_weight") is not None else data.get("weight")
        pfp = data.get("profile_picture"), 
        weight = data.get("weight"),
        height = data.get("height"),


        required_fields = [date, weight, height]
        if any(field is None for field in required_fields):
            return jsonify({"error": "weight, height, date of birth are required field"}), 400

        if role == 'client':
            try:
                #In the future we may optionally accept the users skill (this will require a schema update)
                onboardUser.onboardClientSurvey(
                    u_id, 
                    pfp, 
                    weight, 
                    height,
                    gw,
                    date
                    )
                return jsonify({"message": "Onboarding completed successfully"}), 200
            except Exception as e: 
                raise e
            
        elif role == 'coach':
            desc = data.get("coach_description")
            price = data.get("price")
            required_fields_coach = [desc, price]
            if any(field is None for field in required_fields_coach):
                return jsonify({"error": "weight, height, date of birth are required field"}), 400
            try:
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
                
                
                n_c = data.get("num_cert") if data.get("num_cert") is not None else 0  
                n_c = int(n_c)
                i = 0
                for i in range(0, n_c): 
                    coach_id = u_id, 
                    cert_name = data.get("cert_name"),
                    provider_name = data.get("provider_name"),
                    description = data.get("description"),
                    issued_date = data.get("issued_date").fromisoformat(), 
                    expires_date = data.get("expires_date").fromisoformat()
                    onboardUser.insertCoachCert(
                        coach_id,
                        cert_name,
                        provider_name, 
                        description,
                        issued_date,
                        expires_date,
                    )
                    i+=1
                
                n_d = data.get("num_days") if data.get("num_days") is not None else 0
                i = 0
                coach_id = u_id 
                dow = data.get("day_of_week")
                st = data.get("start_time")
                et = data.get("end_time")
                rec = data.get("recurring")
                active = data.get("active")
                for i in range (0, int(n_d)):
                    onboardUser.coachAvailability(
                        coach_id,
                        dow,
                        st,
                        et, 
                        rec, 
                        active
                    ) 
                return jsonify({"message": "Onboarding completed successfully"}), 200
            except Exception as e: 
                raise e
    
        else: 
            return jsonify({"error": "Invalid role"}), 400
    except Exception as e: 
        raise e 