from datetime import date

from app.services import run_query
from app.services.payments.add_Payment_Method import add_payment_method
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


def get_payment_method(user_id, payment_method_id):
    result = run_query(
        """
        SELECT payment_method_id
        FROM user_payment_method
        WHERE payment_method_id = :payment_method_id
        AND user_id = :user_id
        LIMIT 1
        """,
        {
            "payment_method_id": payment_method_id,
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    return result[0] if result else None


def set_default_payment_method(user_id, payment_method_id):
    run_query(
        """
        UPDATE user_payment_method
        SET is_default = 0
        WHERE user_id = :user_id
        """,
        {"user_id": user_id},
        fetch=False,
        commit=True,
    )

    run_query(
        """
        UPDATE user_payment_method
        SET is_default = 1
        WHERE payment_method_id = :payment_method_id
        AND user_id = :user_id
        """,
        {
            "payment_method_id": payment_method_id,
            "user_id": user_id,
        },
        fetch=False,
        commit=True,
    )


def get_coach_price(coach_id):
    result = run_query(
        """
        SELECT price
        FROM coach
        WHERE coach_id = :coach_id
        LIMIT 1
        """,
        {"coach_id": coach_id},
        fetch=True,
        commit=False,
    )

    return result[0]["price"] if result else None


def requestContract(
    user_id: int,
    coach_id: int,
    is_recurring: bool,
    training_reason: str,
    goals: str,
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

    actual_price = get_coach_price(coach_id)

    if actual_price is None:
        raise Exception("Coach not found")

    if payment_method_id:
        existing_payment_method = get_payment_method(user_id, payment_method_id)

        if not existing_payment_method:
            raise Exception("Payment method not found or does not belong to this user")

        set_default_payment_method(user_id, payment_method_id)

    else:
        clean_card_number = str(card_number).replace(" ", "")
        card_last_four = clean_card_number[-4:]

        payment_method_id = add_payment_method(
            user_id=user_id,
            card_last_four=card_last_four,
            card_brand=card_brand,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
        )

    contract_text = (
        f"training_reason:{training_reason}|"
        f"goals:{goals}|"
        f"preferred_schedule:{preferred_schedule if preferred_schedule else 'Not provided'}|"
        f"notes:{notes if notes else 'Not provided'}|"
        f"payment_type:{'recurring' if is_recurring else 'one_time'}|"
        f"price:{actual_price}|"
        f"payment_note:Payment method saved for contract start. No charge is made when the request is sent."
    )

    result = run_query(
        """
        INSERT INTO user_coach_contract
            (
                coach_id,
                user_id,
                agreed_price,
                start_date,
                contract_text,
                active,
                is_recurring
            )
        VALUES
            (
                :coach_id,
                :user_id,
                :agreed_price,
                :start_date,
                :contract_text,
                0,
                :is_recurring
            )
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

    contract_id = None

    if isinstance(result, dict):
        contract_id = result.get("lastrowid") or result.get("contract_id")

    return {
        "contract_id": contract_id,
        "payment_method_id": payment_method_id,
    }
