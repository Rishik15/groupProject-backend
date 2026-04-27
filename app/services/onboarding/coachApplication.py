import json
from app.services import run_query


def addCoachApplication(
    user_id: int,
    years_experience,
    coach_description: str,
    desired_price: float,
    metadata: dict,
):
    try:
        run_query(
            """
            INSERT INTO coach_application
            (
                user_id,
                status,
                years_experience,
                coach_description,
                desired_price,
                metadata
            )
            VALUES
            (
                :user_id,
                'pending',
                :years_experience,
                :coach_description,
                :desired_price,
                CAST(:metadata AS JSON)
            )
            ON DUPLICATE KEY UPDATE
                status = 'pending',
                years_experience = VALUES(years_experience),
                coach_description = VALUES(coach_description),
                desired_price = VALUES(desired_price),
                metadata = VALUES(metadata),
                reviewed_at = NULL,
                reviewed_by_admin_id = NULL,
                admin_action = NULL
            """,
            {
                "user_id": user_id,
                "years_experience": years_experience,
                "coach_description": coach_description,
                "desired_price": desired_price,
                "metadata": json.dumps(metadata),
            },
            fetch=False,
            commit=True,
        )

    except Exception as e:
        raise e
