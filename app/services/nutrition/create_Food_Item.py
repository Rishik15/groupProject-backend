from app.services import run_query


def create_food_item(user_id: int, name: str, calories: int, protein: float, carbs: float, fats: float, image_url: str = None):
    run_query(
        """
        INSERT INTO food_item (user_id, name, calories, protein, carbs, fats, image_url)
        VALUES (:user_id, :name, :calories, :protein, :carbs, :fats, :image_url)
        """,
        {
            "user_id": user_id,
            "name": name,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fats": fats,
            "image_url": image_url
        },
        fetch=False, commit=True
    )