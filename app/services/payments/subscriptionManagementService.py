from datetime import date, datetime

from app.services import run_query


def format_date(value):
    if value is None:
        return None

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    return str(value)


def format_contract(contract):
    if not contract:
        return None

    return {
        "contract_id": contract["contract_id"],
        "coach_id": contract["coach_id"],
        "user_id": contract["user_id"],
        "agreed_price": float(contract["agreed_price"]),
        "coach_name": contract["coach_name"],
        "is_recurring": int(contract["is_recurring"]),
        "next_billing_date": format_date(contract["next_billing_date"]),
        "start_date": format_date(contract["start_date"]),
        "end_date": format_date(contract["end_date"]),
        "active": int(contract["active"]),
    }


def get_active_client_subscription_contract(user_id: int):
    result = run_query(
        """
        SELECT
            ucc.contract_id,
            ucc.coach_id,
            ucc.user_id,
            ucc.agreed_price,
            ucc.start_date,
            ucc.end_date,
            ucc.active,
            ucc.is_recurring,
            ucc.next_billing_date,
            CONCAT(ui.first_name, ' ', ui.last_name) AS coach_name
        FROM user_coach_contract ucc
        JOIN coach c
            ON c.coach_id = ucc.coach_id
        JOIN users_immutables ui
            ON ui.user_id = c.coach_id
        WHERE ucc.user_id = :user_id
          AND ucc.active = 1
        LIMIT 1;
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    return format_contract(result[0]) if result else None


def user_has_default_payment_method(user_id: int):
    result = run_query(
        """
        SELECT payment_method_id
        FROM user_payment_method
        WHERE user_id = :user_id
          AND is_default = 1
        LIMIT 1;
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    return bool(result)


def start_client_subscription(user_id: int):
    contract = get_active_client_subscription_contract(user_id)

    if not contract:
        raise ValueError("You do not have an active coach contract")

    if contract["is_recurring"] == 1:
        return contract

    if not user_has_default_payment_method(user_id):
        raise ValueError(
            "Please add a default payment method before starting a subscription"
        )

    run_query(
        """
        UPDATE user_coach_contract
        SET is_recurring = 1,
            next_billing_date = DATE_ADD(CURDATE(), INTERVAL 1 MONTH)
        WHERE contract_id = :contract_id
          AND user_id = :user_id
          AND active = 1;
        """,
        {
            "contract_id": contract["contract_id"],
            "user_id": user_id,
        },
        fetch=False,
        commit=True,
    )

    return get_active_client_subscription_contract(user_id)


def cancel_client_subscription(user_id: int):
    contract = get_active_client_subscription_contract(user_id)

    if not contract:
        raise ValueError("You do not have an active coach contract")

    if contract["is_recurring"] == 0:
        return contract

    run_query(
        """
        UPDATE user_coach_contract
        SET is_recurring = 0,
            next_billing_date = NULL
        WHERE contract_id = :contract_id
          AND user_id = :user_id
          AND active = 1;
        """,
        {
            "contract_id": contract["contract_id"],
            "user_id": user_id,
        },
        fetch=False,
        commit=True,
    )

    return get_active_client_subscription_contract(user_id)
