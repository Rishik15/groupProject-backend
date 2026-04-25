from app.services import run_query
from app.services.admin.dashboard import _is_admin
import json
from datetime import datetime
from app.services.onboarding import onboardUser
from app.sockets.notifications.notifications import send_notification
from app.services.auth.getUserRoles import getUserRoles


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
            ca.metadata,
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
        commit=False,
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
        commit=False,
    )


def _shape_application(application_row, cert_rows):
    name = f'{application_row["first_name"]} {application_row["last_name"]}'

    cert_names = []
    certifications = []

    for cert in cert_rows:
        cert_names.append(cert["cert_name"])
        certifications.append(
            {
                "cert_name": cert["cert_name"],
                "provider_name": cert["provider_name"],
                "description": cert["description"],
                "issued_date": (
                    cert["issued_date"].isoformat()
                    if cert["issued_date"] is not None
                    else None
                ),
                "expires_date": (
                    cert["expires_date"].isoformat()
                    if cert["expires_date"] is not None
                    else None
                ),
            }
        )

    return {
        "id": application_row["application_id"],
        "application_id": application_row["application_id"],
        "user_id": application_row["user_id"],
        "name": name,
        "email": application_row["email"],
        "appliedLabel": (
            application_row["submitted_at"].isoformat()
            if application_row["submitted_at"] is not None
            else None
        ),
        "avatarInitial": (
            application_row["first_name"][0] if application_row["first_name"] else None
        ),
        "status": application_row["status"],
        "years_experience": application_row["years_experience"],
        "coach_description": application_row["coach_description"],
        "desired_price": (
            float(application_row["desired_price"])
            if application_row["desired_price"] is not None
            else None
        ),
        "reviewed_at": (
            application_row["reviewed_at"].isoformat()
            if application_row["reviewed_at"] is not None
            else None
        ),
        "reviewed_by_admin_id": application_row["reviewed_by_admin_id"],
        "admin_action": application_row["admin_action"],
        "certifications": cert_names,
        "certification_details": certifications,
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
            ca.metadata,
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
        commit=False,
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
        commit=False,
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
            _shape_application(row, certs_by_application.get(row["application_id"], []))
        )

    return applications


def _parse_metadata(metadata):
    if not metadata:
        return {}

    if isinstance(metadata, dict):
        return metadata

    if isinstance(metadata, str):
        return json.loads(metadata)

    return {}


def approve_coach_application(user_id: int, application_id: int, admin_action=None):
    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    if not application_id:
        raise ValueError("application_id is required")

    application_row = _get_application_row(int(application_id))

    if application_row["status"] != "pending":
        raise ValueError("Only pending applications can be approved")

    coach_id = application_row["user_id"]

    existing_coach_rows = run_query(
        """
        SELECT coach_id
        FROM coach
        WHERE coach_id = :coach_id
        """,
        params={"coach_id": coach_id},
        fetch=True,
        commit=False,
    )

    if existing_coach_rows:
        raise ValueError("Coach row already exists for this user")

    metadata = _parse_metadata(application_row.get("metadata"))

    final_admin_action = admin_action if admin_action else "Approved by admin"

    run_query(
        """
        INSERT INTO coach (coach_id, coach_description, price)
        VALUES (:coach_id, '', 0)
        """,
        params={"coach_id": coach_id},
        fetch=False,
        commit=True,
    )

    onboardUser.onboardCoachSurvey(
        coach_id, application_row["coach_description"], application_row["desired_price"]
    )

    n_c = int(metadata.get("num_cert") or 0)

    cert_names = metadata.get("cert_name", [])
    provider_names = metadata.get("provider_name", [])
    descriptions = metadata.get("description", [])
    issued_dates = metadata.get("issued_date", [])
    expires_dates = metadata.get("expires_date", [])

    for i in range(n_c):
        onboardUser.insertCoachCert(
            coach_id,
            cert_names[i],
            provider_names[i],
            descriptions[i],
            datetime.fromisoformat(issued_dates[i]) if issued_dates[i] else None,
            datetime.fromisoformat(expires_dates[i]) if expires_dates[i] else None,
        )

    n_d = int(metadata.get("num_days") or 0)

    days_of_week = metadata.get("day_of_week", [])
    start_times = metadata.get("start_time", [])
    end_times = metadata.get("end_time", [])
    recurring_list = metadata.get("recurring", [])
    active_list = metadata.get("active", [])

    for i in range(n_d):
        onboardUser.coachAvailability(
            coach_id,
            days_of_week[i],
            start_times[i],
            end_times[i],
            recurring_list[i],
            active_list[i],
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
            "application_id": int(application_id),
        },
        fetch=False,
        commit=True,
    )

    roles = getUserRoles(coach_id)

    send_notification(
        user_id=coach_id,
        mode="client",
        notification_type="coach_application",
        title="Coach application approved",
        body="Your coach application was approved. You can now switch to coach mode.",
        route="/client/profile",
        metadata={
            "status": "approved",
            "roles": roles,
        },
        reference_id=application_id,
        extra_event="coach_application_status_changed",
        extra_payload={
            "status": "approved",
            "roles": roles,
        },
    )

    updated_application = _get_application_row(int(application_id))
    return _shape_application(updated_application, [])


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
            "application_id": int(application_id),
        },
        fetch=False,
        commit=True,
    )

    applicant_id = application_row["user_id"]

    send_notification(
        user_id=applicant_id,
        mode="client",
        notification_type="coach_application",
        title="Coach application rejected",
        body="Your coach application was rejected. You can apply again from your profile.",
        route="/client/profile",
        metadata={
            "status": "rejected",
            "roles": ["client"],
        },
        reference_id=application_id,
        extra_event="coach_application_status_changed",
        extra_payload={
            "status": "rejected",
            "roles": ["client"],
        },
    )

    updated_application = _get_application_row(int(application_id))
    return _shape_application(updated_application, [])
