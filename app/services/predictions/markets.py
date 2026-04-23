from datetime import datetime
from sqlalchemy import text
from app import db
from app.services import run_query
from app.services.admin.dashboard import _is_admin


def _get_user_row(user_id: int):
    rows = run_query(
        """
        SELECT
            user_id,
            first_name,
            last_name,
            email,
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
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN 1 ELSE 0 END), 0) AS yes_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN 1 ELSE 0 END), 0) AS no_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN p.points_wagered ELSE 0 END), 0) AS yes_points,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN p.points_wagered ELSE 0 END), 0) AS no_points,
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
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
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


def _get_or_create_wallet_row(user_id: int):
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

    if not created_rows:
        raise ValueError("Wallet creation failed")

    return created_rows[0]


def _shape_prediction_market(row):
    shaped = {
        "market_id": row["market_id"],
        "creator_user_id": row["creator_user_id"],
        "creator_name": f'{row["first_name"]} {row["last_name"]}',
        "creator_email": row["email"],
        "title": row["title"],
        "goal_text": row["goal_text"],
        "end_date": row["end_date"].isoformat() if row["end_date"] is not None else None,
        "status": row["status"],
        "review_status": row["review_status"],
        "reviewed_by_admin_id": row["reviewed_by_admin_id"],
        "reviewed_at": row["reviewed_at"].isoformat() if row["reviewed_at"] is not None else None,
        "review_note": row["review_note"],
        "settlement_result": row["settlement_result"],
        "settled_by_admin_id": row["settled_by_admin_id"],
        "settled_at": row["settled_at"].isoformat() if row["settled_at"] is not None else None,
        "settlement_note": row["settlement_note"],
        "cancel_request_status": row["cancel_request_status"],
        "cancel_request_reason": row["cancel_request_reason"],
        "cancel_requested_at": row["cancel_requested_at"].isoformat() if row["cancel_requested_at"] is not None else None,
        "cancel_reviewed_by_admin_id": row["cancel_reviewed_by_admin_id"],
        "cancel_reviewed_at": row["cancel_reviewed_at"].isoformat() if row["cancel_reviewed_at"] is not None else None,
        "cancel_review_note": row["cancel_review_note"],
        "total_bets": int(row["total_bets"]),
        "total_points": int(row["total_points"]) if row["total_points"] is not None else 0,
        "yes_bets": int(row["yes_bets"]),
        "no_bets": int(row["no_bets"]),
        "yes_points": int(row["yes_points"]) if row["yes_points"] is not None else 0,
        "no_points": int(row["no_points"]) if row["no_points"] is not None else 0,
        "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
    }

    if row["status"] == "cancelled":
        shaped["result"] = "cancelled"
    elif row["settlement_result"] is not None:
        shaped["result"] = row["settlement_result"]
    else:
        shaped["result"] = None

    return shaped


def get_open_prediction_markets(user_id: int):
    user = _get_user_row(int(user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    rows = run_query(
        """
        SELECT
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN 1 ELSE 0 END), 0) AS yes_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN 1 ELSE 0 END), 0) AS no_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN p.points_wagered ELSE 0 END), 0) AS yes_points,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN p.points_wagered ELSE 0 END), 0) AS no_points,
            COALESCE(COUNT(p.prediction_id), 0) AS total_bets,
            COALESCE(SUM(p.points_wagered), 0) AS total_points
        FROM prediction_market AS pm
        JOIN users_immutables AS ui
            ON pm.creator_user_id = ui.user_id
        LEFT JOIN prediction AS p
            ON pm.market_id = p.market_id
        WHERE pm.status = 'open'
          AND pm.review_status = 'approved'
        GROUP BY
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
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
    user = _get_user_row(int(creator_user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    final_title = title.strip() if title else ""
    final_goal_text = goal_text.strip() if goal_text else ""

    if not final_title:
        raise ValueError("title is required")

    if not final_goal_text:
        raise ValueError("goal_text is required")

    if not end_date:
        raise ValueError("end_date is required")

    try:
        parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("end_date must be in YYYY-MM-DD format")

    if parsed_end_date <= datetime.utcnow().date():
        raise ValueError("end_date must be in the future")

    run_query(
        """
        INSERT INTO prediction_market (
            creator_user_id,
            title,
            goal_text,
            end_date,
            status,
            review_status,
            reviewed_by_admin_id,
            reviewed_at,
            review_note,
            settlement_result,
            settled_by_admin_id,
            settled_at,
            settlement_note,
            cancel_request_status,
            cancel_request_reason,
            cancel_requested_at,
            cancel_reviewed_by_admin_id,
            cancel_reviewed_at,
            cancel_review_note
        )
        VALUES (
            :creator_user_id,
            :title,
            :goal_text,
            :end_date,
            'open',
            'pending',
            NULL,
            NULL,
            NULL,
            NULL,
            NULL,
            NULL,
            NULL,
            'none',
            NULL,
            NULL,
            NULL,
            NULL,
            NULL
        )
        """,
        params={
            "creator_user_id": int(creator_user_id),
            "title": final_title,
            "goal_text": final_goal_text,
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
            "title": final_title,
            "goal_text": final_goal_text,
            "end_date": parsed_end_date
        },
        fetch=True,
        commit=False
    )

    if not created_rows:
        raise ValueError("Prediction market creation failed")

    return _shape_prediction_market(_get_prediction_market_row(created_rows[0]["market_id"]))


def get_my_prediction_markets(user_id: int):
    user = _get_user_row(int(user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    rows = run_query(
        """
        SELECT
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN 1 ELSE 0 END), 0) AS yes_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN 1 ELSE 0 END), 0) AS no_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN p.points_wagered ELSE 0 END), 0) AS yes_points,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN p.points_wagered ELSE 0 END), 0) AS no_points,
            COALESCE(COUNT(p.prediction_id), 0) AS total_bets,
            COALESCE(SUM(p.points_wagered), 0) AS total_points
        FROM prediction_market AS pm
        JOIN users_immutables AS ui
            ON pm.creator_user_id = ui.user_id
        LEFT JOIN prediction AS p
            ON pm.market_id = p.market_id
        WHERE pm.creator_user_id = :user_id
        GROUP BY
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email
        ORDER BY pm.created_at DESC, pm.market_id DESC
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False
    )

    return [_shape_prediction_market(row) for row in rows]


def get_prediction_summary(user_id: int):
    user = _get_user_row(int(user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    wallet = _get_or_create_wallet_row(int(user_id))

    total_bets_placed = run_query(
        """
        SELECT COUNT(*) AS count
        FROM prediction
        WHERE predictor_user_id = :user_id
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False
    )[0]["count"]

    total_markets_created = run_query(
        """
        SELECT COUNT(*) AS count
        FROM prediction_market
        WHERE creator_user_id = :user_id
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False
    )[0]["count"]

    open_markets_created = run_query(
        """
        SELECT COUNT(*) AS count
        FROM prediction_market
        WHERE creator_user_id = :user_id
          AND status = 'open'
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False
    )[0]["count"]

    completed_markets_participated = run_query(
        """
        SELECT COUNT(DISTINCT pm.market_id) AS count
        FROM prediction AS p
        JOIN prediction_market AS pm
            ON p.market_id = pm.market_id
        WHERE p.predictor_user_id = :user_id
          AND pm.status IN ('settled', 'cancelled')
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False
    )[0]["count"]

    return {
        "wallet_balance": int(wallet["balance"]),
        "total_bets_placed": int(total_bets_placed),
        "total_markets_created": int(total_markets_created),
        "open_markets_created": int(open_markets_created),
        "completed_markets_participated": int(completed_markets_participated),
    }


def get_completed_prediction_markets(user_id: int):
    user = _get_user_row(int(user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    rows = run_query(
        """
        SELECT
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN 1 ELSE 0 END), 0) AS yes_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN 1 ELSE 0 END), 0) AS no_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN p.points_wagered ELSE 0 END), 0) AS yes_points,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN p.points_wagered ELSE 0 END), 0) AS no_points,
            COALESCE(COUNT(p.prediction_id), 0) AS total_bets,
            COALESCE(SUM(p.points_wagered), 0) AS total_points
        FROM prediction_market AS pm
        JOIN users_immutables AS ui
            ON pm.creator_user_id = ui.user_id
        LEFT JOIN prediction AS p
            ON pm.market_id = p.market_id
        WHERE pm.status IN ('settled', 'cancelled')
        GROUP BY
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email
        ORDER BY pm.updated_at DESC, pm.market_id DESC
        """,
        fetch=True,
        commit=False
    )

    return [_shape_prediction_market(row) for row in rows]


def get_prediction_leaderboard(user_id: int):
    user = _get_user_row(int(user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    rows = run_query(
        """
        SELECT
            ui.user_id,
            CONCAT(ui.first_name, ' ', ui.last_name) AS name,
            COALESCE(pw.balance, 0) AS balance
        FROM users_immutables AS ui
        LEFT JOIN points_wallet AS pw
            ON ui.user_id = pw.user_id
        WHERE ui.account_status = 'active'
        ORDER BY COALESCE(pw.balance, 0) DESC, ui.user_id ASC
        """,
        fetch=True,
        commit=False
    )

    leaderboard = []

    rank = 1
    for row in rows:
        leaderboard.append({
            "rank": rank,
            "user_id": row["user_id"],
            "name": row["name"],
            "balance": int(row["balance"])
        })
        rank += 1

    return leaderboard


def get_admin_prediction_review_queue(admin_user_id: int):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    rows = run_query(
        """
        SELECT
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN 1 ELSE 0 END), 0) AS yes_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN 1 ELSE 0 END), 0) AS no_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN p.points_wagered ELSE 0 END), 0) AS yes_points,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN p.points_wagered ELSE 0 END), 0) AS no_points,
            COALESCE(COUNT(p.prediction_id), 0) AS total_bets,
            COALESCE(SUM(p.points_wagered), 0) AS total_points
        FROM prediction_market AS pm
        JOIN users_immutables AS ui
            ON pm.creator_user_id = ui.user_id
        LEFT JOIN prediction AS p
            ON pm.market_id = p.market_id
        WHERE pm.review_status = 'pending'
        GROUP BY
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email
        ORDER BY pm.created_at ASC, pm.market_id ASC
        """,
        fetch=True,
        commit=False
    )

    return [_shape_prediction_market(row) for row in rows]


def approve_prediction_market(admin_user_id: int, market_id, admin_action=None):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    if not market_id:
        raise ValueError("market_id is required")

    market = _get_prediction_market_row(int(market_id))

    if market["review_status"] != "pending":
        raise ValueError("Only pending prediction markets can be approved")

    final_admin_action = admin_action.strip() if isinstance(admin_action, str) and admin_action.strip() else "Approved by admin"

    run_query(
        """
        UPDATE prediction_market
        SET
            review_status = 'approved',
            reviewed_by_admin_id = :admin_user_id,
            reviewed_at = NOW(),
            review_note = :review_note
        WHERE market_id = :market_id
          AND review_status = 'pending'
        """,
        params={
            "admin_user_id": int(admin_user_id),
            "review_note": final_admin_action,
            "market_id": int(market_id)
        },
        fetch=False,
        commit=True
    )

    return _shape_prediction_market(_get_prediction_market_row(int(market_id)))


def reject_prediction_market(admin_user_id: int, market_id, admin_action=None):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    if not market_id:
        raise ValueError("market_id is required")

    market = _get_prediction_market_row(int(market_id))

    if market["review_status"] != "pending":
        raise ValueError("Only pending prediction markets can be rejected")

    final_admin_action = admin_action.strip() if isinstance(admin_action, str) and admin_action.strip() else "Rejected by admin"

    run_query(
        """
        UPDATE prediction_market
        SET
            review_status = 'rejected',
            status = 'cancelled',
            reviewed_by_admin_id = :admin_user_id,
            reviewed_at = NOW(),
            review_note = :review_note
        WHERE market_id = :market_id
          AND review_status = 'pending'
        """,
        params={
            "admin_user_id": int(admin_user_id),
            "review_note": final_admin_action,
            "market_id": int(market_id)
        },
        fetch=False,
        commit=True
    )

    return _shape_prediction_market(_get_prediction_market_row(int(market_id)))


def get_admin_pending_settlement_queue(admin_user_id: int):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    rows = run_query(
        """
        SELECT
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN 1 ELSE 0 END), 0) AS yes_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN 1 ELSE 0 END), 0) AS no_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN p.points_wagered ELSE 0 END), 0) AS yes_points,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN p.points_wagered ELSE 0 END), 0) AS no_points,
            COALESCE(COUNT(p.prediction_id), 0) AS total_bets,
            COALESCE(SUM(p.points_wagered), 0) AS total_points
        FROM prediction_market AS pm
        JOIN users_immutables AS ui
            ON pm.creator_user_id = ui.user_id
        LEFT JOIN prediction AS p
            ON pm.market_id = p.market_id
        WHERE pm.review_status = 'approved'
          AND pm.status = 'closed'
          AND pm.settlement_result IS NULL
        GROUP BY
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email
        ORDER BY pm.end_date ASC, pm.market_id ASC
        """,
        fetch=True,
        commit=False
    )

    return [_shape_prediction_market(row) for row in rows]


def settle_prediction_market(admin_user_id: int, market_id, result, admin_action=None):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    if not market_id:
        raise ValueError("market_id is required")

    normalized_result = str(result).strip().lower()
    if normalized_result not in ("yes", "no", "cancelled"):
        raise ValueError("result must be 'yes', 'no', or 'cancelled'")

    market = _get_prediction_market_row(int(market_id))

    if market["review_status"] != "approved":
        raise ValueError("Only approved prediction markets can be settled")

    if market["status"] != "closed":
        raise ValueError("Only closed prediction markets can be settled")

    if market["settlement_result"] is not None:
        raise ValueError("Prediction market already settled")

    final_admin_action = admin_action.strip() if isinstance(admin_action, str) and admin_action.strip() else "Settled by admin"

    predictions = run_query(
        """
        SELECT
            prediction_id,
            predictor_user_id,
            prediction_value,
            points_wagered
        FROM prediction
        WHERE market_id = :market_id
        ORDER BY prediction_id ASC
        """,
        params={"market_id": int(market_id)},
        fetch=True,
        commit=False
    )

    total_pool = sum(int(row["points_wagered"]) for row in predictions)

    try:
        if normalized_result == "cancelled":
            for row in predictions:
                user_id = int(row["predictor_user_id"])
                refund_points = int(row["points_wagered"])

                db.session.execute(
                    text(
                        """
                        INSERT INTO points_wallet (user_id, balance)
                        VALUES (:user_id, :balance)
                        ON DUPLICATE KEY UPDATE balance = balance + :balance
                        """
                    ),
                    {
                        "user_id": user_id,
                        "balance": refund_points
                    }
                )

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
                            'Prediction market refund',
                            'prediction_market',
                            :ref_id
                        )
                        """
                    ),
                    {
                        "user_id": user_id,
                        "delta_points": refund_points,
                        "ref_id": int(market_id)
                    }
                )

            db.session.execute(
                text(
                    """
                    UPDATE prediction_market
                    SET
                        status = 'cancelled',
                        settlement_result = 'cancelled',
                        settled_by_admin_id = :admin_user_id,
                        settled_at = NOW(),
                        settlement_note = :settlement_note
                    WHERE market_id = :market_id
                      AND status = 'closed'
                      AND settlement_result IS NULL
                    """
                ),
                {
                    "admin_user_id": int(admin_user_id),
                    "settlement_note": final_admin_action,
                    "market_id": int(market_id)
                }
            )

        else:
            winners = [
                row for row in predictions
                if str(row["prediction_value"]).strip().lower() == normalized_result
            ]

            if len(winners) == 0:
                db.session.execute(
                    text(
                        """
                        UPDATE prediction_market
                        SET
                            status = 'cancelled',
                            settlement_result = 'cancelled',
                            settled_by_admin_id = :admin_user_id,
                            settled_at = NOW(),
                            settlement_note = :settlement_note
                        WHERE market_id = :market_id
                          AND status = 'closed'
                          AND settlement_result IS NULL
                        """
                    ),
                    {
                        "admin_user_id": int(admin_user_id),
                        "settlement_note": "No winners found; market cancelled during settlement.",
                        "market_id": int(market_id)
                    }
                )

                for row in predictions:
                    user_id = int(row["predictor_user_id"])
                    refund_points = int(row["points_wagered"])

                    db.session.execute(
                        text(
                            """
                            INSERT INTO points_wallet (user_id, balance)
                            VALUES (:user_id, :balance)
                            ON DUPLICATE KEY UPDATE balance = balance + :balance
                            """
                        ),
                        {
                            "user_id": user_id,
                            "balance": refund_points
                        }
                    )

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
                                'Prediction market refund',
                                'prediction_market',
                                :ref_id
                            )
                            """
                        ),
                        {
                            "user_id": user_id,
                            "delta_points": refund_points,
                            "ref_id": int(market_id)
                        }
                    )

            else:
                total_winning_pool = sum(int(row["points_wagered"]) for row in winners)

                for row in winners:
                    user_id = int(row["predictor_user_id"])
                    user_wager = int(row["points_wagered"])
                    payout = (total_pool * user_wager) // total_winning_pool

                    db.session.execute(
                        text(
                            """
                            INSERT INTO points_wallet (user_id, balance)
                            VALUES (:user_id, :balance)
                            ON DUPLICATE KEY UPDATE balance = balance + :balance
                            """
                        ),
                        {
                            "user_id": user_id,
                            "balance": payout
                        }
                    )

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
                                'Prediction market payout',
                                'prediction_market',
                                :ref_id
                            )
                            """
                        ),
                        {
                            "user_id": user_id,
                            "delta_points": payout,
                            "ref_id": int(market_id)
                        }
                    )

                db.session.execute(
                    text(
                        """
                        UPDATE prediction_market
                        SET
                            status = 'settled',
                            settlement_result = :settlement_result,
                            settled_by_admin_id = :admin_user_id,
                            settled_at = NOW(),
                            settlement_note = :settlement_note
                        WHERE market_id = :market_id
                          AND status = 'closed'
                          AND settlement_result IS NULL
                        """
                    ),
                    {
                        "settlement_result": normalized_result,
                        "admin_user_id": int(admin_user_id),
                        "settlement_note": final_admin_action,
                        "market_id": int(market_id)
                    }
                )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return _shape_prediction_market(_get_prediction_market_row(int(market_id)))


