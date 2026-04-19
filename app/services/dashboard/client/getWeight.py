from app.services import run_query
from datetime import datetime, timedelta


def get_user_weight(user_id):
    rows = run_query(
        """
        SELECT 
            FLOOR(DATEDIFF(metric_date, first_date) / 7) + 1 AS week_number,
            AVG(weight) as avg_weight
        FROM daily_metrics,
        (
            SELECT MIN(metric_date) as first_date
            FROM daily_metrics
            WHERE user_id = :user_id
        ) as start
        WHERE user_id = :user_id
        GROUP BY week_number
        ORDER BY week_number ASC
        """,
        {"user_id": user_id},
    )

    data_map = {int(row["week_number"]): float(row["avg_weight"]) for row in rows}

    if not data_map:
        return []

    max_week = max(data_map.keys())

    weeks = []
    last_value = None
    seen_real_data = False

    start_week = max(1, max_week - 3)

    for week in range(start_week, max_week + 1):
        if week in data_map:
            value = data_map[week]
            last_value = value
            seen_real_data = True
        else:
            if not seen_real_data:
                value = 0
            else:
                value = last_value

        weeks.append({"week": f"W{week}", "avg_weight": value})

    return weeks
