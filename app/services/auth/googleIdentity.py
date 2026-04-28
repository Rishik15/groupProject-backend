from app.services import run_query


def getGoogleIdentityBySub(google_sub: str):
    result = run_query(
        """
        SELECT
            google_identity_id,
            user_id,
            google_sub,
            google_email,
            email_verified,
            created_at,
            updated_at
        FROM google_user_identity
        WHERE google_sub = :google_sub
        LIMIT 1
        """,
        {"google_sub": google_sub},
        fetch=True,
        commit=False,
    )

    return result[0] if result else None


def getGoogleIdentityByUserId(user_id: int):
    result = run_query(
        """
        SELECT
            google_identity_id,
            user_id,
            google_sub,
            google_email,
            email_verified,
            created_at,
            updated_at
        FROM google_user_identity
        WHERE user_id = :user_id
        LIMIT 1
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    return result[0] if result else None


def linkGoogleIdentity(
    user_id: int,
    google_sub: str,
    google_email: str,
    email_verified: bool,
):
    existing_for_user = getGoogleIdentityByUserId(user_id)
    if existing_for_user is not None:
        run_query(
            """
            UPDATE google_user_identity
            SET
                google_sub = :google_sub,
                google_email = :google_email,
                email_verified = :email_verified
            WHERE user_id = :user_id
            """,
            {
                "user_id": user_id,
                "google_sub": google_sub,
                "google_email": google_email,
                "email_verified": 1 if email_verified else 0,
            },
            fetch=False,
            commit=True,
        )
        return

    run_query(
        """
        INSERT INTO google_user_identity
        (
            user_id,
            google_sub,
            google_email,
            email_verified
        )
        VALUES
        (
            :user_id,
            :google_sub,
            :google_email,
            :email_verified
        )
        """,
        {
            "user_id": user_id,
            "google_sub": google_sub,
            "google_email": google_email,
            "email_verified": 1 if email_verified else 0,
        },
        fetch=False,
        commit=True,
    )


def _split_name(name: str | None):
    cleaned = (name or "").strip()

    if not cleaned:
        return "Google", "User"

    parts = cleaned.split(" ", 1)

    if len(parts) == 1:
        return parts[0], "User"

    return parts[0], parts[1]


def createUserFromGoogle(
    email: str,
    full_name: str | None = None,
    role: str | None = None,
):
    first_name, last_name = _split_name(full_name)

    run_query(
        """
        INSERT INTO users_immutables (first_name, last_name, email)
        VALUES (:first_name, :last_name, :email)
        """,
        {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        },
        fetch=False,
        commit=False,
    )

    result = run_query("SELECT LAST_INSERT_ID() AS user_id")
    user_id = result[0]["user_id"]

    if role == "client":
        run_query(
            """
            INSERT INTO user_mutables (user_id)
            VALUES (:user_id)
            """,
            {"user_id": user_id},
            fetch=False,
            commit=False,
        )

        run_query(
            """
            INSERT INTO points_wallet (user_id, balance)
            VALUES (:user_id, 0)
            """,
            {"user_id": user_id},
            fetch=False,
            commit=True,
        )

    elif role == "coach":
        run_query(
            """
            INSERT INTO user_mutables (user_id)
            VALUES (:user_id)
            """,
            {"user_id": user_id},
            fetch=False,
            commit=False,
        )

        run_query(
            """
            INSERT INTO points_wallet (user_id, balance)
            VALUES (:user_id, 0)
            """,
            {"user_id": user_id},
            fetch=False,
            commit=False,
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

    else:
        run_query("SELECT 1", fetch=False, commit=True)

    return user_id
