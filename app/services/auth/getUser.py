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
                ui.first_name,
                ui.last_name,
                ui.email,
                um.profile_picture
            FROM users_immutables ui
            LEFT JOIN user_mutables um
                ON ui.user_id = um.user_id
            WHERE ui.user_id = :user_id
            """,
            {"user_id": user_id},
            fetch=True,
            commit=False,
        )
    except Exception as e:
        raise e

    return user[0] if user else None


def getUserOnboardingStatus(user_id: int, role: str):
    try:
        if role == "coach":
            result = run_query(
                """
                SELECT
                    ui.dob,
                    um.weight,
                    um.height,
                    um.goal_weight,
                    c.coach_description,
                    c.price
                FROM users_immutables ui
                INNER JOIN user_mutables um
                    ON ui.user_id = um.user_id
                LEFT JOIN coach c
                    ON ui.user_id = c.coach_id
                WHERE ui.user_id = :user_id
                LIMIT 1
                """,
                {"user_id": user_id},
                fetch=True,
                commit=False,
            )

            if not result:
                return True

            row = result[0]

            missing_description = (
                row.get("coach_description") is None
                or str(row.get("coach_description")).strip() == ""
            )

            needs_onboarding = any([
                row.get("dob") is None,
                row.get("weight") is None,
                row.get("height") is None,
                row.get("goal_weight") is None,
                missing_description,
                row.get("price") is None,
            ])

            return needs_onboarding

        if role == "client":
            result = run_query(
                """
                SELECT
                    ui.dob,
                    um.weight,
                    um.height,
                    um.goal_weight
                FROM users_immutables ui
                INNER JOIN user_mutables um
                    ON ui.user_id = um.user_id
                WHERE ui.user_id = :user_id
                LIMIT 1
                """,
                {"user_id": user_id},
                fetch=True,
                commit=False,
            )

            if not result:
                return True

            row = result[0]

            needs_onboarding = any([
                row.get("dob") is None,
                row.get("weight") is None,
                row.get("height") is None,
                row.get("goal_weight") is None,
            ])

            return needs_onboarding

        return False

    except Exception as e:
        raise e