from app.services import run_query
from app.services.admin.dashboard import _is_admin


def _validate_application_status_filter(status: str):
    if status not in ["pending", "approved", "rejected"]:
        raise ValueError("status must be 'pending', 'approved', or 'rejected'")


def _get_application_row(application_id: int):
    rows = run_query(
        """
        SELECT
            ca.application_id,
            ca.user_id,
            ca.status,
            ca.years_experience,
            ca.coach_description,
            ca.desired_price,
            ca.submitted_at,
            ca.reviewed_at,
            ca.reviewed_by_admin_id,
            ca.admin_action,
            ui.first_name,
            ui.last_name,
            ui.email
        FROM coach_application AS ca
        JOIN users_immutables AS ui
            ON ca.user_id = ui.user_id
        WHERE ca.application_id = :application_id
        """,
        params={"application_id": int(application_id)},
        fetch=True,
        commit=False
    )

    if not rows:
        raise ValueError("Coach application not found")

    return rows[0]


def _get_application_cert_rows(application_id: int):
    return run_query(
        """
        SELECT
            application_id,
            cert_name,
            provider_name,
            description,
            issued_date,
            expires_date
        FROM coach_application_certification
        WHERE application_id = :application_id
        ORDER BY application_certification_id ASC
        """,
        params={"application_id": int(application_id)},
        fetch=True,
        commit=False
    )


def _shape_application(application_row, cert_rows):
    name = f'{application_row["first_name"]} {application_row["last_name"]}'

    cert_names = []
    certifications = []

    for cert in cert_rows:
        cert_names.append(cert["cert_name"])
        certifications.append({
            "cert_name": cert["cert_name"],
            "provider_name": cert["provider_name"],
            "description": cert["description"],
            "issued_date": cert["issued_date"].isoformat() if cert["issued_date"] is not None else None,
            "expires_date": cert["expires_date"].isoformat() if cert["expires_date"] is not None else None
        })

    return {
        "id": application_row["application_id"],
        "application_id": application_row["application_id"],
        "user_id": application_row["user_id"],
        "name": name,
        "email": application_row["email"],
        "appliedLabel": application_row["submitted_at"].isoformat() if application_row["submitted_at"] is not None else None,
        "avatarInitial": application_row["first_name"][0] if application_row["first_name"] else None,
        "status": application_row["status"],
        "years_experience": application_row["years_experience"],
        "coach_description": application_row["coach_description"],
        "desired_price": float(application_row["desired_price"]) if application_row["desired_price"] is not None else None,
        "reviewed_at": application_row["reviewed_at"].isoformat() if application_row["reviewed_at"] is not None else None,
        "reviewed_by_admin_id": application_row["reviewed_by_admin_id"],
        "admin_action": application_row["admin_action"],
        "certifications": cert_names,
        "certification_details": certifications
    }


def get_admin_coach_applications(user_id: int, status: str):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    _validate_application_status_filter(status)

    rows = run_query(
        """
        SELECT
            ca.application_id,
            ca.user_id,
            ca.status,
            ca.years_experience,
            ca.coach_description,
            ca.desired_price,
            ca.submitted_at,
            ca.reviewed_at,
            ca.reviewed_by_admin_id,
            ca.admin_action,
            ui.first_name,
            ui.last_name,
            ui.email
        FROM coach_application AS ca
        JOIN users_immutables AS ui
            ON ca.user_id = ui.user_id
        WHERE ca.status = :status
        ORDER BY ca.submitted_at DESC, ca.application_id DESC
        """,
        params={"status": status},
        fetch=True,
        commit=False
    )

    cert_rows = run_query(
        """
        SELECT
            application_id,
            cert_name,
            provider_name,
            description,
            issued_date,
            expires_date
        FROM coach_application_certification
        ORDER BY application_id ASC, application_certification_id ASC
        """,
        fetch=True,
        commit=False
    )

    certs_by_application = {}

    for cert in cert_rows:
        application_id = cert["application_id"]

        if application_id not in certs_by_application:
            certs_by_application[application_id] = []

        certs_by_application[application_id].append(cert)

    applications = []

    for row in rows:
        applications.append(
            _shape_application(
                row,
                certs_by_application.get(row["application_id"], [])
            )
        )

    return applications


def approve_coach_application(user_id: int, application_id: int, admin_action=None):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not application_id:
        raise ValueError("application_id is required")

    application_row = _get_application_row(int(application_id))

    if application_row["status"] != "pending":
        raise ValueError("Only pending applications can be approved")

    existing_coach_rows = run_query(
        """
        SELECT coach_id
        FROM coach
        WHERE coach_id = :coach_id
        """,
        params={"coach_id": application_row["user_id"]},
        fetch=True,
        commit=False
    )

    if existing_coach_rows:
        raise ValueError("Coach row already exists for this user")

    cert_rows = _get_application_cert_rows(int(application_id))

    final_admin_action = admin_action if admin_action else "Approved by admin"

    run_query(
        """
        INSERT INTO coach (coach_id, coach_description, price)
        VALUES (:coach_id, :coach_description, :price)
        """,
        params={
            "coach_id": application_row["user_id"],
            "coach_description": application_row["coach_description"],
            "price": application_row["desired_price"]
        },
        fetch=False,
        commit=False
    )

    for cert in cert_rows:
        run_query(
            """
            INSERT INTO certifications (
                coach_id,
                cert_name,
                provider_name,
                description,
                issued_date,
                expires_date
            )
            VALUES (
                :coach_id,
                :cert_name,
                :provider_name,
                :description,
                :issued_date,
                :expires_date
            )
            """,
            params={
                "coach_id": application_row["user_id"],
                "cert_name": cert["cert_name"],
                "provider_name": cert["provider_name"],
                "description": cert["description"],
                "issued_date": cert["issued_date"],
                "expires_date": cert["expires_date"]
            },
            fetch=False,
            commit=False
        )

    run_query(
        """
        UPDATE coach_application
        SET
            status = 'approved',
            reviewed_at = NOW(),
            reviewed_by_admin_id = :admin_id,
            admin_action = :admin_action
        WHERE application_id = :application_id
        """,
        params={
            "admin_id": user_id,
            "admin_action": final_admin_action,
            "application_id": int(application_id)
        },
        fetch=False,
        commit=True
    )

    updated_application = _get_application_row(int(application_id))
    updated_certs = _get_application_cert_rows(int(application_id))

    return _shape_application(updated_application, updated_certs)


def reject_coach_application(user_id: int, application_id: int, admin_action=None):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not application_id:
        raise ValueError("application_id is required")

    application_row = _get_application_row(int(application_id))

    if application_row["status"] != "pending":
        raise ValueError("Only pending applications can be rejected")

    final_admin_action = admin_action if admin_action else "Rejected by admin"

    run_query(
        """
        UPDATE coach_application
        SET
            status = 'rejected',
            reviewed_at = NOW(),
            reviewed_by_admin_id = :admin_id,
            admin_action = :admin_action
        WHERE application_id = :application_id
        """,
        params={
            "admin_id": user_id,
            "admin_action": final_admin_action,
            "application_id": int(application_id)
        },
        fetch=False,
        commit=True
    )

    updated_application = _get_application_row(int(application_id))
    updated_certs = _get_application_cert_rows(int(application_id))

    return _shape_application(updated_application, updated_certs)