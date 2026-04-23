from app.services import run_query
from app.services.admin.dashboard import _is_admin


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
        commit=False
    )

    if not rows:
        raise ValueError("Report not found")

    return rows[0]


def _shape_report(row):
    return {
        "id": row["report_id"],
        "report_id": row["report_id"],
        "reported_user_id": row["reported_user_id"],
        "reporter_user_id": row["reporter_user_id"],
        "title": f"Report against user {row['reported_user_id']}",
        "description": row["reason"],
        "status": row["status"],
        "submittedLabel": row["created_at"].isoformat() if row["created_at"] is not None else None,
        "admin_action": row["admin_action"]
    }


def get_admin_reports(user_id: int, status: str):
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
            commit=False
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
            commit=False
        )

    return [_shape_report(row) for row in rows]


def close_admin_report(user_id: int, report_id: int, admin_action=None):
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
            "report_id": int(report_id)
        },
        fetch=False,
        commit=True
    )

    updated_row = _get_report_row(int(report_id))
    return _shape_report(updated_row)