from app.services import run_query
def getTopFiveCoaches(): 
    try: 
        return run_query(
            """
                SELECT 
                    c.coach_id,
                    ui.first_name,
                    ui.last_name,
                    ui.email,
                    c.coach_description,
                    c.price,
                    ROUND(AVG(cr.rating), 2) AS avg_rating,
                    COUNT(cr.review_id) AS review_count
                FROM coach c
                JOIN users_immutables ui
                    ON c.coach_id = ui.user_id
                LEFT JOIN coach_review cr
                    ON c.coach_id = cr.coach_id
                GROUP BY 
                    c.coach_id,
                    ui.first_name,
                    ui.last_name,
                    ui.email,
                    c.coach_description,
                    c.price
                HAVING COUNT(cr.review_id) > 0
                ORDER BY 
                    avg_rating DESC,
                    review_count DESC
                LIMIT 5;
            """,
            {},
            fetch=True,
            commit=False,
        )
    except Exception as e: 
        raise e