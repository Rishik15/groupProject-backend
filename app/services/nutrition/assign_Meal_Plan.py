from app.services import run_query
from datetime import date, timedelta


DAY_ORDER = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def get_week_start():
    """Returns this Monday's date. If today is Monday, returns today."""
    today = date.today()
    days_since_monday = today.weekday()
    return today - timedelta(days=days_since_monday)


def assign_meal_plan(user_id: int, plan_id: int):
    """
    Assigns a system meal plan to a user.
    - Copies the plan into meal_plan owned by the user
    - Copies all user_meal rows to the new plan
    - Inserts calendar rows for Mon-Sun of the current week
    - Inserts one meal event per day into the event table
    """

    system_plan = run_query(
        """
        SELECT plan_name, total_calories
        FROM meal_plan
        WHERE meal_plan_id = :plan_id AND user_id = 1
        """,
        {"plan_id": plan_id},
        fetch=True, commit=False
    )

    if not system_plan:
        raise Exception("System meal plan not found")

    plan_name = system_plan[0]["plan_name"]
    total_calories = system_plan[0]["total_calories"]

    existing = run_query(
        """
        SELECT meal_plan_id FROM meal_plan
        WHERE user_id = :user_id AND plan_name = :plan_name
        """,
        {"user_id": user_id, "plan_name": plan_name},
        fetch=True, commit=False
    )

    if existing:
        raise Exception("You already have a meal plan with this name")

    week_start = get_week_start()

    run_query(
        """
        INSERT INTO meal_plan (user_id, plan_name, start_date, total_calories)
        VALUES (:user_id, :plan_name, :start_date, :total_calories)
        """,
        {
            "user_id": user_id,
            "plan_name": plan_name,
            "start_date": week_start,
            "total_calories": total_calories
        },
        fetch=False, commit=True
    )

    new_plan = run_query(
        """
        SELECT meal_plan_id FROM meal_plan
        WHERE user_id = :user_id AND plan_name = :plan_name
        ORDER BY meal_plan_id DESC
        LIMIT 1
        """,
        {"user_id": user_id, "plan_name": plan_name},
        fetch=True, commit=False
    )

    new_plan_id = new_plan[0]["meal_plan_id"]

    system_meals = run_query(
        """
        SELECT meal_id, meal_type, servings, day_of_week
        FROM user_meal
        WHERE meal_plan_id = :plan_id
        """,
        {"plan_id": plan_id},
        fetch=True, commit=False
    )

    for meal in system_meals:
        run_query(
            """
            INSERT INTO user_meal (meal_id, meal_plan_id, meal_type, servings, day_of_week)
            VALUES (:meal_id, :meal_plan_id, :meal_type, :servings, :day_of_week)
            """,
            {
                "meal_id": meal["meal_id"],
                "meal_plan_id": new_plan_id,
                "meal_type": meal["meal_type"],
                "servings": meal["servings"],
                "day_of_week": meal["day_of_week"]
            },
            fetch=False, commit=True
        )

    for i, day_name in enumerate(DAY_ORDER):
        day_date = week_start + timedelta(days=i)

        existing_cal = run_query(
            """
            SELECT calendar_id FROM calendar
            WHERE user_id = :user_id AND full_date = :full_date
            """,
            {"user_id": user_id, "full_date": day_date},
            fetch=True, commit=False
        )

        if not existing_cal:
            run_query(
                """
                INSERT INTO calendar (user_id, full_date, day_name)
                VALUES (:user_id, :full_date, :day_name)
                """,
                {
                    "user_id": user_id,
                    "full_date": day_date,
                    "day_name": day_name
                },
                fetch=False, commit=True
            )

        run_query(
            """
            INSERT INTO event (user_id, event_date, event_type, description)
            VALUES (:user_id, :event_date, 'meal', :description)
            """,
            {
                "user_id": user_id,
                "event_date": day_date,
                "description": f"{plan_name} - {day_name}"
            },
            fetch=False, commit=True
        )