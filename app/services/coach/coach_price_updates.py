from app.services import run_query


def _shape_price_update(row):
    return {
        "request_id": row["request_id"],
        "coach_id": row["coach_id"],
        "current_price": (
            float(row["current_price"]) if row["current_price"] is not None else None
        ),
        "proposed_price": (
            float(row["proposed_price"]) if row["proposed_price"] is not None else None
        ),
        "status": row["status"],
        "admin_action": row["admin_action"],
        "reviewed_by_admin_id": row["reviewed_by_admin_id"],
        "reviewed_at": row["reviewed_at"].isoformat() if row["reviewed_at"] else None,
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


def get_my_price_updates(coach_id: int):
    rows = run_query(
        """
        SELECT
            cpr.request_id,
            cpr.coach_id,
            c.price AS current_price,
            cpr.proposed_price,
            cpr.status,
            cpr.admin_action,
            cpr.reviewed_by_admin_id,
            cpr.reviewed_at,
            cpr.created_at,
            cpr.updated_at
        FROM coach_price_change_request cpr
        JOIN coach c
            ON c.coach_id = cpr.coach_id
        WHERE cpr.coach_id = :coach_id
        ORDER BY cpr.created_at DESC, cpr.request_id DESC
        """,
        params={"coach_id": coach_id},
        fetch=True,
        commit=False,
    )

    return [_shape_price_update(row) for row in rows]
