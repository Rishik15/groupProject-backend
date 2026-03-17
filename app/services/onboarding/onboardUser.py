from app.services import run_query

def onboardClientSurvey(user_id: int, profile_picture: str, weight: float, height: float, goal_weight: float):

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
            {"user_id": user_id, "profile_picture": profile_picture, "weight": weight, "height": height, "goal_weight": goal_weight },
            fetch=False,
            commit=True,
        )

    except Exception as e:
        raise e
    
def onboardCoachSurvey(user_id: int, desc: str, price : float ):

    try:

        run_query(
            """
            UPDATE coach
            SET  
                coach_description = :desc
                price = :price
            WHERE 
                user_id = :user_id; 
        """,
            {"user_id": user_id, "desc": desc, "price": price},
            fetch=False,
            commit=True,
        )

    except Exception as e:
        raise e

