from app.services import run_query

def get_user_nutrition_goals(user_id: int):
    goals = run_query(
        """
        SELECT
            user_id,
            calories_target,
            protein_target,
            carbs_target,
            fat_target,
            created_at,
            updated_at
        FROM user_nutrition_goals
        WHERE user_id = :user_id
        """,
        {
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    if not goals:
        return None

    return goals[0]


def upsert_user_nutrition_goals(
    user_id: int,
    calories_target=None,
    protein_target=None,
    carbs_target=None,
    fat_target=None,
):
    run_query(
        """
        INSERT INTO user_nutrition_goals (
            user_id,
            calories_target,
            protein_target,
            carbs_target,
            fat_target
        )
        VALUES (
            :user_id,
            :calories_target,
            :protein_target,
            :carbs_target,
            :fat_target
        )
        ON DUPLICATE KEY UPDATE
            calories_target = VALUES(calories_target),
            protein_target = VALUES(protein_target),
            carbs_target = VALUES(carbs_target),
            fat_target = VALUES(fat_target)
        """,
        {
            "user_id": user_id,
            "calories_target": calories_target,
            "protein_target": protein_target,
            "carbs_target": carbs_target,
            "fat_target": fat_target,
        },
        fetch=False,
        commit=True,
    )

    return get_user_nutrition_goals(user_id)
