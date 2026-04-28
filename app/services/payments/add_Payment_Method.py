from app.services import run_query


def add_payment_method(user_id: int, card_last_four: str, card_brand: str, expiry_month: int, expiry_year: int):

    existing = run_query(
        """
        SELECT payment_method_id FROM user_payment_method
        WHERE user_id = :user_id
        AND card_last_four = :card_last_four
        AND card_brand = :card_brand
        AND expiry_month = :expiry_month
        AND expiry_year = :expiry_year
        """,
        {
            "user_id": user_id,
            "card_last_four": card_last_four,
            "card_brand": card_brand,
            "expiry_month": expiry_month,
            "expiry_year": expiry_year
        },
        fetch=True, commit=False
    )

    if existing:
        payment_method_id = existing[0]["payment_method_id"]

        run_query(
            "UPDATE user_payment_method SET is_default = 0 WHERE user_id = :user_id",
            {"user_id": user_id},
            fetch=False, commit=True
        )

        run_query(
            "UPDATE user_payment_method SET is_default = 1 WHERE payment_method_id = :id",
            {"id": payment_method_id},
            fetch=False, commit=True
        )

        return payment_method_id

    run_query(
        "UPDATE user_payment_method SET is_default = 0 WHERE user_id = :user_id",
        {"user_id": user_id},
        fetch=False, commit=True
    )

    run_query(
        """
        INSERT INTO user_payment_method (user_id, card_last_four, card_brand, expiry_month, expiry_year, is_default)
        VALUES (:user_id, :card_last_four, :card_brand, :expiry_month, :expiry_year, 1)
        """,
        {
            "user_id": user_id,
            "card_last_four": card_last_four,
            "card_brand": card_brand,
            "expiry_month": expiry_month,
            "expiry_year": expiry_year
        },
        fetch=False, commit=True
    )

    result = run_query(
        "SELECT LAST_INSERT_ID() AS payment_method_id",
        fetch=True, commit=False
    )

    return result[0]["payment_method_id"]