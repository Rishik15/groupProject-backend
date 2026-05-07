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


def log_food_item(
    user_id: int,
    name: str,
    calories: int,
    protein: float,
    carbs: float,
    fats: float,
    servings: float,
    eaten_at: str,
    notes: str | None = None,
    uploaded_file=None,
    user_timezone: str | None = None,
):
    eaten_at_utc = _local_input_to_utc_string(eaten_at, user_timezone)

    photo_url = None

    if uploaded_file:
        result = save_meal_image_for_user(user_id, uploaded_file)
        photo_url = result["photo_url"]

    existing = run_query(
        """
        SELECT food_item_id
        FROM food_item
        WHERE user_id = :user_id
        AND LOWER(name) = LOWER(:name)
        LIMIT 1
        """,
        {
            "user_id": user_id,
            "name": name,
        },
        fetch=True,
        commit=False,
    )

    if existing:
        food_item_id = existing[0]["food_item_id"]

        run_query(
            """
            UPDATE food_item
            SET
                calories = :calories,
                protein = :protein,
                carbs = :carbs,
                fats = :fats,
                image_url = COALESCE(:image_url, image_url)
            WHERE food_item_id = :food_item_id
            AND user_id = :user_id
            """,
            {
                "food_item_id": food_item_id,
                "user_id": user_id,
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fats": fats,
                "image_url": photo_url,
            },
            fetch=False,
            commit=True,
        )

    else:
        food_item_id = run_query(
            """
            INSERT INTO food_item
            (
                user_id,
                name,
                calories,
                protein,
                carbs,
                fats,
                image_url
            )
            VALUES
            (
                :user_id,
                :name,
                :calories,
                :protein,
                :carbs,
                :fats,
                :image_url
            )
            """,
            {
                "user_id": user_id,
                "name": name,
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fats": fats,
                "image_url": photo_url,
            },
            fetch=False,
            commit=True,
            return_lastrowid=True,
        )

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
            NULL,
            :food_item_id,
            :eaten_at,
            :servings,
            :notes,
            :photo_url
        )
        """,
        {
            "user_id": user_id,
            "food_item_id": food_item_id,
            "eaten_at": eaten_at_utc,
            "servings": servings,
            "notes": notes,
            "photo_url": photo_url,
        },
        fetch=False,
        commit=True,
    )

    return {
        "food_item_id": food_item_id,
        "photo_url": photo_url,
    }
