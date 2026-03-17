from app.services import run_query


def getUserCreds(email):

    result = run_query(
        """
        SELECT 
            uc.user_id,
            uc.password_hash,
            CASE
                WHEN a.admin_id IS NOT NULL THEN 'admin'
                WHEN c.coach_id IS NOT NULL THEN 'coach'
                ELSE 'client'
            END AS role
        FROM user_creds uc
        LEFT JOIN coach c 
            ON uc.user_id = c.coach_id
        LEFT JOIN admin a
            ON uc.user_id = a.admin_id
        WHERE uc.email = :email
        """,
        {"email": email},
        fetch=True,
        commit=False
    )

    return result[0] if result else None