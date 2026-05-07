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


def _validate_report_status_filter(status: str):
    if status not in ["open", "closed"]:
        raise ValueError("status must be 'open' or 'closed'")


def _get_report_row(report_id: int):
    rows = run_query(
        """
        SELECT
            report_id,
            reported_user_id,
            reporter_user_id,
            reason,
            status,
            created_at,
            admin_action
        FROM user_report
        WHERE report_id = :report_id
        """,
        params={"report_id": int(report_id)},
        fetch=True,
        commit=False,
    )

    if not rows:
        raise ValueError("Report not found")

    return rows[0]


def _shape_report(row, user_timezone: str | None = None):
    return {
        "id": row["report_id"],
        "report_id": row["report_id"],
        "reported_user_id": row["reported_user_id"],
        "reporter_user_id": row["reporter_user_id"],
        "title": f"Report against user {row['reported_user_id']}",
        "description": row["reason"],
        "status": row["status"],
        "submittedLabel": _format_datetime(row["created_at"], user_timezone),
        "admin_action": row["admin_action"],
    }


def get_admin_reports(
    user_id: int,
    status: str,
    user_timezone: str | None = None,
):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    _validate_report_status_filter(status)

    if status == "open":
        rows = run_query(
            """
            SELECT
                report_id,
                reported_user_id,
                reporter_user_id,
                reason,
                status,
                created_at,
                admin_action
            FROM user_report
            WHERE status IN ('open', 'reviewing')
            ORDER BY created_at DESC, report_id DESC
            """,
            fetch=True,
            commit=False,
        )
    else:
        rows = run_query(
            """
            SELECT
                report_id,
                reported_user_id,
                reporter_user_id,
                reason,
                status,
                created_at,
                admin_action
            FROM user_report
            WHERE status = 'resolved'
            ORDER BY created_at DESC, report_id DESC
            """,
            fetch=True,
            commit=False,
        )

    return [_shape_report(row, user_timezone) for row in rows]


def close_admin_report(
    user_id: int,
    report_id: int,
    admin_action=None,
    user_timezone: str | None = None,
):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not report_id:
        raise ValueError("report_id is required")

    row = _get_report_row(int(report_id))

    if row["status"] == "resolved":
        raise ValueError("Report is already closed")

    final_admin_action = admin_action if admin_action else "Closed by admin"

    run_query(
        """
        UPDATE user_report
        SET
            status = 'resolved',
            admin_action = :admin_action,
            resolved_by_admin_id = :admin_id
        WHERE report_id = :report_id
        """,
        params={
            "admin_action": final_admin_action,
            "admin_id": user_id,
            "report_id": int(report_id),
        },
        fetch=False,
        commit=True,
    )

    updated_row = _get_report_row(int(report_id))
    shaped_report = _shape_report(updated_row, user_timezone)

    send_notification(
        user_id=int(updated_row["reporter_user_id"]),
        mode="client",
        notification_type="report",
        title="Your report was reviewed",
        body=final_admin_action,
        route="/client/settings",
        reference_id=int(report_id),
        metadata={
            "report_id": int(report_id),
            "reported_user_id": int(updated_row["reported_user_id"]),
            "admin_action": final_admin_action,
        },
    )

    return shaped_report
