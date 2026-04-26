from app.services import run_query


def set_default_payment_method(user_id: int, payment_method_id: int):

    existing = run_query(
        """
        SELECT payment_method_id FROM user_payment_method
        WHERE payment_method_id = :payment_method_id AND user_id = :user_id
        """,
        {"payment_method_id": payment_method_id, "user_id": user_id},
        fetch=True, commit=False
    )

    if not existing:
        raise ValueError("Payment method not found or does not belong to this user")

    run_query(
        """
        UPDATE user_payment_method
        SET is_default = 0
        WHERE user_id = :user_id
        """,
        {"user_id": user_id},
        fetch=False, commit=True
    )

    run_query(
        """
        UPDATE user_payment_method
        SET is_default = 1
        WHERE payment_method_id = :payment_method_id
        """,
        {"payment_method_id": payment_method_id},
        fetch=False, commit=True
    )