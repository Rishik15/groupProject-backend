from app.services import run_query
from datetime import date, timedelta


def get_workout_completion_service(user_id: int):
    today = date.today()

    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    planned_rows = run_query(
        """
        SELECT 
            event_date,
            COUNT(*) as planned_count
        FROM event
        WHERE user_id = :user_id
        AND event_type = 'workout'
        AND event_date BETWEEN :start AND :end
        GROUP BY event_date
    """,
        {"user_id": user_id, "start": start_of_week, "end": end_of_week},
    )

    completed_rows = run_query(
        """
        SELECT 
            DATE(ended_at) as day,
            COUNT(*) as completed_count
        FROM workout_session
        WHERE user_id = :user_id
        AND ended_at IS NOT NULL
        AND DATE(ended_at) BETWEEN :start AND :end
        GROUP BY day
    """,
        {"user_id": user_id, "start": start_of_week, "end": end_of_week},
    )

    planned_map = {row["event_date"]: row["planned_count"] for row in planned_rows}
    completed_map = {row["day"]: row["completed_count"] for row in completed_rows}

    days = []
    total_planned = 0
    total_completed = 0

    for i in range(7):
        current_day = start_of_week + timedelta(days=i)

        planned = int(planned_map.get(current_day, 0))
        completed = int(completed_map.get(current_day, 0))

        total_planned += planned
        total_completed += completed

        days.append(
            {
                "day": current_day.strftime("%a"),
                "date": str(current_day),
                "planned": planned,
                "completed": completed,
            }
        )

    return {
        "days": days,
        "summary": {"planned": total_planned, "completed": total_completed},
    }
