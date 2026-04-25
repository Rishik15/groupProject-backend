from app.services import run_query
from datetime import datetime

DAY_NAMES = {
    0: 'Mon', 1: 'Tue', 2: 'Wed',
    3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'
}


def assign_plan(requester_id: int, plan_id: int, day_assignments: list, target_user_id: int = None, force: bool = False, note: str = None):

    if not day_assignments:
        raise ValueError("day_assignments is required")

    # Determine if this is a self-assign or coach assign
    is_coach_assign = target_user_id and target_user_id != requester_id

    if is_coach_assign:
        # Verify active contract
        contract = run_query(
            """
            SELECT contract_id FROM user_coach_contract
            WHERE coach_id = :coach_id
            AND user_id = :client_id
            AND active = 1
            """,
            {"coach_id": requester_id, "client_id": target_user_id},
            fetch=True, commit=False
        )

        if not contract:
            raise PermissionError("No active contract found between this coach and client")

        assigned_to  = target_user_id
        coach_id     = requester_id
    else:
        assigned_to  = requester_id
        coach_id     = 1  # system user for self-assign

    # Collect all dates being assigned
    dates = [a["date"] for a in day_assignments]

    # Check for existing workout events on any of these dates
    existing = run_query(
        """
        SELECT e.event_id, e.event_date, wp.plan_name
        FROM event e
        JOIN workout_plan wp ON e.workout_plan_id = wp.plan_id
        WHERE e.user_id = :user_id
        AND e.event_type = 'workout'
        AND e.event_date IN :dates
        """,
        {"user_id": assigned_to, "dates": tuple(dates)},
        fetch=True, commit=False
    )

    if existing:
        if not force:
            conflicting_plan = existing[0]["plan_name"]
            conflicting_date = str(existing[0]["event_date"])
            raise ValueError(f"EXISTING_PLAN:{conflicting_plan}|{conflicting_date}")

        for row in existing:
            run_query(
                """
                DELETE FROM event WHERE event_id = :event_id
                """,
                {"event_id": row["event_id"]},
                fetch=False, commit=True
            )

    # Fetch plan name
    plan = run_query(
        "SELECT plan_name FROM workout_plan WHERE plan_id = :plan_id",
        {"plan_id": plan_id},
        fetch=True, commit=False
    )

    if not plan:
        raise ValueError("Workout plan not found")

    plan_name = plan[0]["plan_name"]

    # Insert assignment log
    run_query(
        """
        INSERT INTO coach_assignment_log
            (coach_id, user_id, assigned_type, workout_plan_id, assigned_at, note)
        VALUES
            (:coach_id, :user_id, 'workout_plan', :plan_id, NOW(), :note)
        """,
        {
            "coach_id": coach_id,
            "user_id": assigned_to,
            "plan_id": plan_id,
            "note": note or ("Self-assigned from predefined plan library" if not is_coach_assign else None)
        },
        fetch=False, commit=True
    )

    # Insert calendar + event rows for each assigned day
    for assignment in day_assignments:
        day_id   = assignment["day_id"]
        date_str = assignment["date"]

        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = DAY_NAMES[parsed_date.weekday()]

        # Verify day belongs to this plan
        day_info = run_query(
            """
            SELECT day_label FROM workout_day
            WHERE day_id = :day_id AND plan_id = :plan_id
            """,
            {"day_id": day_id, "plan_id": plan_id},
            fetch=True, commit=False
        )

        if not day_info:
            raise ValueError(f"day_id {day_id} does not belong to plan {plan_id}")

        day_label   = day_info[0]["day_label"]
        description = f"{plan_name} — {day_label}"

        run_query(
            """
            INSERT IGNORE INTO calendar (user_id, full_date, day_name)
            VALUES (:user_id, :full_date, :day_name)
            """,
            {
                "user_id": assigned_to,
                "full_date": date_str,
                "day_name": day_name
            },
            fetch=False, commit=True
        )

        run_query(
            """
            INSERT INTO event (user_id, event_date, event_type, description, workout_plan_id)
            VALUES (:user_id, :event_date, 'workout', :description, :workout_plan_id)
            """,
            {
                "user_id": assigned_to,
                "event_date": date_str,
                "description": description,
                "workout_plan_id": plan_id
            },
            fetch=False, commit=True
        )