from .. import run_query


def _serialize_review_rows(rows):
    serialized = []

    for row in rows:
        serialized.append(
            {
                "review_id": row["review_id"],
                "rating": row["rating"],
                "review_text": row["review_text"],
                "reviewer_first_name": row["reviewer_first_name"],
                "reviewer_last_name": row["reviewer_last_name"],
                "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
                "updated_at": row["updated_at"].isoformat() if row.get("updated_at") else None,
            }
        )

    return serialized


def getReviews(coach_id: int):
    try:
        coach_info = run_query(
            """
                SELECT
                    c.coach_id,
                    ui.first_name AS coach_first_name,
                    ui.last_name AS coach_last_name
                FROM coach c
                INNER JOIN users_immutables ui
                    ON c.coach_id = ui.user_id
                WHERE c.coach_id = :c_id
                ;
            """,
            {"c_id": coach_id},
            fetch=True,
            commit=False
        )

        if not coach_info:
            raise ValueError("Coach not found")

        summary = run_query(
            """
                SELECT
                    ROUND(AVG(cr.rating), 2) AS coach_avg_rating
                FROM coach_review cr
                WHERE cr.coach_id = :c_id
                ;
            """,
            {"c_id": coach_id},
            fetch=True,
            commit=False
        )

        reviews = run_query(
            """
                SELECT
                    cr.review_id,
                    cr.rating,
                    cr.review_text,
                    reviewer.first_name AS reviewer_first_name,
                    reviewer.last_name AS reviewer_last_name,
                    cr.created_at,
                    cr.updated_at
                FROM coach_review cr
                INNER JOIN users_immutables reviewer
                    ON cr.reviewer_user_id = reviewer.user_id
                WHERE cr.coach_id = :c_id
                ORDER BY cr.created_at DESC
                ;
            """,
            {"c_id": coach_id},
            fetch=True,
            commit=False
        )

        avg_rating = None
        if summary and summary[0]["coach_avg_rating"] is not None:
            avg_rating = float(summary[0]["coach_avg_rating"])

        return {
            "coach_avg_rating": avg_rating,
            "reviews": _serialize_review_rows(reviews),
            "coach_first_name": coach_info[0]["coach_first_name"],
            "coach_last_name": coach_info[0]["coach_last_name"]
        }

    except Exception:
        raise


def clientKnowsCoach(user_id: int, coach_id: int):
    try:
        ret = run_query(
            """
                SELECT
                    contract_id
                FROM user_coach_contract
                WHERE coach_id = :c_id
                  AND user_id = :u_id
                ;
            """,
            {"u_id": user_id, "c_id": coach_id},
            fetch=True,
            commit=False
        )

        return len(ret) > 0

    except Exception:
        raise


def hasExistingReview(user_id: int, coach_id: int):
    try:
        ret = run_query(
            """
                SELECT
                    review_id
                FROM coach_review
                WHERE coach_id = :c_id
                  AND reviewer_user_id = :u_id
                ;
            """,
            {"u_id": user_id, "c_id": coach_id},
            fetch=True,
            commit=False
        )

        return len(ret) > 0

    except Exception:
        raise


def postReview(user_id: int, coach_id: int, rating: int, review_text: str):
    try:
        run_query(
            """
                INSERT INTO coach_review
                (
                    coach_id,
                    reviewer_user_id,
                    rating,
                    review_text
                )
                VALUES
                (
                    :c_id,
                    :u_id,
                    :rate,
                    :review
                )
                ;
            """,
            {
                "u_id": user_id,
                "c_id": coach_id,
                "rate": rating,
                "review": review_text
            },
            fetch=False,
            commit=True
        )

    except Exception:
        raise