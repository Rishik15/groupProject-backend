from app.services import run_query


def get_coach_metrics(coach_id: int):

    active_clients = run_query(
        """
        SELECT COUNT(*) as count
        FROM user_coach_contract
        WHERE coach_id = :coach_id
        AND active = 1
        """,
        {"coach_id": coach_id},
    )[0]["count"]

    last_month_clients = run_query(
        """
        SELECT COUNT(*) as count
        FROM user_coach_contract
        WHERE coach_id = :coach_id
        AND active = 1
        AND MONTH(start_date) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
        AND YEAR(start_date) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
        """,
        {"coach_id": coach_id},
    )[0]["count"]

    client_diff = active_clients - last_month_clients

    revenue_mtd = run_query(
        """
        SELECT COALESCE(SUM(agreed_price), 0) as revenue
        FROM user_coach_contract
        WHERE coach_id = :coach_id
        AND MONTH(start_date) = MONTH(CURDATE())
        AND YEAR(start_date) = YEAR(CURDATE())
        """,
        {"coach_id": coach_id},
    )[0]["revenue"]

    revenue_last_month = run_query(
        """
        SELECT COALESCE(SUM(agreed_price), 0) as revenue
        FROM user_coach_contract
        WHERE coach_id = :coach_id
        AND MONTH(start_date) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
        AND YEAR(start_date) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
        """,
        {"coach_id": coach_id},
    )[0]["revenue"]

    revenue_diff = revenue_mtd - revenue_last_month

    sessions_week = run_query(
        """
        SELECT COUNT(*) as count
        FROM event
        WHERE event_type = 'coach_session'
        AND user_id IN (
            SELECT user_id FROM user_coach_contract WHERE coach_id = :coach_id
        )
        AND YEARWEEK(event_date, 1) = YEARWEEK(CURDATE(), 1)
        """,
        {"coach_id": coach_id},
    )[0]["count"]

    sessions_month = run_query(
        """
        SELECT COUNT(*) as count
        FROM event
        WHERE event_type = 'coach_session'
        AND user_id IN (
            SELECT user_id FROM user_coach_contract WHERE coach_id = :coach_id
        )
        AND MONTH(event_date) = MONTH(CURDATE())
        AND YEAR(event_date) = YEAR(CURDATE())
        """,
        {"coach_id": coach_id},
    )[0]["count"]

    rating_data = run_query(
        """
        SELECT 
            COALESCE(AVG(rating), 0) as avg_rating,
            COUNT(*) as total_reviews
        FROM coach_review
        WHERE coach_id = :coach_id
        """,
        {"coach_id": coach_id},
    )[0]

    return {
        "activeClients": {"count": active_clients, "diff": client_diff},
        "revenue": {"amount": float(revenue_mtd), "diff": float(revenue_diff)},
        "sessions": {"week": sessions_week, "month": sessions_month},
        "rating": {
            "avg": round(float(rating_data["avg_rating"]), 1),
            "count": rating_data["total_reviews"],
        },
    }
