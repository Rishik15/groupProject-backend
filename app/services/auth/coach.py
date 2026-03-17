from app.services import run_query


def addCoach(email, password_hash, first_name, last_name):

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

        run_query(
            """
            INSERT INTO user_mutables (user_id)
            VALUES (:user_id)
        """,
            {"user_id": user_id},
            fetch=False,
        )

        run_query(
            """
            INSERT INTO points_wallet (user_id, balance)
            VALUES (:user_id, 0)
        """,
            {"user_id": user_id},
            fetch=False,
        )

        run_query(
            """
            INSERT INTO coach (coach_id, price)
            VALUES (:user_id, 0)
        """,
            {"user_id": user_id},
            fetch=False,
            commit=True,
        )

        return user_id

    except Exception as e:
        raise e
