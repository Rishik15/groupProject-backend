from app.services import run_query
from app.services.payments.add_Payment_Method import add_payment_method
from datetime import date
from app.services.contracts.contract_Status import get_contract_status


def get_client_active_contract(user_id):
    result = run_query(
        """
        SELECT
        ucc.contract_id,
        ucc.coach_id,
        ucc.agreed_price,
        CONCAT(ui.first_name, ' ', ui.last_name) AS coach_name
        FROM user_coach_contract ucc
        JOIN users_immutables ui ON ui.user_id = ucc.coach_id
        WHERE ucc.user_id = :user_id
        AND ucc.active = 1
        LIMIT 1
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )
    return result[0] if result else None


def requestContract(
    user_id: int,
    coach_id: int,
    is_recurring: bool,
    training_reason: str,
    preferred_schedule: str = "",
    notes: str = "",
    payment_method_id: int = None,
    card_number: str = None,
    card_brand: str = None,
    expiry_month: int = None,
    expiry_year: int = None,
):
    active_contract = get_client_active_contract(user_id)
    if active_contract:
        raise Exception("You already have an active coach")

    status = get_contract_status(user_id, coach_id)

    if status == "active":
        raise Exception("You already have an active contract with this coach")

    if status == "pending":
        raise Exception("You already have a pending request with this coach")

    coach_info = run_query(
        """
        SELECT price
        FROM coach
        WHERE coach_id = :coach_id
        """,
        {"coach_id": coach_id},
        fetch=True,
        commit=False,

    )

    if not coach_info:
        raise Exception("Coach not found")

    actual_price = coach_info[0]["price"]

    # Handle payment method
    if payment_method_id:
        existing = run_query(
            """
            SELECT payment_method_id FROM user_payment_method
            WHERE payment_method_id = :id AND user_id = :user_id
            """,
            {"id": payment_method_id, "user_id": user_id},
            fetch=True,
            commit=False,
        )
        if not existing:
            raise Exception("Payment method not found or does not belong to this user")

        run_query(
            "UPDATE user_payment_method SET is_default = 0 WHERE user_id = :user_id",
            {"user_id": user_id},
            fetch=False,
            commit=True,
        )
        run_query(
            "UPDATE user_payment_method SET is_default = 1 WHERE payment_method_id = :id",
            {"id": payment_method_id},
            fetch=False,
            commit=True,
        )
    else:
        card_last_four = str(card_number).replace(" ", "")[-4:]
        payment_method_id = add_payment_method(
            user_id=user_id,
            card_last_four=card_last_four,
            card_brand=card_brand,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
        )

    # Build parsable contract text
    contract_text = (
        f"training_reason:{training_reason}|"
        f"preferred_schedule:{preferred_schedule if preferred_schedule else 'Not provided'}|"
        f"notes:{notes if notes else 'Not provided'}|"
        f"payment_type:{'recurring' if is_recurring else 'one_time'}|"
        f"price:{actual_price}"
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
            "contract_text": contract_text,
            "is_recurring": 1 if is_recurring else 0,
        },
        fetch=False,
        commit=True,

    )
