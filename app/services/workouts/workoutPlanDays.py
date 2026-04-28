from app.services import run_query


def get_workout_plan_days(user_id: int, plan_id: int):
    rows = run_query(
        """
        SELECT
            wd.day_id,
            wd.plan_id,
            wd.day_order,
            wd.day_label,
            COUNT(pe.exercise_id) AS total_exercises
        FROM workout_day wd
        LEFT JOIN plan_exercise pe
            ON pe.day_id = wd.day_id
        WHERE wd.plan_id = :plan_id
        AND (
            EXISTS (
                SELECT 1
                FROM workout_plan_template wpt
                WHERE wpt.plan_id = wd.plan_id
                AND wpt.author_user_id = :user_id
            )
            OR EXISTS (
                SELECT 1
                FROM coach_assignment_log cal
                WHERE cal.workout_plan_id = wd.plan_id
                AND cal.user_id = :user_id
            )
        )
        GROUP BY wd.day_id, wd.plan_id, wd.day_order, wd.day_label
        ORDER BY wd.day_order ASC
        """,
        {
            "user_id": user_id,
            "plan_id": plan_id,
        },
        fetch=True,
        commit=False,
    )

    return rows or []
