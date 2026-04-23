from app.services import run_query


def get_account_settings(user_id: int, role: str):
    try:
        result = run_query(
            """
            SELECT
                ui.first_name,
                ui.last_name,
                ui.email,
                ui.phone_number,
                ui.dob,
                um.profile_picture,
                um.weight,
                um.height,
                um.goal_weight,
                c.coach_description,
                c.price
            FROM users_immutables ui
            LEFT JOIN user_mutables um
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
            raise ValueError("User not found")

        row = result[0]

        settings_payload = {
            "first_name": row.get("first_name"),
            "last_name": row.get("last_name"),
            "email": row.get("email"),
            "phone_number": row.get("phone_number"),
            "dob": row.get("dob").isoformat() if row.get("dob") is not None else None,
            "profile_picture": row.get("profile_picture"),
            "weight": row.get("weight"),
            "height": row.get("height"),
            "goal_weight": row.get("goal_weight"),
            "role": role,
        }

        if role == "coach":
            settings_payload["coach_description"] = row.get("coach_description")
            settings_payload["price"] = row.get("price")

        return settings_payload

    except Exception as e:
        raise e


def update_account_settings(user_id: int, role: str, update_json: dict):
    try:
        allowed_user_immutable_fields = {
            "first_name": "first_name",
            "last_name": "last_name",
            "phone_number": "phone_number",
            "dob": "dob",
        }

        allowed_user_mutable_fields = {
            "weight": "weight",
            "height": "height",
            "goal_weight": "goal_weight",
        }

        allowed_coach_fields = {
            "coach_description": "coach_description",
            "price": "price",
        }

        immutable_updates = []
        immutable_params = {"user_id": user_id}

        for key, column in allowed_user_immutable_fields.items():
            if key in update_json:
                immutable_updates.append(f"{column} = :{key}")
                immutable_params[key] = update_json[key]

        if immutable_updates:
            run_query(
                f"""
                UPDATE users_immutables
                SET {", ".join(immutable_updates)}
                WHERE user_id = :user_id
                """,
                immutable_params,
                fetch=False,
                commit=False,
            )

        mutable_updates = []
        mutable_params = {"user_id": user_id}

        for key, column in allowed_user_mutable_fields.items():
            if key in update_json:
                mutable_updates.append(f"{column} = :{key}")
                mutable_params[key] = update_json[key]

        if mutable_updates:
            run_query(
                f"""
                UPDATE user_mutables
                SET {", ".join(mutable_updates)}
                WHERE user_id = :user_id
                """,
                mutable_params,
                fetch=False,
                commit=False,
            )

        if role == "coach":
            coach_updates = []
            coach_params = {"user_id": user_id}

            for key, column in allowed_coach_fields.items():
                if key in update_json:
                    coach_updates.append(f"{column} = :{key}")
                    coach_params[key] = update_json[key]

            if coach_updates:
                run_query(
                    f"""
                    UPDATE coach
                    SET {", ".join(coach_updates)}
                    WHERE coach_id = :user_id
                    """,
                    coach_params,
                    fetch=False,
                    commit=False,
                )

        run_query("SELECT 1", fetch=False, commit=True)

        return get_account_settings(user_id=user_id, role=role)

    except Exception as e:
        raise e


def update_profile_picture(user_id: int, role: str, photo_url: str):
    try:
        run_query(
            """
            UPDATE user_mutables
            SET profile_picture = :photo_url
            WHERE user_id = :user_id
            """,
            {
                "user_id": user_id,
                "photo_url": photo_url,
            },
            fetch=False,
            commit=True,
        )

        return get_account_settings(user_id=user_id, role=role)

    except Exception as e:
        raise e