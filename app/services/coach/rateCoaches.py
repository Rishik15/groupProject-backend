from .. import run_query

def getReviews(coach_id: int):
    try:
        summary = run_query(
            """
                SELECT 
                    ROUND(AVG(cr.rating), 2) AS coach_avg_rating,
                    ui.first_name AS coach_first_name,
                    ui.last_name AS coach_last_name
                FROM coach_review cr
                INNER JOIN users_immutables ui
                    ON cr.coach_id = ui.user_id
                WHERE cr.coach_id = :c_id
                GROUP BY ui.first_name, ui.last_name
                ;
            """,
            {"c_id": coach_id},
            fetch=True,
            commit=False
        )

        reviews = run_query(
            """
                SELECT 
                    cr.review_id,
                    cr.rating,
                    cr.review_text,
                    reviewer.first_name AS reviewer_first_name,
                    reviewer.last_name AS reviewer_last_name,
                    cr.created_at,
                    cr.updated_at
                FROM coach_review cr
                INNER JOIN users_immutables reviewer
                    ON cr.reviewer_user_id = reviewer.user_id
                WHERE cr.coach_id = :c_id
                ORDER BY cr.created_at DESC
                ;
            """,
            {"c_id": coach_id},
            fetch=True,
            commit=False
        )

        if not summary:
            coach_info = run_query(
                """
                    SELECT 
                        first_name AS coach_first_name,
                        last_name AS coach_last_name
                    FROM users_immutables
                    WHERE user_id = :c_id
                    ;
                """,
                {"c_id": coach_id},
                fetch=True,
                commit=False
            )

            if not coach_info:
                raise ValueError("Coach not found")

            return {
                "coach_avg_rating": None,
                "reviews": [],
                "coach_first_name": coach_info[0]["coach_first_name"],
                "coach_last_name": coach_info[0]["coach_last_name"]
            }

        return {
            "coach_avg_rating": summary[0]["coach_avg_rating"],
            "reviews": reviews,
            "coach_first_name": summary[0]["coach_first_name"],
            "coach_last_name": summary[0]["coach_last_name"]
        }

    except Exception as e:
        raise e
    

def clientKnowsCoach(user_id : int, coach_id : int):
    try: 
        ret = run_query(
            """
                select 
                    * 
                from 
                    clientKnowsCoach 
                where
                  coach_id = :c_id 
                  AND 
                  user_id = :u_id
                  ;
            """,
            {"u_id":user_id, "c_id":coach_id},
            fetch=True, 
            commit=False
        )

        if len(ret) > 0 :
            return True
        return False
        
    except Exception as e : 
        raise e

def postReview(user_id :int, coach_id: int, rating: int, review_text: str):
    try:
        run_query(
            """
                INSERT INTO coach_review 
                (
                    coach_id,
                    reviewer_user_id,
                    rating,
                    review_text
                )
                VALUES
                (
                    :c_id, 
                    :u_id,
                    :rate,
                    :review
                )
                ; 
            """,
            {"u_id": user_id, "c_id": coach_id, "rate": rating, "review": review_text},
            fetch=False, 
            commit=True
        )

    except Exception as e: 
        raise e