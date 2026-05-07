from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services import run_query


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _get_month_start(year: int, month: int):
    return datetime(year, month, 1).date()


def _get_previous_month_start(year: int, month: int):
    if month == 1:
        return datetime(year - 1, 12, 1).date()

    return datetime(year, month - 1, 1).date()


def _get_next_month_start(year: int, month: int):
    if month == 12:
        return datetime(year + 1, 1, 1).date()

    return datetime(year, month + 1, 1).date()


def get_coach_metrics(coach_id: int, user_timezone: str | None = None):
    valid_timezone = _get_valid_timezone(user_timezone)
    today = datetime.now(ZoneInfo(valid_timezone)).date()

    current_month_start = _get_month_start(today.year, today.month)
    next_month_start = _get_next_month_start(today.year, today.month)
    previous_month_start = _get_previous_month_start(today.year, today.month)

    week_start = today - timedelta(days=today.weekday())
    next_week_start = week_start + timedelta(days=7)

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
        AND start_date >= :previous_month_start
        AND start_date < :current_month_start
        """,
        {
            "coach_id": coach_id,
            "previous_month_start": previous_month_start,
            "current_month_start": current_month_start,
        },
    )[0]["count"]

    client_diff = int(active_clients) - int(last_month_clients)

    revenue_mtd = run_query(
        """
        SELECT COALESCE(SUM(agreed_price), 0) as revenue
        FROM user_coach_contract
        WHERE coach_id = :coach_id
        AND start_date >= :current_month_start
        AND start_date < :next_month_start
        """,
        {
            "coach_id": coach_id,
            "current_month_start": current_month_start,
            "next_month_start": next_month_start,
        },
    )[0]["revenue"]

    revenue_last_month = run_query(
        """
        SELECT COALESCE(SUM(agreed_price), 0) as revenue
        FROM user_coach_contract
        WHERE coach_id = :coach_id
        AND start_date >= :previous_month_start
        AND start_date < :current_month_start
        """,
        {
            "coach_id": coach_id,
            "previous_month_start": previous_month_start,
            "current_month_start": current_month_start,
        },
    )[0]["revenue"]

    revenue_diff = float(revenue_mtd) - float(revenue_last_month)

    sessions_week = run_query(
        """
        SELECT COUNT(*) as count
        FROM event
        WHERE event_type = 'coach_session'
        AND user_id IN (
            SELECT user_id
            FROM user_coach_contract
            WHERE coach_id = :coach_id
        )
        AND event_date >= :week_start
        AND event_date < :next_week_start
        """,
        {
            "coach_id": coach_id,
            "week_start": week_start,
            "next_week_start": next_week_start,
        },
    )[0]["count"]

    sessions_month = run_query(
        """
        SELECT COUNT(*) as count
        FROM event
        WHERE event_type = 'coach_session'
        AND user_id IN (
            SELECT user_id
            FROM user_coach_contract
            WHERE coach_id = :coach_id
        )
        AND event_date >= :current_month_start
        AND event_date < :next_month_start
        """,
        {
            "coach_id": coach_id,
            "current_month_start": current_month_start,
            "next_month_start": next_month_start,
        },
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
        "activeClients": {
            "count": int(active_clients),
            "diff": client_diff,
        },
        "revenue": {
            "amount": float(revenue_mtd),
            "diff": float(revenue_diff),
        },
        "sessions": {
            "week": int(sessions_week),
            "month": int(sessions_month),
        },
        "rating": {
            "avg": round(float(rating_data["avg_rating"]), 1),
            "count": int(rating_data["total_reviews"]),
        },
    }
