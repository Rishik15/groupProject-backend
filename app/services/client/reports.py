from app.services import run_query


def _shape_report(row):
    return {
        "id": row["report_id"],
        "report_id": row["report_id"],
        "reported_user_id": row["reported_user_id"],
        "reported_name": row["reported_name"],
        "reported_email": row["reported_email"],
        "reason": row["reason"],
        "description": None,
        "status": row["status"],
        "admin_action": row["admin_action"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


def get_my_reports(user_id: int):
    rows = run_query(
        """
        SELECT
            ur.report_id,
            ur.reported_user_id,
            CONCAT(ui.first_name, ' ', ui.last_name) AS reported_name,
            uc.email AS reported_email,
            ur.reason,
            ur.status,
            ur.admin_action,
            ur.created_at,
            ur.updated_at
        FROM user_report ur
        LEFT JOIN users_immutables ui
            ON ui.user_id = ur.reported_user_id
        LEFT JOIN user_creds uc
            ON uc.user_id = ur.reported_user_id
        WHERE ur.reporter_user_id = :user_id
        ORDER BY ur.created_at DESC, ur.report_id DESC
        """,
        params={"user_id": user_id},
        fetch=True,
        commit=False,
    )

    return [_shape_report(row) for row in rows]
