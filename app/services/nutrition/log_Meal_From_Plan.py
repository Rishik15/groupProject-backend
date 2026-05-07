from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services import run_query
from app.services.media import save_meal_image_for_user


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _local_input_to_utc_string(value: str, user_timezone: str | None):
    if value is None or str(value).strip() == "":
        raise ValueError("eaten_at is required")

    cleaned_value = str(value).strip().replace("Z", "+00:00")

    try:
        parsed_datetime = datetime.fromisoformat(cleaned_value)
    except ValueError:
        raise ValueError("eaten_at must be a valid datetime")

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(
            tzinfo=ZoneInfo(_get_valid_timezone(user_timezone))
        )

    utc_datetime = parsed_datetime.astimezone(timezone.utc)

    return utc_datetime.strftime("%Y-%m-%d %H:%M:%S")


def log_meal_from_plan(
    user_id,
    meal_id,
    servings,
    eaten_at,
    notes=None,
    uploaded_file=None,
    user_timezone: str | None = None,
):
    meal = run_query(
        """
        SELECT meal_id
        FROM meal
        WHERE meal_id = :meal_id
        """,
        {"meal_id": meal_id},
        fetch=True,
        commit=False,
    )

    if not meal:
        raise ValueError("Meal not found")

    eaten_at_utc = _local_input_to_utc_string(eaten_at, user_timezone)

    photo_url = None

    if uploaded_file:
        result = save_meal_image_for_user(user_id, uploaded_file)
        photo_url = result["photo_url"]

    run_query(
        """
        INSERT INTO meal_log
        (
            user_id,
            meal_id,
            food_item_id,
            eaten_at,
            servings,
            notes,
            photo_url
        )
        VALUES
        (
            :user_id,
            :meal_id,
            NULL,
            :eaten_at,
            :servings,
            :notes,
            :photo_url
        )
        """,
        {
            "user_id": user_id,
            "meal_id": meal_id,
            "eaten_at": eaten_at_utc,
            "servings": servings,
            "notes": notes,
            "photo_url": photo_url,
        },
        fetch=False,
        commit=True,
    )

    return photo_url
