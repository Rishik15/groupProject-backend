from app.services import run_query
from app.services.admin.dashboard import _is_admin


def get_admin_engagement_analytics(user_id: int):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    daily_active_users = run_query(
        """
        SELECT COUNT(DISTINCT user_id) AS count
        FROM (
            SELECT user_id
            FROM workout_session
            WHERE DATE(started_at) = CURDATE()

            UNION

            SELECT user_id
            FROM cardio_log
            WHERE DATE(performed_at) = CURDATE()

            UNION

            SELECT user_id
            FROM meal_log
            WHERE DATE(eaten_at) = CURDATE()

            UNION

            SELECT user_id
            FROM daily_metrics
            WHERE metric_date = CURDATE()

            UNION

            SELECT user_id
            FROM mental_wellness_survey
            WHERE survey_date = CURDATE()
        ) AS active_today
        """,
        fetch=True,
        commit=False
    )[0]["count"]

    weekly_active_users = run_query(
        """
        SELECT COUNT(DISTINCT user_id) AS count
        FROM (
            SELECT user_id
            FROM workout_session
            WHERE DATE(started_at) >= CURDATE() - INTERVAL 7 DAY

            UNION

            SELECT user_id
            FROM cardio_log
            WHERE DATE(performed_at) >= CURDATE() - INTERVAL 7 DAY

            UNION

            SELECT user_id
            FROM meal_log
            WHERE DATE(eaten_at) >= CURDATE() - INTERVAL 7 DAY

            UNION

            SELECT user_id
            FROM daily_metrics
            WHERE metric_date >= CURDATE() - INTERVAL 7 DAY

            UNION

            SELECT user_id
            FROM mental_wellness_survey
            WHERE survey_date >= CURDATE() - INTERVAL 7 DAY
        ) AS active_week
        """,
        fetch=True,
        commit=False
    )[0]["count"]

    monthly_active_users = run_query(
        """
        SELECT COUNT(DISTINCT user_id) AS count
        FROM (
            SELECT user_id
            FROM workout_session
            WHERE DATE(started_at) >= CURDATE() - INTERVAL 30 DAY

            UNION

            SELECT user_id
            FROM cardio_log
            WHERE DATE(performed_at) >= CURDATE() - INTERVAL 30 DAY

            UNION

            SELECT user_id
            FROM meal_log
            WHERE DATE(eaten_at) >= CURDATE() - INTERVAL 30 DAY

            UNION

            SELECT user_id
            FROM daily_metrics
            WHERE metric_date >= CURDATE() - INTERVAL 30 DAY

            UNION

            SELECT user_id
            FROM mental_wellness_survey
            WHERE survey_date >= CURDATE() - INTERVAL 30 DAY
        ) AS active_month
        """,
        fetch=True,
        commit=False
    )[0]["count"]

    return {
        "daily_active_users": int(daily_active_users),
        "weekly_active_users": int(weekly_active_users),
        "monthly_active_users": int(monthly_active_users),
    }