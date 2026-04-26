from datetime import datetime
from app.services import run_query
from app.services.media import save_meal_image_for_user


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
):
    eaten_dt = datetime.fromisoformat(eaten_at)

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
        run_query(
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
        )

        created = run_query(
            "SELECT LAST_INSERT_ID() AS food_item_id",
            fetch=True,
            commit=False,
        )

        food_item_id = created[0]["food_item_id"]

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
            "eaten_at": eaten_dt.isoformat(),
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
