from app.services import run_query


def getClientGrowthLast3Months(coach_id: int):
    results = run_query(
        """
        SELECT 
            DATE_FORMAT(start_date, '%b') AS month,
            MONTH(start_date) AS month_num,
            COUNT(*) AS new_clients
        FROM user_coach_contract
        WHERE coach_id = :coach_id
        AND start_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
        GROUP BY MONTH(start_date), DATE_FORMAT(start_date, '%b')
        ORDER BY month_num
        """,
        {"coach_id": coach_id},
    )

    return results
