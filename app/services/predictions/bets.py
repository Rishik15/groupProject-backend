from sqlalchemy import text
from app import db
from app.services import run_query


def _get_user_row(user_id: int):
    rows = run_query(
        """
        SELECT
            user_id,
            first_name,
            last_name,
            account_status
        FROM users_immutables
        WHERE user_id = :user_id
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False
    )

    if not rows:
        raise ValueError("User not found")

    return rows[0]


def _get_wallet_row(user_id: int):
    rows = run_query(
        """
        SELECT
            user_id,
            balance,
            created_at,
            updated_at
        FROM points_wallet
        WHERE user_id = :user_id
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False
    )

    if rows:
        return rows[0]

    user = _get_user_row(int(user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    run_query(
        """
        INSERT INTO points_wallet (user_id, balance)
        VALUES (:user_id, 0)
        """,
        params={"user_id": int(user_id)},
        fetch=False,
        commit=True
    )

    created_rows = run_query(
        """
        SELECT
            user_id,
            balance,
            created_at,
            updated_at
        FROM points_wallet
        WHERE user_id = :user_id
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False
    )

    return created_rows[0]


def _get_market_row(market_id: int):
    rows = run_query(
        """
        SELECT
            market_id,
            creator_user_id,
            title,
            goal_text,
            end_date,
            status,
            created_at,
            updated_at
        FROM prediction_market
        WHERE market_id = :market_id
        """,
        params={"market_id": int(market_id)},
        fetch=True,
        commit=False
    )

    if not rows:
        raise ValueError("Prediction market not found")

    return rows[0]


def _get_prediction_row_by_id(prediction_id: int):
    rows = run_query(
        """
        SELECT
            p.prediction_id,
            p.market_id,
            p.predictor_user_id,
            p.prediction_value,
            p.points_wagered,
            p.created_at,
            p.updated_at,
            pm.title AS market_title,
            pm.goal_text,
            pm.end_date,
            pm.status AS market_status
        FROM prediction AS p
        JOIN prediction_market AS pm
            ON p.market_id = pm.market_id
        WHERE p.prediction_id = :prediction_id
        """,
        params={"prediction_id": int(prediction_id)},
        fetch=True,
        commit=False
    )

    if not rows:
        raise ValueError("Prediction not found")

    return rows[0]


def _shape_prediction(row):
    return {
        "prediction_id": row["prediction_id"],
        "market_id": row["market_id"],
        "predictor_user_id": row["predictor_user_id"],
        "prediction_value": row["prediction_value"],
        "points_wagered": int(row["points_wagered"]),
        "market_title": row.get("market_title"),
        "goal_text": row.get("goal_text"),
        "end_date": row["end_date"].isoformat() if row.get("end_date") is not None else None,
        "market_status": row.get("market_status"),
        "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
    }


def get_my_prediction_bets(user_id: int):
    user = _get_user_row(int(user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    rows = run_query(
        """
        SELECT
            p.prediction_id,
            p.market_id,
            p.predictor_user_id,
            p.prediction_value,
            p.points_wagered,
            p.created_at,
            p.updated_at,
            pm.title AS market_title,
            pm.goal_text,
            pm.end_date,
            pm.status AS market_status
        FROM prediction AS p
        JOIN prediction_market AS pm
            ON p.market_id = pm.market_id
        WHERE p.predictor_user_id = :user_id
        ORDER BY p.created_at DESC, p.prediction_id DESC
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False
    )

    return [_shape_prediction(row) for row in rows]


def place_prediction_bet(predictor_user_id: int, market_id, prediction_value, points_wagered):
    user = _get_user_row(int(predictor_user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    if not market_id:
        raise ValueError("market_id is required")

    if not prediction_value:
        raise ValueError("prediction_value is required")

    normalized_prediction_value = str(prediction_value).strip().lower()

    if normalized_prediction_value not in ("yes", "no"):
        raise ValueError("prediction_value must be 'yes' or 'no'")

    if points_wagered is None:
        raise ValueError("points_wagered is required")

    try:
        final_points_wagered = int(points_wagered)
    except (TypeError, ValueError):
        raise ValueError("points_wagered must be an integer")

    if final_points_wagered <= 0:
        raise ValueError("points_wagered must be greater than 0")

    market = _get_market_row(int(market_id))

    if market["status"] != "open":
        raise ValueError("Only open markets can accept bets")

    existing_prediction_rows = run_query(
        """
        SELECT prediction_id
        FROM prediction
        WHERE market_id = :market_id
          AND predictor_user_id = :predictor_user_id
        """,
        params={
            "market_id": int(market_id),
            "predictor_user_id": int(predictor_user_id)
        },
        fetch=True,
        commit=False
    )

    if existing_prediction_rows:
        raise ValueError("User has already placed a bet on this market")

    wallet = _get_wallet_row(int(predictor_user_id))

    if int(wallet["balance"]) < final_points_wagered:
        raise ValueError("Insufficient wallet balance")

    try:
        deduct_result = db.session.execute(
            text(
                """
                UPDATE points_wallet
                SET balance = balance - :points_wagered
                WHERE user_id = :user_id
                  AND balance >= :points_wagered
                """
            ),
            {
                "points_wagered": final_points_wagered,
                "user_id": int(predictor_user_id)
            }
        )

        if deduct_result.rowcount != 1:
            db.session.rollback()
            raise ValueError("Insufficient wallet balance")

        db.session.execute(
            text(
                """
                INSERT INTO prediction (
                    market_id,
                    predictor_user_id,
                    prediction_value,
                    points_wagered
                )
                VALUES (
                    :market_id,
                    :predictor_user_id,
                    :prediction_value,
                    :points_wagered
                )
                """
            ),
            {
                "market_id": int(market_id),
                "predictor_user_id": int(predictor_user_id),
                "prediction_value": normalized_prediction_value,
                "points_wagered": final_points_wagered
            }
        )

        prediction_id_row = db.session.execute(
            text(
                """
                SELECT prediction_id
                FROM prediction
                WHERE market_id = :market_id
                  AND predictor_user_id = :predictor_user_id
                ORDER BY prediction_id DESC
                LIMIT 1
                """
            ),
            {
                "market_id": int(market_id),
                "predictor_user_id": int(predictor_user_id)
            }
        ).mappings().first()

        if not prediction_id_row:
            db.session.rollback()
            raise ValueError("Prediction bet creation failed")

        prediction_id = prediction_id_row["prediction_id"]

        db.session.execute(
            text(
                """
                INSERT INTO points_txn (
                    user_id,
                    delta_points,
                    reason,
                    ref_type,
                    ref_id
                )
                VALUES (
                    :user_id,
                    :delta_points,
                    :reason,
                    :ref_type,
                    :ref_id
                )
                """
            ),
            {
                "user_id": int(predictor_user_id),
                "delta_points": -final_points_wagered,
                "reason": "Prediction market wager",
                "ref_type": "prediction",
                "ref_id": int(prediction_id)
            }
        )

        db.session.commit()

    except ValueError:
        raise

    except Exception:
        db.session.rollback()
        raise

    return _shape_prediction(_get_prediction_row_by_id(int(prediction_id)))