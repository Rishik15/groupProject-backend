from app.services import run_query


def getUserInfo(user_id):
    result = run_query(
        """
        SELECT
            ui.user_id,
            ui.first_name,
            ui.last_name,
            ui.email,
            ui.phone_number,
            ui.dob,
            um.profile_picture,
            um.weight,
            um.height,
            um.goal_weight,

            CASE
                WHEN a.admin_id IS NOT NULL THEN 'admin'
                WHEN c.coach_id IS NOT NULL THEN 'coach'
                ELSE 'client'
            END AS role

        FROM users_immutables ui

        LEFT JOIN user_mutables um
            ON ui.user_id = um.user_id

        LEFT JOIN coach c 
            ON ui.user_id = c.coach_id

        LEFT JOIN admin a
            ON ui.user_id = a.admin_id

        WHERE ui.user_id = :user_id
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    print("QUERY RESULT:", result)

    return result[0] if result else None
