from app.services import run_query


def get_my_exercises(coach_id):
    # returns this coach's own exercises
    return run_query(
        """
        SELECT
            exercise_id,
            exercise_name,
            equipment,
            description,
            video_url,
            created_by
        FROM exercise
        WHERE created_by = :coach_id
        ORDER BY created_by ASC, exercise_name ASC
        """,
        {"coach_id": coach_id},
        fetch=True, commit=False
    )