from app.services import run_query


def get_payment_methods(user_id: int):
    return run_query(
        """
        SELECT
            payment_method_id,
            card_last_four,
            card_brand,
            expiry_month,
            expiry_year,
            is_default
        FROM user_payment_method
        WHERE user_id = :user_id
        ORDER BY is_default DESC, created_at DESC
        """,
        {"user_id": user_id},
        fetch=True, commit=False
    )