from app.services import run_query
from datetime import datetime, timedelta

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def get_week_monday(date: datetime) -> datetime:
    days_since_monday = date.weekday()
    return date - timedelta(days=days_since_monday)


def delete_meal_events_for_week(user_id: int, monday: datetime):
    for index in range(7):
        day_date = monday + timedelta(days=index)

        run_query(
            """
            DELETE FROM event
            WHERE user_id = :user_id
            AND event_date = :event_date
            AND event_type = 'meal'
            """,
            {
                "user_id": user_id,
                "event_date": day_date.strftime("%Y-%m-%d"),
            },
            fetch=False,
            commit=True,
        )


def create_meal_events_for_week(user_id: int, monday: datetime, plan_name: str):
    for index in range(7):
        day_date = monday + timedelta(days=index)
        day_name = DAY_NAMES[index]
        date_str = day_date.strftime("%Y-%m-%d")

        run_query(
            """
            INSERT IGNORE INTO calendar
            (
                user_id,
                full_date,
                day_name
            )
            VALUES
            (
                :user_id,
                :full_date,
                :day_name
            )
            """,
            {
                "user_id": user_id,
                "full_date": date_str,
                "day_name": day_name,
            },
            fetch=False,
            commit=True,
        )

        run_query(
            """
            INSERT INTO event
            (
                user_id,
                event_date,
                event_type,
                description
            )
            VALUES
            (
                :user_id,
                :event_date,
                'meal',
                :description
            )
            """,
            {
                "user_id": user_id,
                "event_date": date_str,
                "description": plan_name,
            },
            fetch=False,
            commit=True,
        )


def assign_meal_plan(
    user_id: int,
    meal_plan_id: int,
    start_date: str = None,
    force: bool = False,
):
    if start_date:
        parsed = datetime.strptime(start_date, "%Y-%m-%d")
        monday = get_week_monday(parsed)
    else:
        monday = get_week_monday(datetime.now())

    sunday = monday + timedelta(days=6)

    monday_str = monday.strftime("%Y-%m-%d")
    sunday_str = sunday.strftime("%Y-%m-%d")

    existing = run_query(
        """
        SELECT meal_plan_id, plan_name
        FROM meal_plan
        WHERE user_id = :user_id
        AND start_date = :start_date
        AND meal_plan_id != :meal_plan_id
        """,
        {
            "user_id": user_id,
            "start_date": monday_str,
            "meal_plan_id": meal_plan_id,
        },
        fetch=True,
        commit=False,
    )

    if existing:
        if not force:
            raise ValueError(f"EXISTING_PLAN:{existing[0]['plan_name']}")

        delete_meal_events_for_week(user_id, monday)

        run_query(
            """
            DELETE FROM meal_plan
            WHERE meal_plan_id = :meal_plan_id
            AND user_id = :user_id
            """,
            {
                "meal_plan_id": existing[0]["meal_plan_id"],
                "user_id": user_id,
            },
            fetch=False,
            commit=True,
        )

    plan = run_query(
        """
        SELECT meal_plan_id, user_id, plan_name, total_calories
        FROM meal_plan
        WHERE meal_plan_id = :meal_plan_id
        AND user_id IN (1, :user_id)
        """,
        {
            "meal_plan_id": meal_plan_id,
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    if not plan:
        raise ValueError("Meal plan not found")

    plan = plan[0]

    if int(plan["user_id"]) == int(user_id):
        run_query(
            """
            UPDATE meal_plan
            SET start_date = :start_date,
                end_date = :end_date
            WHERE meal_plan_id = :meal_plan_id
            AND user_id = :user_id
            """,
            {
                "start_date": monday_str,
                "end_date": sunday_str,
                "meal_plan_id": meal_plan_id,
                "user_id": user_id,
            },
            fetch=False,
            commit=True,
        )

        delete_meal_events_for_week(user_id, monday)
        create_meal_events_for_week(user_id, monday, plan["plan_name"])

        return meal_plan_id

    new_plan_id = run_query(
        """
        INSERT INTO meal_plan
        (
            user_id,
            plan_name,
            start_date,
            end_date,
            total_calories
        )
        VALUES
        (
            :user_id,
            :plan_name,
            :start_date,
            :end_date,
            :total_calories
        )
        """,
        {
            "user_id": user_id,
            "plan_name": plan["plan_name"],
            "start_date": monday_str,
            "end_date": sunday_str,
            "total_calories": plan["total_calories"],
        },
        fetch=False,
        commit=True,
        return_lastrowid=True,
    )

    if not new_plan_id:
        raise ValueError("Failed to create assigned meal plan")

    user_meals = run_query(
        """
        SELECT meal_id, meal_type, servings, day_of_week
        FROM user_meal
        WHERE meal_plan_id = :meal_plan_id
        """,
        {
            "meal_plan_id": meal_plan_id,
        },
        fetch=True,
        commit=False,
    )

    for meal in user_meals:
        run_query(
            """
            INSERT INTO user_meal
            (
                meal_id,
                meal_plan_id,
                meal_type,
                servings,
                day_of_week
            )
            VALUES
            (
                :meal_id,
                :meal_plan_id,
                :meal_type,
                :servings,
                :day_of_week
            )
            """,
            {
                "meal_id": meal["meal_id"],
                "meal_plan_id": new_plan_id,
                "meal_type": meal["meal_type"],
                "servings": meal["servings"],
                "day_of_week": meal["day_of_week"],
            },
            fetch=False,
            commit=True,
        )

    create_meal_events_for_week(user_id, monday, plan["plan_name"])

    return new_plan_id
