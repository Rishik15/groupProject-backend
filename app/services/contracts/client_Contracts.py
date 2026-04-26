from app.services import run_query
from app.services.payments.add_Payment_Method import add_payment_method
from datetime import date
from app.services.contracts.contract_Status import get_contract_status


def requestContract(user_id: int, coach_id: int, is_recurring: bool, payment_method_id: int = None, card_number: str = None, card_brand: str = None, expiry_month: int = None, expiry_year: int = None):

    status = get_contract_status(user_id, coach_id)

    if status == "active":
        raise Exception("You already have an active contract with this coach")

    if status == "pending":
        raise Exception("You already have a pending request with this coach")

    coach_info = run_query(
        "SELECT price FROM coach WHERE coach_id = :coach_id",
        {"coach_id": coach_id},
        fetch=True, commit=False
    )

    if not coach_info:
        raise Exception("Coach not found")

    actual_price = coach_info[0]["price"]

    if payment_method_id:
        existing = run_query(
            """
            SELECT payment_method_id FROM user_payment_method
            WHERE payment_method_id = :id AND user_id = :user_id
            """,
            {"id": payment_method_id, "user_id": user_id},
            fetch=True, commit=False
        )

        if not existing:
            raise Exception("Payment method not found or does not belong to this user")

        run_query(
            "UPDATE user_payment_method SET is_default = 0 WHERE user_id = :user_id",
            {"user_id": user_id}, fetch=False, commit=True
        )
        run_query(
            "UPDATE user_payment_method SET is_default = 1 WHERE payment_method_id = :id",
            {"id": payment_method_id}, fetch=False, commit=True
        )

    else:
        card_last_four = str(card_number).replace(" ", "")[-4:]
        payment_method_id = add_payment_method(
            user_id=user_id,
            card_last_four=card_last_four,
            card_brand=card_brand,
            expiry_month=expiry_month,
            expiry_year=expiry_year
        )

    run_query(
        """
        INSERT INTO user_coach_contract
            (coach_id, user_id, agreed_price, start_date, contract_text, active, is_recurring)
        VALUES
            (:coach_id, :user_id, :agreed_price, :start_date, :contract_text, 0, :is_recurring)
        """,
        {
            "coach_id": coach_id,
            "user_id": user_id,
            "agreed_price": actual_price,
            "start_date": date.today(),
            "contract_text": f"{'Recurring subscription' if is_recurring else 'One-time coaching'} at ${actual_price}/session. Waiting for coach approval.",
            "is_recurring": 1 if is_recurring else 0
        },
        fetch=False, commit=True
    )