from app.services import run_query
from datetime import datetime, timedelta

DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def get_week_monday(date: datetime) -> datetime:
    days_since_monday = date.weekday()
    return date - timedelta(days=days_since_monday)


def assign_meal_plan(user_id: int, meal_plan_id: int, start_date: str = None, force: bool = False):

    # Determine the Monday to start from
    if start_date:
        parsed = datetime.strptime(start_date, "%Y-%m-%d")
        monday = get_week_monday(parsed)
    else:
        monday = get_week_monday(datetime.now())

    sunday = monday + timedelta(days=6)

    # Check if user already has a plan assigned for this week
    existing = run_query(
        """
        SELECT meal_plan_id, plan_name FROM meal_plan
        WHERE user_id = :user_id
        AND start_date = :start_date
        """,
        {
            "user_id": user_id,
            "start_date": monday.strftime("%Y-%m-%d")
        },
        fetch=True, commit=False
    )

    if existing:
        if not force:
            raise ValueError(f"EXISTING_PLAN:{existing[0]['plan_name']}")

        # Force replace — delete existing plan (cascades to user_meal)
        run_query(
            """
            DELETE FROM meal_plan
            WHERE meal_plan_id = :meal_plan_id AND user_id = :user_id
            """,
            {
                "meal_plan_id": existing[0]["meal_plan_id"],
                "user_id": user_id
            },
            fetch=False, commit=True
        )

        # Also delete existing calendar events for this week
        for i in range(7):
            day_date = monday + timedelta(days=i)
            run_query(
                """
                DELETE FROM event
                WHERE user_id = :user_id
                AND event_date = :event_date
                AND event_type = 'meal'
                """,
                {
                    "user_id": user_id,
                    "event_date": day_date.strftime("%Y-%m-%d")
                },
                fetch=False, commit=True
            )

    # Fetch the system plan details
    plan = run_query(
        """
        SELECT plan_name, total_calories FROM meal_plan
        WHERE meal_plan_id = :meal_plan_id
        """,
        {"meal_plan_id": meal_plan_id},
        fetch=True, commit=False
    )

    if not plan:
        raise ValueError("Meal plan not found")

    plan = plan[0]

    # Copy the plan for the user
    run_query(
        """
        INSERT INTO meal_plan (user_id, plan_name, start_date, end_date, total_calories)
        VALUES (:user_id, :plan_name, :start_date, :end_date, :total_calories)
        """,
        {
            "user_id": user_id,
            "plan_name": plan["plan_name"],
            "start_date": monday.strftime("%Y-%m-%d"),
            "end_date": sunday.strftime("%Y-%m-%d"),
            "total_calories": plan["total_calories"]
        },
        fetch=False, commit=True
    )

    # Get the new plan ID
    result = run_query(
        "SELECT LAST_INSERT_ID() AS meal_plan_id",
        fetch=True, commit=False
    )
    new_plan_id = result[0]["meal_plan_id"]

    # Copy user_meal rows from the system plan
    user_meals = run_query(
        """
        SELECT meal_id, meal_type, servings, day_of_week
        FROM user_meal
        WHERE meal_plan_id = :meal_plan_id
        """,
        {"meal_plan_id": meal_plan_id},
        fetch=True, commit=False
    )

    for meal in user_meals:
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

    # Insert calendar + event rows for Mon-Sun
    for i in range(7):
        day_date = monday + timedelta(days=i)
        day_name = DAY_NAMES[i]
        date_str = day_date.strftime("%Y-%m-%d")

        # Insert calendar row (ignore if already exists for this user/date)
        run_query(
            """
            INSERT IGNORE INTO calendar (user_id, full_date, day_name)
            VALUES (:user_id, :full_date, :day_name)
            """,
            {
                "user_id": user_id,
                "full_date": date_str,
                "day_name": day_name
            },
            fetch=False, commit=True
        )

        # Insert meal event for this day
        run_query(
            """
            INSERT INTO event (user_id, event_date, event_type, description)
            VALUES (:user_id, :event_date, 'meal', :description)
            """,
            {
                "user_id": user_id,
                "event_date": date_str,
                "description": plan["plan_name"]
            },
            fetch=False, commit=True
        )

    return new_plan_id