from app.services import run_query
from datetime import datetime


def onboardClientSurvey(
    user_id: int,
    profile_picture: str,
    weight: float,
    height: float,
    goal_weight: float,
    dob=None
):
    if dob is None:
        dob = datetime.now()

    try:
        run_query(
            """
            UPDATE user_mutables 
            SET  
                profile_picture = :profile_picture,
                weight = :weight,
                height = :height,
                goal_weight = :goal_weight
            WHERE user_id = :user_id; 
            """,
            {
                "user_id": user_id,
                "profile_picture": profile_picture,
                "weight": weight,
                "height": height,
                "goal_weight": goal_weight
            },
            fetch=False,
            commit=True,
        )

        run_query(
            """
            UPDATE user_immutables 
            SET  
                dob = :dob
            WHERE user_id = :user_id; 
            """,
            {"user_id": user_id, "dob": dob},
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
            WHERE 
                coach_id = :user_id; 
            """,
            {"user_id": user_id, "desc": desc, "price": price},
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
                :cid, 
                :certN,
                :provN, 
                :desc, 
                :id, 
                :ed
            )
            """,
            {
                "cid": coach_id,
                "certN": cert_name,
                "provN": provider_name,
                "desc": description,
                "id": issued_date,
                "ed": expires_date
            },
            fetch=False,
            commit=True
        )
    except Exception as e:
        raise e


def coachAvailability(
    coach_id,
    dow,
    st,
    et,
    rec,
    active
):
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
                :cid, 
                :dow, 
                :st,
                :et, 
                :rec, 
                :active
            )
            """,
            {
                "cid": coach_id,
                "dow": dow,
                "st": st,
                "et": et,
                "rec": rec,
                "active": active
            },
            fetch=False,
            commit=True
        )
    except Exception as e:
        raise e