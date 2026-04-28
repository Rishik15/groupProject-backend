from app.services import run_query


def getUserRoles(user_id: int):
    result = run_query(
        """
        SELECT
            EXISTS(
                SELECT 1
                FROM admin
                WHERE admin_id = :user_id
            ) AS is_admin,

            EXISTS(
                SELECT 1
                FROM coach
                WHERE coach_id = :user_id
            ) AS is_coach,

            EXISTS(
                SELECT 1
                FROM user_mutables
                WHERE user_id = :user_id
            ) AS is_client
        """,
        {"user_id": user_id},
    )

    if not result:
        return []

    row = result[0]

    if row["is_admin"]:
        return ["admin"]

    if row["is_coach"]:
        return ["coach", "client"]

    if row["is_client"]:
        return ["client"]

    return []
