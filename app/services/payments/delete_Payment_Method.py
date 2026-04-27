from app.services import run_query


def delete_payment_method(user_id: int, payment_method_id: int):

    existing = run_query(
        """
        SELECT payment_method_id, is_default FROM user_payment_method
        WHERE payment_method_id = :payment_method_id AND user_id = :user_id
        """,
        {"payment_method_id": payment_method_id, "user_id": user_id},
        fetch=True, commit=False
    )

    if not existing:
        raise ValueError("Payment method not found or does not belong to this user")

    was_default = existing[0]["is_default"]

    run_query(
        """
        DELETE FROM user_payment_method
        WHERE payment_method_id = :payment_method_id AND user_id = :user_id
        """,
        {"payment_method_id": payment_method_id, "user_id": user_id},
        fetch=False, commit=True
    )

    if was_default:
        run_query(
            """
            UPDATE user_payment_method
            SET is_default = 1
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT 1
            """,
            {"user_id": user_id},
            fetch=False, commit=True
        )