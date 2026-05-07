from app.services import run_query


def onboardClientSurvey(
    user_id: int,
    profile_picture: str,
    weight: float,
    height: float,
    goal_weight: float,
    dob,
):
    try:
        run_query(
            """
            UPDATE user_mutables 
            SET  
                profile_picture = :profile_picture,
                weight = :weight,
                height = :height,
                goal_weight = :goal_weight
            WHERE user_id = :user_id
            """,
            {
                "user_id": user_id,
                "profile_picture": profile_picture,
                "weight": weight,
                "height": height,
                "goal_weight": goal_weight,
            },
            fetch=False,
            commit=True,
        )

        run_query(
            """
            UPDATE users_immutables 
            SET dob = :dob
            WHERE user_id = :user_id
            """,
            {
                "user_id": user_id,
                "dob": dob,
            },
            fetch=False,
            commit=True,
        )

    except Exception as e:
        raise e


def onboardCoachSurvey(user_id: int, desc: str, price: float):
    try:
        run_query(
            """
            UPDATE coach
            SET  
                coach_description = :desc,
                price = :price
            WHERE coach_id = :user_id
            """,
            {
                "user_id": user_id,
                "desc": desc,
                "price": price,
            },
            fetch=False,
            commit=True,
        )

    except Exception as e:
        raise e


def insertCoachCert(
    coach_id: int,
    cert_name: str,
    provider_name: str,
    description: str,
    issued_date,
    expires_date,
):
    try:
        run_query(
            """
            INSERT INTO certifications
            (
                coach_id,
                cert_name,
                provider_name, 
                description,
                issued_date,
                expires_date
            )
            VALUES
            (
                :coach_id, 
                :cert_name,
                :provider_name, 
                :description, 
                :issued_date, 
                :expires_date
            )
            """,
            {
                "coach_id": coach_id,
                "cert_name": cert_name,
                "provider_name": provider_name,
                "description": description,
                "issued_date": issued_date,
                "expires_date": expires_date,
            },
            fetch=False,
            commit=True,
        )

    except Exception as e:
        raise e


def coachAvailability(coach_id, dow, st, et, rec, active):
    day_map = {
        "Monday": "Mon",
        "Tuesday": "Tue",
        "Wednesday": "Wed",
        "Thursday": "Thu",
        "Friday": "Fri",
        "Saturday": "Sat",
        "Sunday": "Sun",
    }

    dow = day_map.get(dow, dow)

    try:
        run_query(
            """
            INSERT INTO coach_availability
            (
                coach_id, 
                day_of_week,
                start_time,
                end_time,
                recurring,
                active
            )
            VALUES 
            (
                :coach_id, 
                :day_of_week, 
                :start_time,
                :end_time, 
                :recurring, 
                :active
            )
            """,
            {
                "coach_id": coach_id,
                "day_of_week": dow,
                "start_time": st,
                "end_time": et,
                "recurring": rec,
                "active": active,
            },
            fetch=False,
            commit=True,
        )

    except Exception as e:
        raise e
