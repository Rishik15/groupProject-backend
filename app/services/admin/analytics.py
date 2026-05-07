from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services import run_query
from app.services.admin.dashboard import _is_admin


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _get_local_today(user_timezone: str | None):
    valid_timezone = _get_valid_timezone(user_timezone)
    tz = ZoneInfo(valid_timezone)

    return datetime.now(tz).date()


def _local_day_range_to_utc(user_timezone: str | None, start_date, days: int):
    valid_timezone = _get_valid_timezone(user_timezone)
    tz = ZoneInfo(valid_timezone)

    start_local = datetime.combine(start_date, time.min, tzinfo=tz)
    end_local = start_local + timedelta(days=days)

    start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc = end_local.astimezone(timezone.utc).replace(tzinfo=None)

    return (
        start_utc.strftime("%Y-%m-%d %H:%M:%S"),
        end_utc.strftime("%Y-%m-%d %H:%M:%S"),
    )


def get_admin_engagement_analytics(user_id: int, user_timezone: str | None = None):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    today = _get_local_today(user_timezone)

    today_start_utc, today_end_utc = _local_day_range_to_utc(
        user_timezone,
        today,
        1,
    )

    week_start_utc, week_end_utc = _local_day_range_to_utc(
        user_timezone,
        today - timedelta(days=6),
        7,
    )

    month_start_utc, month_end_utc = _local_day_range_to_utc(
        user_timezone,
        today - timedelta(days=29),
        30,
    )

    daily_active_users = run_query(
        """
        SELECT COUNT(DISTINCT user_id) AS count
        FROM (
            SELECT user_id
            FROM workout_session
            WHERE started_at >= :today_start_utc
              AND started_at < :today_end_utc

            UNION

            SELECT user_id
            FROM cardio_log
            WHERE performed_at >= :today_start_utc
              AND performed_at < :today_end_utc

            UNION

            SELECT user_id
            FROM meal_log
            WHERE eaten_at >= :today_start_utc
              AND eaten_at < :today_end_utc

            UNION

            SELECT user_id
            FROM daily_metrics
            WHERE metric_date = :today

            UNION

            SELECT user_id
            FROM mental_wellness_survey
            WHERE survey_date = :today
        ) AS active_today
        """,
        params={
            "today_start_utc": today_start_utc,
            "today_end_utc": today_end_utc,
            "today": today,
        },
        fetch=True,
        commit=False,
    )[0]["count"]

    weekly_active_users = run_query(
        """
        SELECT COUNT(DISTINCT user_id) AS count
        FROM (
            SELECT user_id
            FROM workout_session
            WHERE started_at >= :week_start_utc
              AND started_at < :week_end_utc

            UNION

            SELECT user_id
            FROM cardio_log
            WHERE performed_at >= :week_start_utc
              AND performed_at < :week_end_utc

            UNION

            SELECT user_id
            FROM meal_log
            WHERE eaten_at >= :week_start_utc
              AND eaten_at < :week_end_utc

            UNION

            SELECT user_id
            FROM daily_metrics
            WHERE metric_date >= :week_start_date
              AND metric_date <= :today

            UNION

            SELECT user_id
            FROM mental_wellness_survey
            WHERE survey_date >= :week_start_date
              AND survey_date <= :today
        ) AS active_week
        """,
        params={
            "week_start_utc": week_start_utc,
            "week_end_utc": week_end_utc,
            "week_start_date": today - timedelta(days=6),
            "today": today,
        },
        fetch=True,
        commit=False,
    )[0]["count"]

    monthly_active_users = run_query(
        """
        SELECT COUNT(DISTINCT user_id) AS count
        FROM (
            SELECT user_id
            FROM workout_session
            WHERE started_at >= :month_start_utc
              AND started_at < :month_end_utc

            UNION

            SELECT user_id
            FROM cardio_log
            WHERE performed_at >= :month_start_utc
              AND performed_at < :month_end_utc

            UNION

            SELECT user_id
            FROM meal_log
            WHERE eaten_at >= :month_start_utc
              AND eaten_at < :month_end_utc

            UNION

            SELECT user_id
            FROM daily_metrics
            WHERE metric_date >= :month_start_date
              AND metric_date <= :today

            UNION

            SELECT user_id
            FROM mental_wellness_survey
            WHERE survey_date >= :month_start_date
              AND survey_date <= :today
        ) AS active_month
        """,
        params={
            "month_start_utc": month_start_utc,
            "month_end_utc": month_end_utc,
            "month_start_date": today - timedelta(days=29),
            "today": today,
        },
        fetch=True,
        commit=False,
    )[0]["count"]

    return {
        "daily_active_users": int(daily_active_users),
        "weekly_active_users": int(weekly_active_users),
        "monthly_active_users": int(monthly_active_users),
    }
