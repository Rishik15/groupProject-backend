from app.services import run_query


def delete_meal_plan(user_id, meal_plan_id):
    owner_check = run_query(
        """
        SELECT meal_plan_id FROM meal_plan
        WHERE meal_plan_id = :meal_plan_id AND user_id = :user_id
        """,
        {"meal_plan_id": meal_plan_id, "user_id": user_id},
        fetch=True, commit=False
    )

    if not owner_check:
        raise PermissionError("Meal plan not found or does not belong to this user")

    run_query(
        """
        DELETE FROM meal_plan
        WHERE meal_plan_id = :meal_plan_id AND user_id = :user_id
        """,
        {"meal_plan_id": meal_plan_id, "user_id": user_id},
        fetch=False, commit=True
    )