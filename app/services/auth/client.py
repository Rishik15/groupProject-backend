from app.services import run_query


def addClient(email, password_hash, first_name, last_name):

    try:

        run_query(
            """
            INSERT INTO users_immutables (first_name, last_name, email)
            VALUES (:first_name, :last_name, :email)
        """,
            {"first_name": first_name, "last_name": last_name, "email": email},
            fetch=False,
        )

        result = run_query("SELECT LAST_INSERT_ID() AS user_id")

        user_id = result[0]["user_id"]

        run_query(
            """
            INSERT INTO user_creds (user_id, username, password_hash, email)
            VALUES (:user_id, :username, :password_hash, :email)
        """,
            {
                "user_id": user_id,
                "username": email,
                "password_hash": password_hash,
                "email": email,
            },
            fetch=False,
        )

        initialize_client_role(user_id, commit=True)

        return user_id

    except Exception as e:
        raise e


def initialize_client_role(user_id: int, commit: bool = True):
    try:
        existing_mutables = run_query(
            """
            SELECT user_id
            FROM user_mutables
            WHERE user_id = :user_id
            LIMIT 1
            """,
            {"user_id": user_id},
            fetch=True,
            commit=False,
        )

        if not existing_mutables:
            run_query(
                """
                INSERT INTO user_mutables (user_id)
                VALUES (:user_id)
                """,
                {"user_id": user_id},
                fetch=False,
                commit=False,
            )

        existing_wallet = run_query(
            """
            SELECT user_id
            FROM points_wallet
            WHERE user_id = :user_id
            LIMIT 1
            """,
            {"user_id": user_id},
            fetch=True,
            commit=False,
        )

        if not existing_wallet:
            run_query(
                """
                INSERT INTO points_wallet (user_id, balance)
                VALUES (:user_id, 0)
                """,
                {"user_id": user_id},
                fetch=False,
                commit=False,
            )

        existing_coach = run_query(
            """
            SELECT coach_id
            FROM coach
            WHERE coach_id = :user_id
            LIMIT 1
            """,
            {"user_id": user_id},
            fetch=True,
            commit=False,
        )

        if existing_coach:
            run_query(
                """
                DELETE FROM coach
                WHERE coach_id = :user_id
                """,
                {"user_id": user_id},
                fetch=False,
                commit=False,
            )

        if commit:
            run_query("SELECT 1", fetch=False, commit=True)

        return user_id

    except Exception as e:
        raise e