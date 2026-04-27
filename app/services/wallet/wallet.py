# app/services/wallet/wallet.py
from app.services import run_query


def _get_user_row(user_id: int):
    rows = run_query(
        """
        SELECT
            user_id,
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


def _shape_wallet(row):
    return {
        "user_id": row["user_id"],
        "balance": int(row["balance"]),
        "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
    }


def _shape_wallet_transaction(row):
    return {
        "txn_id": row["txn_id"],
        "user_id": row["user_id"],
        "delta_points": int(row["delta_points"]),
        "reason": row["reason"],
        "ref_type": row["ref_type"],
        "ref_id": row["ref_id"],
        "created_at": row["created_at"].isoformat() if row["created_at"] is not None else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] is not None else None,
    }


def get_wallet(user_id: int):
    user = _get_user_row(int(user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    wallet = _get_or_create_wallet_row(int(user_id))
    return _shape_wallet(wallet)


def get_wallet_transactions(user_id: int):
    user = _get_user_row(int(user_id))

    if user["account_status"] != "active":
        raise ValueError("User account is not active")

    _get_or_create_wallet_row(int(user_id))

    rows = run_query(
        """
        SELECT
            txn_id,
            user_id,
            delta_points,
            reason,
            ref_type,
            ref_id,
            created_at,
            updated_at
        FROM points_txn
        WHERE user_id = :user_id
        ORDER BY created_at DESC, txn_id DESC
        """,
        params={"user_id": int(user_id)},
        fetch=True,
        commit=False
    )

    return [_shape_wallet_transaction(row) for row in rows]