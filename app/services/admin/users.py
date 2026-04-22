from app.services import run_query
from app.services.admin.dashboard import _is_admin


def _get_admin_user_row(target_user_id: int):
    rows = run_query(
        """
        SELECT
            ui.user_id,
            ui.first_name,
            ui.last_name,
            CONCAT(ui.first_name, ' ', ui.last_name) AS name,
            uc.email,
            ui.phone_number,
            ui.account_status,
            ui.suspension_reason,
            ui.updated_at,
            CASE WHEN c.coach_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_coach,
            CASE WHEN a.admin_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_admin
        FROM users_immutables ui
        LEFT JOIN user_creds uc
            ON ui.user_id = uc.user_id
        LEFT JOIN coach c
            ON ui.user_id = c.coach_id
        LEFT JOIN admin a
            ON ui.user_id = a.admin_id
        WHERE ui.user_id = :target_user_id
        """,
        params={"target_user_id": int(target_user_id)},
        fetch=True,
        commit=False
    )

    if not rows:
        raise ValueError("User not found")

    row = rows[0]

    return {
        "user_id": row["user_id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "name": row["name"],
        "email": row["email"],
        "phone_number": row["phone_number"],
        "is_coach": bool(row["is_coach"]),
        "is_admin": bool(row["is_admin"]),
        "account_status": row["account_status"],
        "suspension_reason": row["suspension_reason"],
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
    }


def get_admin_users(user_id: int):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    rows = run_query(
        """
        SELECT
            ui.user_id,
            ui.first_name,
            ui.last_name,
            CONCAT(ui.first_name, ' ', ui.last_name) AS name,
            uc.email,
            ui.phone_number,
            ui.account_status,
            ui.suspension_reason,
            ui.updated_at,
            CASE WHEN c.coach_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_coach,
            CASE WHEN a.admin_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_admin
        FROM users_immutables ui
        LEFT JOIN user_creds uc
            ON ui.user_id = uc.user_id
        LEFT JOIN coach c
            ON ui.user_id = c.coach_id
        LEFT JOIN admin a
            ON ui.user_id = a.admin_id
        ORDER BY ui.user_id ASC
        """,
        fetch=True,
        commit=False
    )

    users = []

    for row in rows:
        users.append({
            "user_id": row["user_id"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "name": row["name"],
            "email": row["email"],
            "phone_number": row["phone_number"],
            "is_coach": bool(row["is_coach"]),
            "is_admin": bool(row["is_admin"]),
            "account_status": row["account_status"],
            "suspension_reason": row["suspension_reason"],
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
        })

    return users


def suspend_admin_user(admin_user_id: int, target_user_id, suspension_reason):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    if not target_user_id:
        raise ValueError("user_id is required")

    if not suspension_reason:
        raise ValueError("suspension_reason is required")

    _get_admin_user_row(int(target_user_id))

    run_query(
        """
        UPDATE users_immutables
        SET
            account_status = 'suspended',
            suspension_reason = :suspension_reason
        WHERE user_id = :target_user_id
        """,
        params={
            "suspension_reason": suspension_reason,
            "target_user_id": int(target_user_id)
        },
        fetch=False,
        commit=True
    )

    return _get_admin_user_row(int(target_user_id))


def deactivate_admin_user(admin_user_id: int, target_user_id, suspension_reason):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    if not target_user_id:
        raise ValueError("user_id is required")

    if not suspension_reason:
        raise ValueError("suspension_reason is required")

    _get_admin_user_row(int(target_user_id))

    run_query(
        """
        UPDATE users_immutables
        SET
            account_status = 'deactivated',
            suspension_reason = :suspension_reason
        WHERE user_id = :target_user_id
        """,
        params={
            "suspension_reason": suspension_reason,
            "target_user_id": int(target_user_id)
        },
        fetch=False,
        commit=True
    )

    return _get_admin_user_row(int(target_user_id))


def update_admin_user_status(admin_user_id: int, target_user_id, account_status, suspension_reason=None):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    if not target_user_id:
        raise ValueError("user_id is required")

    if not account_status:
        raise ValueError("account_status is required")

    if account_status not in ("active", "suspended", "deactivated"):
        raise ValueError("account_status must be one of: active, suspended, deactivated")

    _get_admin_user_row(int(target_user_id))

    final_reason = suspension_reason
    if account_status == "active":
        final_reason = None
    elif account_status in ("suspended", "deactivated") and not final_reason:
        raise ValueError("suspension_reason is required when setting suspended or deactivated status")

    run_query(
        """
        UPDATE users_immutables
        SET
            account_status = :account_status,
            suspension_reason = :suspension_reason
        WHERE user_id = :target_user_id
        """,
        params={
            "account_status": account_status,
            "suspension_reason": final_reason,
            "target_user_id": int(target_user_id)
        },
        fetch=False,
        commit=True
    )

    return _get_admin_user_row(int(target_user_id))


def get_active_coaches(user_id: int):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    coach_rows = run_query(
        """
        SELECT
            ui.user_id,
            ui.first_name,
            ui.last_name,
            CONCAT(ui.first_name, ' ', ui.last_name) AS name,
            uc.email,
            c.coach_description,
            c.price,
            COUNT(DISTINCT ucc.contract_id) AS contract_count
        FROM users_immutables ui
        JOIN user_creds uc
            ON ui.user_id = uc.user_id
        JOIN coach c
            ON ui.user_id = c.coach_id
        LEFT JOIN user_coach_contract ucc
            ON c.coach_id = ucc.coach_id AND ucc.active = 1
        GROUP BY
            ui.user_id,
            ui.first_name,
            ui.last_name,
            uc.email,
            c.coach_description,
            c.price
        ORDER BY ui.user_id ASC
        """,
        fetch=True,
        commit=False
    )

    cert_rows = run_query(
        """
        SELECT
            coach_id,
            cert_name,
            provider_name,
            description,
            issued_date,
            expires_date
        FROM certifications
        ORDER BY coach_id ASC, cert_id ASC
        """,
        fetch=True,
        commit=False
    )

    cert_map = {}

    for cert in cert_rows:
        cert_map.setdefault(cert["coach_id"], []).append({
            "cert_name": cert["cert_name"],
            "provider_name": cert["provider_name"],
            "description": cert["description"],
            "issued_date": cert["issued_date"].isoformat() if cert["issued_date"] else None,
            "expires_date": cert["expires_date"].isoformat() if cert["expires_date"] else None,
        })

    coaches = []

    for row in coach_rows:
        coaches.append({
            "user_id": row["user_id"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "name": row["name"],
            "email": row["email"],
            "coach_description": row["coach_description"],
            "price": float(row["price"]) if row["price"] is not None else None,
            "contract_count": int(row["contract_count"]),
            "certifications": cert_map.get(row["user_id"], [])
        })

    return coaches