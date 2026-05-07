from datetime import datetime
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


def getClientGrowthLast3Months(coach_id: int, user_timezone: str | None = None):
    valid_timezone = _get_valid_timezone(user_timezone)
    today = datetime.now(ZoneInfo(valid_timezone)).date()

    results = run_query(
        """
        SELECT 
            DATE_FORMAT(start_date, '%b') AS month,
            MONTH(start_date) AS month_num,
            YEAR(start_date) AS year_num,
            COUNT(*) AS new_clients
        FROM user_coach_contract
        WHERE coach_id = :coach_id
        AND start_date >= DATE_SUB(:today, INTERVAL 3 MONTH)
        GROUP BY
            YEAR(start_date),
            MONTH(start_date),
            DATE_FORMAT(start_date, '%b')
        ORDER BY year_num ASC, month_num ASC
        """,
        {
            "coach_id": coach_id,
            "today": today,
        },
    )

    return results
