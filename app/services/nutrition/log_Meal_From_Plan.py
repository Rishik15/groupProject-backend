from app.services import run_query
from app.services.media import save_meal_image_for_user


def log_meal_from_plan(
    user_id,
    meal_id,
    servings,
    eaten_at,
    notes=None,
    uploaded_file=None,
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
            "eaten_at": eaten_at,
            "servings": servings,
            "notes": notes,
            "photo_url": photo_url,
        },
        fetch=False,
        commit=True,
    )

    return photo_url
