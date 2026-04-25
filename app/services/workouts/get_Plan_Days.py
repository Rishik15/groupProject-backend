from app.services import run_query


def get_plan_days(plan_id: int):
    return run_query(
        """
        SELECT
            wd.day_id,
            wd.day_order,
            wd.day_label,
            wp.plan_name
        FROM workout_day wd
        JOIN workout_plan wp ON wd.plan_id = wp.plan_id
        WHERE wd.plan_id = :plan_id
        ORDER BY wd.day_order ASC
        """,
        {"plan_id": plan_id},
        fetch=True, commit=False
    )