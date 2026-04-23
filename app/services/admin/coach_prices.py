from app.services import run_query
from app.services.admin.dashboard import _is_admin


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
        commit=False
    )

    if not rows:
        raise ValueError("Coach price request not found")

    return rows[0]


def _shape_coach_price_request(row):
    return {
        "request_id": row["request_id"],
        "coach_id": row["coach_id"],
        "coach_name": f'{row["first_name"]} {row["last_name"]}',
        "current_price": float(row["current_price"]) if row["current_price"] is not None else None,
        "proposed_price": float(row["proposed_price"]) if row["proposed_price"] is not None else None,
        "status": row["status"],
        "admin_action": row["admin_action"],
        "reviewed_by_admin_id": row["reviewed_by_admin_id"],
        "reviewed_at": row["reviewed_at"].isoformat() if row["reviewed_at"] is not None else None,
        "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
    }


def get_pending_coach_price_requests(user_id: int):
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
        commit=False
    )

    return [_shape_coach_price_request(row) for row in rows]


def approve_coach_price_request(admin_user_id: int, request_id, admin_action=None):
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
        SET
            price = :proposed_price
        WHERE coach_id = :coach_id
        """,
        params={
            "proposed_price": row["proposed_price"],
            "coach_id": row["coach_id"]
        },
        fetch=False,
        commit=False
    )

    run_query(
        """
        UPDATE coach_price_change_request
        SET
            status = 'approved',
            admin_action = :admin_action,
            reviewed_by_admin_id = :admin_id,
            reviewed_at = NOW()
        WHERE request_id = :request_id
        """,
        params={
            "admin_action": final_admin_action,
            "admin_id": admin_user_id,
            "request_id": int(request_id)
        },
        fetch=False,
        commit=True
    )

    updated_row = _get_coach_price_request_row(int(request_id))
    return _shape_coach_price_request(updated_row)


def reject_coach_price_request(admin_user_id: int, request_id, admin_action=None):
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
            reviewed_at = NOW()
        WHERE request_id = :request_id
        """,
        params={
            "admin_action": final_admin_action,
            "admin_id": admin_user_id,
            "request_id": int(request_id)
        },
        fetch=False,
        commit=True
    )

    updated_row = _get_coach_price_request_row(int(request_id))
    return _shape_coach_price_request(updated_row)