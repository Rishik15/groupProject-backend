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
        commit=False,
    )

    return result[0] if result else None


def getUserByEmail(email):
    result = run_query(
        """
        SELECT
            ui.user_id,
            ui.first_name,
            ui.last_name,
            ui.email,
            CASE
                WHEN a.admin_id IS NOT NULL THEN 'admin'
                WHEN c.coach_id IS NOT NULL THEN 'coach'
                ELSE 'client'
            END AS role
        FROM users_immutables ui
        LEFT JOIN coach c
            ON ui.user_id = c.coach_id
        LEFT JOIN admin a
            ON ui.user_id = a.admin_id
        WHERE ui.email = :email
        LIMIT 1
        """,
        {"email": email},
        fetch=True,
        commit=False,
    )

    return result[0] if result else None


def getUserByGoogleSub(google_sub):
    result = run_query(
        """
        SELECT
            ui.user_id,
            ui.first_name,
            ui.last_name,
            ui.email,
            CASE
                WHEN a.admin_id IS NOT NULL THEN 'admin'
                WHEN c.coach_id IS NOT NULL THEN 'coach'
                ELSE 'client'
            END AS role
        FROM google_user_identity gui
        INNER JOIN users_immutables ui
            ON gui.user_id = ui.user_id
        LEFT JOIN coach c
            ON ui.user_id = c.coach_id
        LEFT JOIN admin a
            ON ui.user_id = a.admin_id
        WHERE gui.google_sub = :google_sub
        LIMIT 1
        """,
        {"google_sub": google_sub},
        fetch=True,
        commit=False,
    )

    return result[0] if result else None


def getUserInfo(user_id):
    try:
        user = run_query(
            """
            SELECT
                ui.first_name, ui.last_name, ui.email
            FROM users_immutables ui
            WHERE ui.user_id = :user_id
            """,
            {"user_id": user_id},
            fetch=True,
            commit=False,
        )
    except Exception as e:
        raise e

    return user[0] if user else None