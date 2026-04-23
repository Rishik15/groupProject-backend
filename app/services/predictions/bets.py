from app.services import run_query


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


def _get_open_market_row(market_id: int):
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


def _get_prediction_row(market_id: int, predictor_user_id: int):
    rows = run_query(
        """
        SELECT
            prediction_id,
            market_id,
            predictor_user_id,
            prediction_value,
            points_wagered,
            created_at,
            updated_at
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
        "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
    }


def place_prediction_bet(predictor_user_id: int, market_id, prediction_value, points_wagered):
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

    market_row = _get_open_market_row(int(market_id))

    if market_row["status"] != "open":
        raise ValueError("Only open markets can accept bets")

    wallet_row = _get_wallet_row(int(predictor_user_id))

    if int(wallet_row["balance"]) < final_points_wagered:
        raise ValueError("Insufficient wallet balance")

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

    wallet_update_result = run_query(
        """
        UPDATE points_wallet
        SET balance = balance - :points_wagered
        WHERE user_id = :user_id
          AND balance >= :points_wagered
        """,
        params={
            "points_wagered": final_points_wagered,
            "user_id": int(predictor_user_id)
        },
        fetch=False,
        commit=False
    )

    run_query(
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
        """,
        params={
            "market_id": int(market_id),
            "predictor_user_id": int(predictor_user_id),
            "prediction_value": normalized_prediction_value,
            "points_wagered": final_points_wagered
        },
        fetch=False,
        commit=False
    )

    created_rows = run_query(
        """
        SELECT prediction_id
        FROM prediction
        WHERE market_id = :market_id
          AND predictor_user_id = :predictor_user_id
        ORDER BY prediction_id DESC
        LIMIT 1
        """,
        params={
            "market_id": int(market_id),
            "predictor_user_id": int(predictor_user_id)
        },
        fetch=True,
        commit=False
    )

    prediction_id = created_rows[0]["prediction_id"]

    run_query(
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
        """,
        params={
            "user_id": int(predictor_user_id),
            "delta_points": -final_points_wagered,
            "reason": "Prediction market wager",
            "ref_type": "prediction",
            "ref_id": int(prediction_id)
        },
        fetch=False,
        commit=True
    )

    return _shape_prediction(_get_prediction_row(int(market_id), int(predictor_user_id)))