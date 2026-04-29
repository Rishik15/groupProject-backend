from app.services import run_query


def get_previous_coaches(user_id: int):
    rows = run_query(
        """
        SELECT
            c.coach_id,
            CONCAT(ui.first_name, ' ', ui.last_name) AS full_name,
            uc.email,
            um.profile_picture AS image,
            CASE
                WHEN ucc.active = 1 THEN 'active'
                WHEN ucc.active = 0 AND ucc.end_date IS NOT NULL THEN 'terminated'
                ELSE 'previous'
            END AS contract_status,
            MAX(ucc.updated_at) AS last_contract_update
        FROM user_coach_contract ucc
        JOIN coach c
            ON c.coach_id = ucc.coach_id
        JOIN users_immutables ui
            ON ui.user_id = c.coach_id
        JOIN user_creds uc
            ON uc.user_id = c.coach_id
        LEFT JOIN user_mutables um
            ON um.user_id = c.coach_id
        WHERE ucc.user_id = :user_id
        AND (
            ucc.active = 1
            OR (ucc.active = 0 AND ucc.end_date IS NOT NULL)
        )
        GROUP BY
            c.coach_id,
            ui.first_name,
            ui.last_name,
            uc.email,
            um.profile_picture,
            contract_status
        ORDER BY
            CASE
                WHEN contract_status = 'active' THEN 0
                WHEN contract_status = 'terminated' THEN 1
                ELSE 2
            END,
            last_contract_update DESC
        """,
        params={"user_id": user_id},
        fetch=True,
        commit=False,
    )

    return [
        {
            "coach_id": row["coach_id"],
            "full_name": row["full_name"],
            "email": row["email"],
            "image": row["image"],
            "contract_status": row["contract_status"],
        }
        for row in rows
    ]
