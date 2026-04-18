from app.services import run_query
from app.services.admin.dashboard import _is_admin


def get_admin_users(user_id: int):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    rows = run_query(
        """
        SELECT
            ui.user_id,
            ui.first_name,
            ui.last_name,
            ui.email,
            ui.phone_number,
            ui.dob,
            ui.created_at,
            ui.updated_at,
            um.profile_picture,
            um.weight,
            um.height,
            um.goal_weight,
            uc.username,
            CASE WHEN c.coach_id IS NOT NULL THEN 1 ELSE 0 END AS is_coach,
            CASE WHEN a.admin_id IS NOT NULL THEN 1 ELSE 0 END AS is_admin
        FROM users_immutables AS ui
        LEFT JOIN user_mutables AS um
            ON ui.user_id = um.user_id
        LEFT JOIN user_creds AS uc
            ON ui.user_id = uc.user_id
        LEFT JOIN coach AS c
            ON ui.user_id = c.coach_id
        LEFT JOIN admin AS a
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
            "name": f'{row["first_name"]} {row["last_name"]}',
            "email": row["email"],
            "phone_number": row["phone_number"],
            "dob": row["dob"].isoformat() if row["dob"] is not None else None,
            "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
            "profile_picture": row["profile_picture"],
            "weight": row["weight"],
            "height": row["height"],
            "goal_weight": row["goal_weight"],
            "username": row["username"],
            "is_coach": bool(row["is_coach"]),
            "is_admin": bool(row["is_admin"])
        })

    return users


def get_active_coaches(user_id: int):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    coach_rows = run_query(
        """
        SELECT
            ui.user_id,
            ui.first_name,
            ui.last_name,
            ui.email,
            ui.phone_number,
            ui.created_at,
            ui.updated_at,
            um.profile_picture,
            um.weight,
            um.height,
            um.goal_weight,
            c.coach_description,
            c.price,
            COALESCE(contract_counts.contract_count, 0) AS contract_count
        FROM coach AS c
        JOIN users_immutables AS ui
            ON c.coach_id = ui.user_id
        LEFT JOIN user_mutables AS um
            ON ui.user_id = um.user_id
        LEFT JOIN (
            SELECT
                coach_id,
                COUNT(*) AS contract_count
            FROM user_coach_contract
            WHERE active = 1
            GROUP BY coach_id
        ) AS contract_counts
            ON c.coach_id = contract_counts.coach_id
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

    certs_by_coach = {}

    for row in cert_rows:
        coach_id = row["coach_id"]

        if coach_id not in certs_by_coach:
            certs_by_coach[coach_id] = []

        certs_by_coach[coach_id].append({
            "cert_name": row["cert_name"],
            "provider_name": row["provider_name"],
            "description": row["description"],
            "issued_date": row["issued_date"].isoformat() if row["issued_date"] is not None else None,
            "expires_date": row["expires_date"].isoformat() if row["expires_date"] is not None else None
        })

    coaches = []

    for row in coach_rows:
        coaches.append({
            "user_id": row["user_id"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "name": f'{row["first_name"]} {row["last_name"]}',
            "email": row["email"],
            "phone_number": row["phone_number"],
            "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
            "profile_picture": row["profile_picture"],
            "weight": row["weight"],
            "height": row["height"],
            "goal_weight": row["goal_weight"],
            "coach_description": row["coach_description"],
            "price": float(row["price"]) if row["price"] is not None else None,
            "contract_count": int(row["contract_count"]),
            "certifications": certs_by_coach.get(row["user_id"], [])
        })

    return coaches