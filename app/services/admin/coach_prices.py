from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services import run_query
from app.services.admin.dashboard import _is_admin
from app.sockets.notifications.notifications import send_notification


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _format_datetime(value, user_timezone: str | None):
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed_datetime = value
    else:
        try:
            parsed_datetime = datetime.fromisoformat(str(value).replace(" ", "T"))
        except (ValueError, TypeError):
            return str(value)

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=timezone.utc)

    local_datetime = parsed_datetime.astimezone(
        ZoneInfo(_get_valid_timezone(user_timezone))
    )

    return local_datetime.strftime("%Y-%m-%dT%H:%M:%S")


def _get_coach_price_request_row(request_id: int):
    rows = run_query(
        """
        SELECT
            cpr.request_id,
            cpr.coach_id,
            cpr.proposed_price,
            cpr.status,
            cpr.admin_action,
            cpr.reviewed_by_admin_id,
            cpr.reviewed_at,
            cpr.created_at,
            cpr.updated_at,
            ui.first_name,
            ui.last_name,
            c.price AS current_price
        FROM coach_price_change_request AS cpr
        JOIN users_immutables AS ui
            ON cpr.coach_id = ui.user_id
        JOIN coach AS c
            ON cpr.coach_id = c.coach_id
        WHERE cpr.request_id = :request_id
        """,
        params={"request_id": int(request_id)},
        fetch=True,
        commit=False,
    )

    if not rows:
        raise ValueError("Coach price request not found")

    return rows[0]


def _shape_coach_price_request(row, user_timezone: str | None = None):
    return {
        "request_id": row["request_id"],
        "coach_id": row["coach_id"],
        "coach_name": f'{row["first_name"]} {row["last_name"]}',
        "current_price": (
            float(row["current_price"]) if row["current_price"] is not None else None
        ),
        "proposed_price": (
            float(row["proposed_price"]) if row["proposed_price"] is not None else None
        ),
        "status": row["status"],
        "admin_action": row["admin_action"],
        "reviewed_by_admin_id": row["reviewed_by_admin_id"],
        "reviewed_at": _format_datetime(row["reviewed_at"], user_timezone),
        "created_at": _format_datetime(row["created_at"], user_timezone),
        "updated_at": _format_datetime(row["updated_at"], user_timezone),
    }


def get_pending_coach_price_requests(
    user_id: int,
    user_timezone: str | None = None,
):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    rows = run_query(
        """
        SELECT
            cpr.request_id,
            cpr.coach_id,
            cpr.proposed_price,
            cpr.status,
            cpr.admin_action,
            cpr.reviewed_by_admin_id,
            cpr.reviewed_at,
            cpr.created_at,
            cpr.updated_at,
            ui.first_name,
            ui.last_name,
            c.price AS current_price
        FROM coach_price_change_request AS cpr
        JOIN users_immutables AS ui
            ON cpr.coach_id = ui.user_id
        JOIN coach AS c
            ON cpr.coach_id = c.coach_id
        WHERE cpr.status = 'pending'
        ORDER BY cpr.created_at DESC, cpr.request_id DESC
        """,
        fetch=True,
        commit=False,
    )

    return [_shape_coach_price_request(row, user_timezone) for row in rows]


def approve_coach_price_request(
    admin_user_id: int,
    request_id,
    admin_action=None,
    user_timezone: str | None = None,
):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    if not request_id:
        raise ValueError("request_id is required")

    row = _get_coach_price_request_row(int(request_id))

    if row["status"] != "pending":
        raise ValueError("Only pending coach price requests can be approved")

    final_admin_action = admin_action if admin_action else "Approved by admin"

    run_query(
        """
        UPDATE coach
        SET price = :proposed_price
        WHERE coach_id = :coach_id
        """,
        params={
            "proposed_price": row["proposed_price"],
            "coach_id": row["coach_id"],
        },
        fetch=False,
        commit=False,
    )

    run_query(
        """
        UPDATE coach_price_change_request
        SET
            status = 'approved',
            admin_action = :admin_action,
            reviewed_by_admin_id = :admin_id,
            reviewed_at = UTC_TIMESTAMP()
        WHERE request_id = :request_id
        """,
        params={
            "admin_action": final_admin_action,
            "admin_id": admin_user_id,
            "request_id": int(request_id),
        },
        fetch=False,
        commit=True,
    )

    updated_row = _get_coach_price_request_row(int(request_id))
    shaped = _shape_coach_price_request(updated_row, user_timezone)

    send_notification(
        user_id=int(updated_row["coach_id"]),
        mode="coach",
        notification_type="profile_update",
        title="Price change approved",
        body=f"Your requested price of ${float(updated_row['proposed_price']):.2f} was approved.",
        route="/coach/settings",
        reference_id=int(request_id),
        metadata={
            "request_id": int(request_id),
            "status": "approved",
            "admin_action": final_admin_action,
        },
    )

    return shaped


def reject_coach_price_request(
    admin_user_id: int,
    request_id,
    admin_action=None,
    user_timezone: str | None = None,
):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    if not request_id:
        raise ValueError("request_id is required")

    row = _get_coach_price_request_row(int(request_id))

    if row["status"] != "pending":
        raise ValueError("Only pending coach price requests can be rejected")

    final_admin_action = admin_action if admin_action else "Rejected by admin"

    run_query(
        """
        UPDATE coach_price_change_request
        SET
            status = 'rejected',
            admin_action = :admin_action,
            reviewed_by_admin_id = :admin_id,
            reviewed_at = UTC_TIMESTAMP()
        WHERE request_id = :request_id
        """,
        params={
            "admin_action": final_admin_action,
            "admin_id": admin_user_id,
            "request_id": int(request_id),
        },
        fetch=False,
        commit=True,
    )

    updated_row = _get_coach_price_request_row(int(request_id))
    shaped = _shape_coach_price_request(updated_row, user_timezone)

    send_notification(
        user_id=int(updated_row["coach_id"]),
        mode="coach",
        notification_type="profile_update",
        title="Price change rejected",
        body=final_admin_action,
        route="/coach/settings",
        reference_id=int(request_id),
        metadata={
            "request_id": int(request_id),
            "status": "rejected",
            "admin_action": final_admin_action,
        },
    )

    return shaped
