from app.services import run_query
from datetime import datetime


def _is_admin(user_id: int) -> bool:
    """
    Verifies admin privileges using admin table (NOT session role).
    """
    rows = run_query(
        """
        SELECT admin_id
        FROM admin
        WHERE admin_id = :uid
        """,
        params={"uid": user_id},
        fetch=True,
        commit=False
    )

    return len(rows) > 0


def get_dashboard_stats(user_id: int):
    """
    Returns dashboard statistics for admin.
    Raises:
        PermissionError if not admin
    """

    if not _is_admin(user_id):
        raise PermissionError("Forbidden")

    total_users = run_query(
        "SELECT COUNT(*) AS count FROM users_immutables",
        fetch=True
    )[0]["count"]

    active_coaches = run_query(
        "SELECT COUNT(*) AS count FROM coach",
        fetch=True
    )[0]["count"]

    pending_apps = run_query(
        """
        SELECT COUNT(*) AS count
        FROM coach_application
        WHERE status = 'pending'
        """,
        fetch=True
    )[0]["count"]

    open_reports = run_query(
        """
        SELECT COUNT(*) AS count
        FROM user_report
        WHERE status IN ('open','reviewing')
        """,
        fetch=True
    )[0]["count"]

    now = datetime.utcnow()
    year = now.year
    month = now.month

    monthly_revenue = run_query(
        """
        SELECT COALESCE(SUM(agreed_price), 0) AS revenue
        FROM user_coach_contract
        WHERE active = 1
          AND (
                (YEAR(start_date) = :year AND MONTH(start_date) = :month)
                OR end_date IS NULL
              )
        """,
        params={"year": year, "month": month},
        fetch=True
    )[0]["revenue"]

    return {
        "total_users": total_users,
        "active_coaches": active_coaches,
        "pending_reviews": pending_apps + open_reports,
        "pending_coach_applications": pending_apps,
        "open_reports": open_reports,
        "monthly_revenue": float(monthly_revenue)
    }