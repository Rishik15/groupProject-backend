from app.services import run_query


def submit_mental_survey_service(
    user_id,
    score,
    notes,
    today,
    weight=None,
    sleep_hours=None,
):
    survey_query = """
        INSERT INTO mental_wellness_survey (
            user_id,
            survey_date,
            mood_score,
            notes
        )
        VALUES (
            :user_id,
            :survey_date,
            :mood_score,
            :notes
        )
    """

    survey_params = {
        "user_id": user_id,
        "survey_date": today,
        "mood_score": score,
        "notes": notes,
    }

    run_query(
        survey_query,
        params=survey_params,
        fetch=False,
        commit=True,
    )

    if weight is None and sleep_hours is None:
        return True

    metrics_query = """
        INSERT INTO daily_metrics (
            user_id,
            metric_date,
            weight,
            sleep_hours
        )
        VALUES (
            :user_id,
            :metric_date,
            :weight,
            :sleep_hours
        )
        ON DUPLICATE KEY UPDATE
            weight = COALESCE(VALUES(weight), weight),
            sleep_hours = COALESCE(VALUES(sleep_hours), sleep_hours)
    """

    metrics_params = {
        "user_id": user_id,
        "metric_date": today,
        "weight": weight,
        "sleep_hours": sleep_hours,
    }

    run_query(
        metrics_query,
        params=metrics_params,
        fetch=False,
        commit=True,
    )

    return True
