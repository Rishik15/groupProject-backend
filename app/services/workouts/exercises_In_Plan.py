from app.services import run_query


def get_workout_plan_exercises(plan_id: int):
    query = """
        SELECT
            wd.day_id,
            wd.day_order,
            wd.day_label,

            pe.exercise_id,
            pe.order_in_workout,
            pe.sets_goal,
            pe.reps_goal,
            pe.weight_goal,

            e.exercise_name,
            e.equipment,
            e.video_url
        FROM workout_day wd
        LEFT JOIN plan_exercise pe ON pe.day_id = wd.day_id
        LEFT JOIN exercise e ON pe.exercise_id = e.exercise_id
        WHERE wd.plan_id = :plan_id
        ORDER BY wd.day_order ASC, pe.order_in_workout ASC
    """

    rows = run_query(query, params={"plan_id": plan_id}, fetch=True, commit=False)

    days_map = {}

    for row in rows:
        day_id = row["day_id"]

        if day_id not in days_map:
            days_map[day_id] = {
                "day_id": row["day_id"],
                "day_order": row["day_order"],
                "day_label": row["day_label"] or f"Day {row['day_order']}",
                "exercises": [],
            }

        if row["exercise_id"] is not None:
            days_map[day_id]["exercises"].append(
                {
                    "exercise_id": row["exercise_id"],
                    "exercise_name": row["exercise_name"],
                    "equipment": row["equipment"],
                    "video_url": row["video_url"],
                    "sets_goal": row["sets_goal"],
                    "reps_goal": row["reps_goal"],
                    "weight_goal": row["weight_goal"],
                    "order_in_workout": row["order_in_workout"],
                }
            )

    return list(days_map.values())
