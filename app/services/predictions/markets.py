from datetime import datetime
from app.services import run_query


def _get_prediction_market_row(market_id: int):
    rows = run_query(
        """
        SELECT
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email,
            COALESCE(COUNT(p.prediction_id), 0) AS total_bets,
            COALESCE(SUM(p.points_wagered), 0) AS total_points
        FROM prediction_market AS pm
        JOIN users_immutables AS ui
            ON pm.creator_user_id = ui.user_id
        LEFT JOIN prediction AS p
            ON pm.market_id = p.market_id
        WHERE pm.market_id = :market_id
        GROUP BY
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email
        """,
        params={"market_id": int(market_id)},
        fetch=True,
        commit=False
    )

    if not rows:
        raise ValueError("Prediction market not found")

    return rows[0]


def _shape_prediction_market(row):
    return {
        "market_id": row["market_id"],
        "creator_user_id": row["creator_user_id"],
        "creator_name": f'{row["first_name"]} {row["last_name"]}',
        "creator_email": row["email"],
        "title": row["title"],
        "goal_text": row["goal_text"],
        "end_date": row["end_date"].isoformat() if row["end_date"] is not None else None,
        "status": row["status"],
        "total_bets": int(row["total_bets"]),
        "total_points": int(row["total_points"]) if row["total_points"] is not None else 0,
        "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
    }


def get_open_prediction_markets(user_id: int):
    user_rows = run_query(
        """
        SELECT user_id
        FROM users_immutables
        WHERE user_id = :user_id
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False
    )

    if not user_rows:
        raise ValueError("User not found")

    rows = run_query(
        """
        SELECT
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email,
            COALESCE(COUNT(p.prediction_id), 0) AS total_bets,
            COALESCE(SUM(p.points_wagered), 0) AS total_points
        FROM prediction_market AS pm
        JOIN users_immutables AS ui
            ON pm.creator_user_id = ui.user_id
        LEFT JOIN prediction AS p
            ON pm.market_id = p.market_id
        WHERE pm.status = 'open'
        GROUP BY
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email
        ORDER BY pm.end_date ASC, pm.market_id DESC
        """,
        fetch=True,
        commit=False
    )

    return [_shape_prediction_market(row) for row in rows]


def create_prediction_market(creator_user_id: int, title: str, goal_text: str, end_date: str):
    if not title or not title.strip():
        raise ValueError("title is required")

    if not goal_text or not goal_text.strip():
        raise ValueError("goal_text is required")

    if not end_date:
        raise ValueError("end_date is required")

    try:
        parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("end_date must be in YYYY-MM-DD format")

    if parsed_end_date <= datetime.utcnow().date():
        raise ValueError("end_date must be in the future")

    user_rows = run_query(
        """
        SELECT user_id
        FROM users_immutables
        WHERE user_id = :user_id
        """,
        params={"user_id": int(creator_user_id)},
        fetch=True,
        commit=False
    )

    if not user_rows:
        raise ValueError("User not found")

    run_query(
        """
        INSERT INTO prediction_market (
            creator_user_id,
            title,
            goal_text,
            end_date,
            status
        )
        VALUES (
            :creator_user_id,
            :title,
            :goal_text,
            :end_date,
            'open'
        )
        """,
        params={
            "creator_user_id": int(creator_user_id),
            "title": title.strip(),
            "goal_text": goal_text.strip(),
            "end_date": parsed_end_date
        },
        fetch=False,
        commit=True
    )

    created_rows = run_query(
        """
        SELECT market_id
        FROM prediction_market
        WHERE creator_user_id = :creator_user_id
          AND title = :title
          AND goal_text = :goal_text
          AND end_date = :end_date
        ORDER BY market_id DESC
        LIMIT 1
        """,
        params={
            "creator_user_id": int(creator_user_id),
            "title": title.strip(),
            "goal_text": goal_text.strip(),
            "end_date": parsed_end_date
        },
        fetch=True,
        commit=False
    )

    return _shape_prediction_market(_get_prediction_market_row(created_rows[0]["market_id"]))