from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .. import run_query


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _format_datetime(value, user_timezone: str | None):
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed_datetime = value
    else:
        try:
            parsed_datetime = datetime.fromisoformat(str(value).replace(" ", "T"))
        except (ValueError, TypeError):
            return str(value)

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=timezone.utc)

    local_datetime = parsed_datetime.astimezone(
        ZoneInfo(_get_valid_timezone(user_timezone))
    )

    return local_datetime.strftime("%Y-%m-%dT%H:%M:%S")


def _serialize_review_rows(rows, user_timezone: str | None = None):
    serialized = []

    for row in rows:
        serialized.append(
            {
                "review_id": row["review_id"],
                "rating": row["rating"],
                "review_text": row["review_text"],
                "reviewer_first_name": row["reviewer_first_name"],
                "reviewer_last_name": row["reviewer_last_name"],
                "created_at": _format_datetime(row.get("created_at"), user_timezone),
                "updated_at": _format_datetime(row.get("updated_at"), user_timezone),
            }
        )

    return serialized


def getReviews(coach_id: int, user_timezone: str | None = None):
    coach_info = run_query(
        """
        SELECT
            c.coach_id,
            ui.first_name AS coach_first_name,
            ui.last_name AS coach_last_name
        FROM coach c
        INNER JOIN users_immutables ui
            ON c.coach_id = ui.user_id
        WHERE c.coach_id = :coach_id
        """,
        {"coach_id": int(coach_id)},
        fetch=True,
        commit=False,
    )

    if not coach_info:
        raise ValueError("Coach not found")

    summary = run_query(
        """
        SELECT
            ROUND(AVG(cr.rating), 2) AS coach_avg_rating
        FROM coach_review cr
        WHERE cr.coach_id = :coach_id
        """,
        {"coach_id": int(coach_id)},
        fetch=True,
        commit=False,
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
        WHERE cr.coach_id = :coach_id
        ORDER BY cr.created_at DESC
        """,
        {"coach_id": int(coach_id)},
        fetch=True,
        commit=False,
    )

    avg_rating = None

    if summary and summary[0]["coach_avg_rating"] is not None:
        avg_rating = float(summary[0]["coach_avg_rating"])

    return {
        "coach_avg_rating": avg_rating,
        "reviews": _serialize_review_rows(reviews, user_timezone),
        "coach_first_name": coach_info[0]["coach_first_name"],
        "coach_last_name": coach_info[0]["coach_last_name"],
    }


def clientKnowsCoach(user_id: int, coach_id: int):
    result = run_query(
        """
        SELECT contract_id
        FROM user_coach_contract
        WHERE user_id = :user_id
          AND coach_id = :coach_id
          AND (
            active = 1
            OR end_date IS NOT NULL
          )
        LIMIT 1
        """,
        {
            "user_id": int(user_id),
            "coach_id": int(coach_id),
        },
        fetch=True,
        commit=False,
    )

    return len(result) > 0


def hasExistingReview(user_id: int, coach_id: int):
    result = run_query(
        """
        SELECT review_id
        FROM coach_review
        WHERE coach_id = :coach_id
          AND reviewer_user_id = :user_id
        LIMIT 1
        """,
        {
            "user_id": int(user_id),
            "coach_id": int(coach_id),
        },
        fetch=True,
        commit=False,
    )

    return len(result) > 0


def postReview(user_id: int, coach_id: int, rating: int, review_text: str):
    run_query(
        """
        INSERT INTO coach_review
            (coach_id, reviewer_user_id, rating, review_text)
        VALUES
            (:coach_id, :user_id, :rating, :review_text)
        """,
        {
            "user_id": int(user_id),
            "coach_id": int(coach_id),
            "rating": int(rating),
            "review_text": review_text,
        },
        fetch=False,
        commit=True,
    )
