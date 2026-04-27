import json
from datetime import date, datetime, time

from app import socketio
from app.services import run_query


CLIENT_WORKOUT_ROUTE = "/client/workouts"


def date_to_string(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date().isoformat()

    if isinstance(value, date):
        return value.isoformat()

    return str(value)


def time_to_string(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.strftime("%H:%M:%S")

    if isinstance(value, time):
        return value.strftime("%H:%M:%S")

    return str(value)


def make_json_safe(value):
    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, time):
        return value.strftime("%H:%M:%S")

    if isinstance(value, list):
        return [make_json_safe(item) for item in value]

    if isinstance(value, dict):
        return {key: make_json_safe(item) for key, item in value.items()}

    return value


def parse_notification_metadata(metadata):
    if not metadata:
        return {}

    if isinstance(metadata, dict):
        return metadata

    if isinstance(metadata, str):
        try:
            return json.loads(metadata)
        except Exception:
            return {}

    return {}


def serialize_event(row):
    if not row:
        return None

    description = row.get("description") or ""
    notes = row.get("notes") or ""

    title = description or "Coach Session"

    if row.get("client_first_name") and row.get("client_last_name"):
        title = (
            f"{title} • {row.get('client_first_name')} {row.get('client_last_name')}"
        )

    return {
        "id": str(row["event_id"]),
        "eventId": int(row["event_id"]),
        "userId": int(row["user_id"]),
        "title": title,
        "date": date_to_string(row.get("event_date")),
        "startTime": time_to_string(row.get("start_time")),
        "endTime": time_to_string(row.get("end_time")),
        "eventType": row.get("event_type"),
        "description": description,
        "notes": notes,
        "workoutPlanId": row.get("workout_plan_id"),
        "workoutPlanName": row.get("workout_plan_name"),
        "workoutDayId": row.get("workout_day_id"),
        "workoutDayLabel": row.get("workout_day_label"),
        "workoutDayOrder": row.get("workout_day_order"),
        "coachSessionId": row.get("coach_session_id"),
        "contractId": row.get("contract_id"),
        "coachId": row.get("coach_id"),
        "clientId": row.get("client_id"),
        "status": row.get("status"),
        "coachFirstName": row.get("coach_first_name"),
        "coachLastName": row.get("coach_last_name"),
        "clientFirstName": row.get("client_first_name"),
        "clientLastName": row.get("client_last_name"),
        "clientEmail": row.get("client_email"),
    }


def get_notification_by_id(notification_id: int):
    rows = run_query(
        """
        SELECT
            notification_id AS id,
            user_id,
            type,
            mode,
            conversation_id AS conversationId,
            reference_id AS referenceId,
            metadata,
            title,
            body,
            is_read AS isRead,
            created_at AS createdAt,
            updated_at AS updatedAt
        FROM notification
        WHERE notification_id = :notification_id
        LIMIT 1
        """,
        {
            "notification_id": notification_id,
        },
        fetch=True,
        commit=False,
    )

    if not rows:
        return None

    notification = rows[0]
    notification["metadata"] = parse_notification_metadata(notification.get("metadata"))
    notification = make_json_safe(notification)

    return notification


def upsert_client_coach_session_notification(
    client_id: int,
    event_id: int,
    title: str,
    body: str,
    action: str,
):
    metadata = {
        "route": CLIENT_WORKOUT_ROUTE,
        "event_id": event_id,
        "action": action,
    }

    existing_rows = run_query(
        """
        SELECT notification_id
        FROM notification
        WHERE user_id = :user_id
        AND type = 'coach_session'
        AND reference_id = :reference_id
        LIMIT 1
        """,
        {
            "user_id": client_id,
            "reference_id": event_id,
        },
        fetch=True,
        commit=False,
    )

    if existing_rows:
        notification_id = existing_rows[0]["notification_id"]

        run_query(
            """
            UPDATE notification
            SET
                mode = 'client',
                metadata = :metadata,
                title = :title,
                body = :body,
                is_read = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE notification_id = :notification_id
            AND user_id = :user_id
            """,
            {
                "notification_id": notification_id,
                "user_id": client_id,
                "metadata": json.dumps(metadata),
                "title": title,
                "body": body,
            },
            fetch=False,
            commit=True,
        )

        notification = get_notification_by_id(notification_id)

        if notification:
            socketio.emit(
                "update_notification",
                notification,
                room=f"{client_id}:client",
            )

        return notification

    notification_id = run_query(
        """
        INSERT INTO notification
        (
            user_id,
            type,
            mode,
            conversation_id,
            reference_id,
            metadata,
            title,
            body,
            is_read
        )
        VALUES
        (
            :user_id,
            'coach_session',
            'client',
            NULL,
            :reference_id,
            :metadata,
            :title,
            :body,
            FALSE
        )
        """,
        {
            "user_id": client_id,
            "reference_id": event_id,
            "metadata": json.dumps(metadata),
            "title": title,
            "body": body,
        },
        fetch=False,
        commit=True,
        return_lastrowid=True,
    )

    notification = get_notification_by_id(notification_id)

    if notification:
        socketio.emit(
            "new_notification",
            notification,
            room=f"{client_id}:client",
        )

    return notification


def clear_old_client_session_notification(client_id: int, event_id: int):
    rows = run_query(
        """
        SELECT notification_id
        FROM notification
        WHERE user_id = :user_id
        AND type = 'coach_session'
        AND reference_id = :reference_id
        LIMIT 1
        """,
        {
            "user_id": client_id,
            "reference_id": event_id,
        },
        fetch=True,
        commit=False,
    )

    if not rows:
        return True

    notification_id = rows[0]["notification_id"]

    run_query(
        """
        UPDATE notification
        SET is_read = TRUE
        WHERE notification_id = :notification_id
        AND user_id = :user_id
        """,
        {
            "notification_id": notification_id,
            "user_id": client_id,
        },
        fetch=False,
        commit=True,
    )

    socketio.emit(
        "clear_notification",
        {
            "id": notification_id,
            "notification_id": notification_id,
        },
        room=f"{client_id}:client",
    )

    return True


def get_all_coach_session_events(
    coach_id: int,
    start_date: date,
    end_date: date,
):
    rows = run_query(
        """
        SELECT
            e.event_id,
            e.user_id,
            e.event_date,
            e.start_time,
            e.end_time,
            e.event_type,
            e.description,
            e.notes,
            e.workout_plan_id,
            e.workout_day_id,

            NULL AS workout_plan_name,
            NULL AS workout_day_label,
            NULL AS workout_day_order,

            cs.coach_session_id,
            cs.contract_id,
            cs.coach_id,
            cs.client_id,
            cs.status,

            coach_user.first_name AS coach_first_name,
            coach_user.last_name AS coach_last_name,
            client_user.first_name AS client_first_name,
            client_user.last_name AS client_last_name,
            client_user.email AS client_email

        FROM coach_session cs
        JOIN event e
            ON e.event_id = cs.event_id
        JOIN users_immutables coach_user
            ON coach_user.user_id = cs.coach_id
        JOIN users_immutables client_user
            ON client_user.user_id = cs.client_id
        WHERE cs.coach_id = :coach_id
        AND e.event_type = 'coach_session'
        AND e.event_date BETWEEN :start_date AND :end_date
        ORDER BY e.event_date ASC, e.start_time ASC, e.event_id ASC
        """,
        {
            "coach_id": coach_id,
            "start_date": start_date,
            "end_date": end_date,
        },
        fetch=True,
        commit=False,
    )

    return [serialize_event(row) for row in rows]


def get_coach_session_event_by_id(coach_id: int, event_id: int):
    rows = run_query(
        """
        SELECT
            e.event_id,
            e.user_id,
            e.event_date,
            e.start_time,
            e.end_time,
            e.event_type,
            e.description,
            e.notes,
            e.workout_plan_id,
            e.workout_day_id,

            NULL AS workout_plan_name,
            NULL AS workout_day_label,
            NULL AS workout_day_order,

            cs.coach_session_id,
            cs.contract_id,
            cs.coach_id,
            cs.client_id,
            cs.status,

            coach_user.first_name AS coach_first_name,
            coach_user.last_name AS coach_last_name,
            client_user.first_name AS client_first_name,
            client_user.last_name AS client_last_name,
            client_user.email AS client_email

        FROM coach_session cs
        JOIN event e
            ON e.event_id = cs.event_id
        JOIN users_immutables coach_user
            ON coach_user.user_id = cs.coach_id
        JOIN users_immutables client_user
            ON client_user.user_id = cs.client_id
        WHERE cs.coach_id = :coach_id
        AND cs.event_id = :event_id
        AND e.event_type = 'coach_session'
        LIMIT 1
        """,
        {
            "coach_id": coach_id,
            "event_id": event_id,
        },
        fetch=True,
        commit=False,
    )

    if not rows:
        return None

    return serialize_event(rows[0])


def get_time_conflicts(
    coach_id: int,
    event_date: date,
    start_time: time,
    end_time: time,
    exclude_event_id: int | None = None,
):
    rows = run_query(
        """
        SELECT
            e.event_id,
            e.user_id,
            e.event_date,
            e.start_time,
            e.end_time,
            e.event_type,
            e.description,
            e.notes,
            e.workout_plan_id,
            e.workout_day_id,

            NULL AS workout_plan_name,
            NULL AS workout_day_label,
            NULL AS workout_day_order,

            cs.coach_session_id,
            cs.contract_id,
            cs.coach_id,
            cs.client_id,
            cs.status,

            coach_user.first_name AS coach_first_name,
            coach_user.last_name AS coach_last_name,
            client_user.first_name AS client_first_name,
            client_user.last_name AS client_last_name,
            client_user.email AS client_email

        FROM coach_session cs
        JOIN event e
            ON e.event_id = cs.event_id
        JOIN users_immutables coach_user
            ON coach_user.user_id = cs.coach_id
        JOIN users_immutables client_user
            ON client_user.user_id = cs.client_id
        WHERE cs.coach_id = :coach_id
        AND e.event_type = 'coach_session'
        AND cs.status != 'cancelled'
        AND e.event_date = :event_date
        AND (:exclude_event_id IS NULL OR e.event_id != :exclude_event_id)
        AND e.start_time < :end_time
        AND e.end_time > :start_time
        ORDER BY e.start_time ASC
        """,
        {
            "coach_id": coach_id,
            "event_date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "exclude_event_id": exclude_event_id,
        },
        fetch=True,
        commit=False,
    )

    return [serialize_event(row) for row in rows]


def create_coach_session_event(
    contract_id: int,
    coach_id: int,
    client_id: int,
    event_date: date,
    start_time: time,
    end_time: time,
    description: str,
    notes: str,
):
    event_id = run_query(
        """
        INSERT INTO event
            (
                user_id,
                event_date,
                start_time,
                end_time,
                event_type,
                description,
                notes,
                workout_plan_id,
                workout_day_id
            )
        VALUES
            (
                :user_id,
                :event_date,
                :start_time,
                :end_time,
                'coach_session',
                :description,
                :notes,
                NULL,
                NULL
            )
        """,
        {
            "user_id": client_id,
            "event_date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "description": description or "Coach Session",
            "notes": notes or "",
        },
        fetch=False,
        commit=True,
        return_lastrowid=True,
    )

    run_query(
        """
        INSERT INTO coach_session
            (
                event_id,
                contract_id,
                coach_id,
                client_id,
                status
            )
        VALUES
            (
                :event_id,
                :contract_id,
                :coach_id,
                :client_id,
                'scheduled'
            )
        """,
        {
            "event_id": event_id,
            "contract_id": contract_id,
            "coach_id": coach_id,
            "client_id": client_id,
        },
        fetch=False,
        commit=True,
    )

    upsert_client_coach_session_notification(
        client_id=client_id,
        event_id=event_id,
        title="Coach session scheduled",
        body=description or "Your coach scheduled a new session.",
        action="created",
    )

    return get_coach_session_event_by_id(
        coach_id=coach_id,
        event_id=event_id,
    )


def update_coach_session_event(
    coach_id: int,
    event_id: int,
    event_date: date | None = None,
    start_time: time | None = None,
    end_time: time | None = None,
    description: str | None = None,
    notes: str | None = None,
    contract_id: int | None = None,
    client_id: int | None = None,
):
    existing = get_coach_session_event_by_id(
        coach_id=coach_id,
        event_id=event_id,
    )

    if not existing:
        return None

    next_event_date = event_date if event_date is not None else existing["date"]
    next_start_time = start_time if start_time is not None else existing["startTime"]
    next_end_time = end_time if end_time is not None else existing["endTime"]
    next_description = (
        description if description is not None else existing["description"]
    )
    next_notes = notes if notes is not None else existing["notes"]
    next_contract_id = (
        contract_id if contract_id is not None else existing["contractId"]
    )
    next_client_id = client_id if client_id is not None else existing["clientId"]

    old_client_id = existing["clientId"]

    run_query(
        """
        UPDATE event e
        JOIN coach_session cs
            ON cs.event_id = e.event_id
        SET
            e.user_id = :client_id,
            e.event_date = :event_date,
            e.start_time = :start_time,
            e.end_time = :end_time,
            e.description = :description,
            e.notes = :notes,
            e.workout_plan_id = NULL,
            e.workout_day_id = NULL,
            cs.contract_id = :contract_id,
            cs.client_id = :client_id
        WHERE e.event_id = :event_id
        AND e.event_type = 'coach_session'
        AND cs.coach_id = :coach_id
        """,
        {
            "event_date": next_event_date,
            "start_time": next_start_time,
            "end_time": next_end_time,
            "description": next_description or "Coach Session",
            "notes": next_notes or "",
            "event_id": event_id,
            "contract_id": next_contract_id,
            "coach_id": coach_id,
            "client_id": next_client_id,
        },
        fetch=False,
        commit=True,
    )

    if old_client_id != next_client_id:
        clear_old_client_session_notification(
            client_id=old_client_id,
            event_id=event_id,
        )

    upsert_client_coach_session_notification(
        client_id=next_client_id,
        event_id=event_id,
        title="Coach session updated",
        body=next_description or "Your coach updated a session.",
        action="updated",
    )

    return get_coach_session_event_by_id(
        coach_id=coach_id,
        event_id=event_id,
    )


def delete_coach_session_event(coach_id: int, event_id: int):
    existing = get_coach_session_event_by_id(
        coach_id=coach_id,
        event_id=event_id,
    )

    if not existing:
        return False

    client_id = existing["clientId"]
    description = existing["description"] or "Coach Session"

    upsert_client_coach_session_notification(
        client_id=client_id,
        event_id=event_id,
        title="Coach session cancelled",
        body=description,
        action="cancelled",
    )

    run_query(
        """
        DELETE e
        FROM event e
        JOIN coach_session cs
            ON cs.event_id = e.event_id
        WHERE e.event_id = :event_id
        AND e.event_type = 'coach_session'
        AND cs.coach_id = :coach_id
        """,
        {
            "event_id": event_id,
            "coach_id": coach_id,
        },
        fetch=False,
        commit=True,
    )

    return True


def update_coach_session_status(
    coach_id: int,
    event_id: int,
    status: str,
):
    existing = get_coach_session_event_by_id(
        coach_id=coach_id,
        event_id=event_id,
    )

    if not existing:
        return None

    run_query(
        """
        UPDATE coach_session
        SET status = :status
        WHERE event_id = :event_id
        AND coach_id = :coach_id
        """,
        {
            "status": status,
            "event_id": event_id,
            "coach_id": coach_id,
        },
        fetch=False,
        commit=True,
    )

    upsert_client_coach_session_notification(
        client_id=existing["clientId"],
        event_id=event_id,
        title="Coach session status updated",
        body=f"Session marked as {status}.",
        action="status_updated",
    )

    return get_coach_session_event_by_id(
        coach_id=coach_id,
        event_id=event_id,
    )