def close_prediction_market(user_id: int, market_id):
    user = _get_user_row(int(user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    if not market_id:
        raise ValueError("market_id is required")

    market = _get_prediction_market_row(int(market_id))

    if int(market["creator_user_id"]) != int(user_id):
        raise PermissionError("Only the market creator can close this market")

    if market["review_status"] != "approved":
        raise ValueError("Only approved markets can be closed")

    if market["status"] != "open":
        raise ValueError("Only open markets can be closed")

    run_query(
        """
        UPDATE prediction_market
        SET status = 'closed'
        WHERE market_id = :market_id
          AND creator_user_id = :user_id
          AND review_status = 'approved'
          AND status = 'open'
        """,
        params={
            "market_id": int(market_id),
            "user_id": int(user_id)
        },
        fetch=False,
        commit=True
    )

    return _shape_prediction_market(_get_prediction_market_row(int(market_id)))


def request_prediction_market_cancellation(user_id: int, market_id, reason: str):
    user = _get_user_row(int(user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    if not market_id:
        raise ValueError("market_id is required")

    final_reason = reason.strip() if isinstance(reason, str) else ""
    if not final_reason:
        raise ValueError("reason is required")

    market = _get_prediction_market_row(int(market_id))

    if int(market["creator_user_id"]) != int(user_id):
        raise PermissionError("Only the market creator can request cancellation")

    if market["review_status"] != "approved":
        raise ValueError("Only approved markets can request cancellation")

    if market["status"] not in ("open", "closed"):
        raise ValueError("Only open or closed markets can request cancellation")

    if market["settlement_result"] is not None:
        raise ValueError("Settled markets cannot request cancellation")

    if market["cancel_request_status"] == "pending":
        raise ValueError("Cancellation request already pending")

    run_query(
        """
        UPDATE prediction_market
        SET
            cancel_request_status = 'pending',
            cancel_request_reason = :reason,
            cancel_requested_at = NOW(),
            cancel_reviewed_by_admin_id = NULL,
            cancel_reviewed_at = NULL,
            cancel_review_note = NULL
        WHERE market_id = :market_id
          AND creator_user_id = :user_id
          AND review_status = 'approved'
          AND status IN ('open', 'closed')
          AND settlement_result IS NULL
        """,
        params={
            "reason": final_reason,
            "market_id": int(market_id),
            "user_id": int(user_id)
        },
        fetch=False,
        commit=True
    )

    return _shape_prediction_market(_get_prediction_market_row(int(market_id)))


def get_admin_prediction_cancel_review_queue(admin_user_id: int):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    rows = run_query(
        """
        SELECT
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN 1 ELSE 0 END), 0) AS yes_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN 1 ELSE 0 END), 0) AS no_bets,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'yes' THEN p.points_wagered ELSE 0 END), 0) AS yes_points,
            COALESCE(SUM(CASE WHEN p.prediction_value = 'no' THEN p.points_wagered ELSE 0 END), 0) AS no_points,
            COALESCE(COUNT(p.prediction_id), 0) AS total_bets,
            COALESCE(SUM(p.points_wagered), 0) AS total_points
        FROM prediction_market AS pm
        JOIN users_immutables AS ui
            ON pm.creator_user_id = ui.user_id
        LEFT JOIN prediction AS p
            ON pm.market_id = p.market_id
        WHERE pm.cancel_request_status = 'pending'
        GROUP BY
            pm.market_id,
            pm.creator_user_id,
            pm.title,
            pm.goal_text,
            pm.end_date,
            pm.status,
            pm.review_status,
            pm.reviewed_by_admin_id,
            pm.reviewed_at,
            pm.review_note,
            pm.settlement_result,
            pm.settled_by_admin_id,
            pm.settled_at,
            pm.settlement_note,
            pm.cancel_request_status,
            pm.cancel_request_reason,
            pm.cancel_requested_at,
            pm.cancel_reviewed_by_admin_id,
            pm.cancel_reviewed_at,
            pm.cancel_review_note,
            pm.created_at,
            pm.updated_at,
            ui.first_name,
            ui.last_name,
            ui.email
        ORDER BY pm.cancel_requested_at ASC, pm.market_id ASC
        """,
        fetch=True,
        commit=False
    )

    return [_shape_prediction_market(row) for row in rows]


def approve_prediction_market_cancellation(admin_user_id: int, market_id, admin_action=None):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    if not market_id:
        raise ValueError("market_id is required")

    market = _get_prediction_market_row(int(market_id))

    if market["cancel_request_status"] != "pending":
        raise ValueError("Only pending cancellation requests can be approved")

    final_admin_action = admin_action.strip() if isinstance(admin_action, str) and admin_action.strip() else "Cancellation approved by admin"

    predictions = run_query(
        """
        SELECT
            prediction_id,
            predictor_user_id,
            points_wagered
        FROM prediction
        WHERE market_id = :market_id
        ORDER BY prediction_id ASC
        """,
        params={"market_id": int(market_id)},
        fetch=True,
        commit=False
    )

    try:
        for row in predictions:
            user_id = int(row["predictor_user_id"])
            refund_points = int(row["points_wagered"])

            db.session.execute(
                text(
                    """
                    INSERT INTO points_wallet (user_id, balance)
                    VALUES (:user_id, :balance)
                    ON DUPLICATE KEY UPDATE balance = balance + :balance
                    """
                ),
                {
                    "user_id": user_id,
                    "balance": refund_points
                }
            )

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
                        'Prediction market refund',
                        'prediction_market',
                        :ref_id
                    )
                    """
                ),
                {
                    "user_id": user_id,
                    "delta_points": refund_points,
                    "ref_id": int(market_id)
                }
            )

        db.session.execute(
            text(
                """
                UPDATE prediction_market
                SET
                    status = 'cancelled',
                    settlement_result = 'cancelled',
                    cancel_request_status = 'approved',
                    cancel_reviewed_by_admin_id = :admin_user_id,
                    cancel_reviewed_at = NOW(),
                    cancel_review_note = :cancel_review_note,
                    settled_by_admin_id = :admin_user_id,
                    settled_at = NOW(),
                    settlement_note = :settlement_note
                WHERE market_id = :market_id
                  AND cancel_request_status = 'pending'
                """
            ),
            {
                "admin_user_id": int(admin_user_id),
                "cancel_review_note": final_admin_action,
                "settlement_note": final_admin_action,
                "market_id": int(market_id)
            }
        )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return _shape_prediction_market(_get_prediction_market_row(int(market_id)))


def reject_prediction_market_cancellation(admin_user_id: int, market_id, admin_action=None):
    if not _is_admin(admin_user_id):
        raise PermissionError("Forbidden")

    if not market_id:
        raise ValueError("market_id is required")

    market = _get_prediction_market_row(int(market_id))

    if market["cancel_request_status"] != "pending":
        raise ValueError("Only pending cancellation requests can be rejected")

    final_admin_action = admin_action.strip() if isinstance(admin_action, str) and admin_action.strip() else "Cancellation rejected by admin"

    run_query(
        """
        UPDATE prediction_market
        SET
            cancel_request_status = 'rejected',
            cancel_reviewed_by_admin_id = :admin_user_id,
            cancel_reviewed_at = NOW(),
            cancel_review_note = :cancel_review_note
        WHERE market_id = :market_id
          AND cancel_request_status = 'pending'
        """,
        params={
            "admin_user_id": int(admin_user_id),
            "cancel_review_note": final_admin_action,
            "market_id": int(market_id)
        },
        fetch=False,
        commit=True
    )

    return _shape_prediction_market(_get_prediction_market_row(int(market_id)))