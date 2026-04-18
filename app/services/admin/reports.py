from app.services import run_query
from app.services.admin.dashboard import _is_admin


def _validate_report_status_filter(status: str):
    if status not in ["open", "closed"]:
        raise ValueError("status must be 'open' or 'closed'")


def get_admin_reports(user_id: int, status: str):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    _validate_report_status_filter(status)

    status_values = ["open", "reviewing"] if status == "open" else ["resolved", "dismissed"]

    rows = run_query(
        """
        SELECT
            ur.report_id,
            ur.reported_user_id,
            ur.reporter_user_id,
            ur.reason,
            ur.status,
            ur.admin_action,
            ur.resolved_by_admin_id,
            ur.created_at,
            ur.updated_at,
            reported.first_name AS reported_first_name,
            reported.last_name AS reported_last_name,
            reporter.first_name AS reporter_first_name,
            reporter.last_name AS reporter_last_name
        FROM user_report AS ur
        JOIN users_immutables AS reported
            ON ur.reported_user_id = reported.user_id
        JOIN users_immutables AS reporter
            ON ur.reporter_user_id = reporter.user_id
        WHERE ur.status IN (:status_one, :status_two)
        ORDER BY ur.created_at DESC, ur.report_id DESC
        """,
        params={
            "status_one": status_values[0],
            "status_two": status_values[1]
        },
        fetch=True,
        commit=False
    )

    reports = []

    for row in rows:
        reported_name = f'{row["reported_first_name"]} {row["reported_last_name"]}'
        reporter_name = f'{row["reporter_first_name"]} {row["reporter_last_name"]}'

        reports.append({
            "id": row["report_id"],
            "report_id": row["report_id"],
            "reported_user_id": row["reported_user_id"],
            "reporter_user_id": row["reporter_user_id"],
            "title": f"Report against {reported_name}",
            "description": row["reason"],
            "reason": row["reason"],
            "submittedLabel": row["created_at"].isoformat() if row["created_at"] is not None else None,
            "statusLabel": row["status"],
            "status": row["status"],
            "admin_action": row["admin_action"],
            "resolved_by_admin_id": row["resolved_by_admin_id"],
            "reported_name": reported_name,
            "reporter_name": reporter_name,
            "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None
        })

    return reports


def close_admin_report(user_id: int, report_id: int, admin_action=None):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    existing_rows = run_query(
        """
        SELECT
            report_id,
            reported_user_id,
            reporter_user_id,
            reason,
            status,
            admin_action,
            resolved_by_admin_id,
            created_at,
            updated_at
        FROM user_report
        WHERE report_id = :report_id
        """,
        params={"report_id": report_id},
        fetch=True,
        commit=False
    )

    if not existing_rows:
        raise ValueError("Report not found")

    existing = existing_rows[0]

    if existing["status"] in ["resolved", "dismissed"]:
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
            "report_id": report_id
        },
        fetch=False,
        commit=True
    )

    updated_rows = run_query(
        """
        SELECT
            report_id,
            reported_user_id,
            reporter_user_id,
            reason,
            status,
            admin_action,
            resolved_by_admin_id,
            created_at,
            updated_at
        FROM user_report
        WHERE report_id = :report_id
        """,
        params={"report_id": report_id},
        fetch=True,
        commit=False
    )

    updated = updated_rows[0]

    return {
        "id": updated["report_id"],
        "report_id": updated["report_id"],
        "reported_user_id": updated["reported_user_id"],
        "reporter_user_id": updated["reporter_user_id"],
        "reason": updated["reason"],
        "status": updated["status"],
        "statusLabel": updated["status"],
        "description": updated["reason"],
        "admin_action": updated["admin_action"],
        "resolved_by_admin_id": updated["resolved_by_admin_id"],
        "created_at": updated["created_at"].isoformat() if updated["created_at"] is not None else None,
        "updated_at": updated["updated_at"].isoformat() if updated["updated_at"] is not None else None
    }