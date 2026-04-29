from datetime import datetime
from sqlalchemy import text
from app import db
from app.services import run_query

DAILY_SURVEY_REWARD_POINTS = 100


def _get_user_row(user_id: int):
    rows = run_query(
        """
        SELECT user_id, account_status
        FROM users_immutables
        WHERE user_id = :user_id
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False,
    )

    if not rows:
        raise ValueError("User not found")

    return rows[0]


def _get_or_create_wallet_row(user_id: int):
    rows = run_query(
        """
        SELECT user_id, balance
        FROM points_wallet
        WHERE user_id = :user_id
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False,
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
        commit=True,
    )

    rows = run_query(
        """
        SELECT user_id, balance
        FROM points_wallet
        WHERE user_id = :user_id
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False,
    )

    return rows[0]


def _already_rewarded_today(user_id: int):
    rows = run_query(
        """
        SELECT txn_id, created_at
        FROM points_txn
        WHERE user_id = :user_id
          AND reason = 'Daily survey reward'
          AND DATE(created_at) = CURDATE()
        LIMIT 1
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False,
    )

    return len(rows) > 0


def reward_daily_survey(user_id: int):
    user_id = int(user_id)

    user = _get_user_row(user_id)

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    wallet_before = _get_or_create_wallet_row(user_id)

    print("DAILY REWARD USER:", user_id)
    print("DAILY REWARD WALLET BEFORE:", dict(wallet_before))

    if _already_rewarded_today(user_id):
        wallet_now = run_query(
            """
            SELECT user_id, balance
            FROM points_wallet
            WHERE user_id = :user_id
            """,
            params={"user_id": user_id},
            fetch=True,
            commit=False,
        )[0]

        print("DAILY REWARD ALREADY AWARDED:", dict(wallet_now))

        return {
            "already_awarded": True,
            "points_awarded": 0,
            "new_balance": int(wallet_now["balance"]),
        }

    try:
        db.session.execute(
            text("""
                UPDATE points_wallet
                SET balance = balance + :points
                WHERE user_id = :user_id
                """),
            {
                "points": DAILY_SURVEY_REWARD_POINTS,
                "user_id": user_id,
            },
        )

        db.session.execute(
            text("""
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
                    'Daily survey reward',
                    'daily_survey',
                    NULL
                )
                """),
            {
                "user_id": user_id,
                "delta_points": DAILY_SURVEY_REWARD_POINTS,
            },
        )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    updated_wallet = run_query(
        """
        SELECT user_id, balance
        FROM points_wallet
        WHERE user_id = :user_id
        """,
        params={"user_id": user_id},
        fetch=True,
        commit=False,
    )[0]

    print("DAILY REWARD WALLET AFTER:", dict(updated_wallet))

    return {
        "already_awarded": False,
        "points_awarded": DAILY_SURVEY_REWARD_POINTS,
        "new_balance": int(updated_wallet["balance"]),
    }
