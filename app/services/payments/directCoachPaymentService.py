from datetime import date, datetime

from app.services import run_query


def format_date(value):
    if value is None:
        return None

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    return str(value)


def get_active_client_coach_contract(user_id: int):
    result = run_query(
        """
        SELECT
            ucc.contract_id,
            ucc.user_id,
            ucc.coach_id,
            ucc.agreed_price,
            ucc.active,
            ucc.is_recurring,
            ucc.next_billing_date,
            ui.first_name AS coach_first_name,
            ui.last_name AS coach_last_name
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

    return result[0] if result else None


def get_default_payment_method(user_id: int):
    result = run_query(
        """
        SELECT
            payment_method_id,
            card_brand,
            card_last_four,
            expiry_month,
            expiry_year
        FROM user_payment_method
        WHERE user_id = :user_id
          AND is_default = 1
        LIMIT 1;
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    return result[0] if result else None


def format_payment(payment):
    if not payment:
        return None

    return {
        "payment_id": payment["payment_id"],
        "amount": float(payment["amount"]),
        "currency": payment["currency"],
        "paid_at": format_date(payment["paid_at"]),
        "payment_type": payment["payment_type"],
        "status": payment["status"],
        "coach": (
            {
                "coach_id": payment["coach_id"],
                "first_name": payment["coach_first_name"],
                "last_name": payment["coach_last_name"],
            }
            if payment["coach_id"]
            else None
        ),
        "payment_method": (
            {
                "card_brand": payment["card_brand"],
                "card_last_four": payment["card_last_four"],
                "expiry_month": payment["expiry_month"],
                "expiry_year": payment["expiry_year"],
            }
            if payment["payment_method_id"]
            else None
        ),
    }


def get_payment_detail(payment_id: int, user_id: int):
    result = run_query(
        """
        SELECT
            p.payment_id,
            p.user_id,
            p.coach_id,
            p.payment_method_id,
            p.amount,
            p.currency,
            p.status,
            p.payment_type,
            p.paid_at,
            coach_ui.first_name AS coach_first_name,
            coach_ui.last_name AS coach_last_name,
            upm.card_brand,
            upm.card_last_four,
            upm.expiry_month,
            upm.expiry_year
        FROM payment p
        LEFT JOIN users_immutables coach_ui
            ON coach_ui.user_id = p.coach_id
        LEFT JOIN user_payment_method upm
            ON upm.payment_method_id = p.payment_method_id
        WHERE p.payment_id = :payment_id
          AND p.user_id = :user_id
        LIMIT 1;
        """,
        {
            "payment_id": payment_id,
            "user_id": user_id,
        },
        fetch=True,
        commit=False,
    )

    return format_payment(result[0]) if result else None


def pay_current_coach_now(user_id: int):
    contract = get_active_client_coach_contract(user_id)

    if not contract:
        raise ValueError("You currently have no coach")

    payment_method = get_default_payment_method(user_id)

    if not payment_method:
        raise ValueError("Please add a default payment method before paying your coach")

    description = (
        f"Direct coach payment for coach #{contract['coach_id']} "
        f"under contract #{contract['contract_id']}."
    )

    run_query(
        """
        INSERT INTO payment
            (
                user_id,
                coach_id,
                payment_method_id,
                amount,
                currency,
                status,
                payment_type,
                description,
                paid_at
            )
        VALUES
            (
                :user_id,
                :coach_id,
                :payment_method_id,
                :amount,
                'USD',
                'completed',
                'coaching_fee',
                :description,
                NOW()
            );
        """,
        {
            "user_id": user_id,
            "coach_id": contract["coach_id"],
            "payment_method_id": payment_method["payment_method_id"],
            "amount": contract["agreed_price"],
            "description": description,
        },
        fetch=False,
        commit=True,
    )

    created_payment = run_query(
        """
        SELECT payment_id
        FROM payment
        WHERE user_id = :user_id
          AND coach_id = :coach_id
          AND payment_type = 'coaching_fee'
          AND status = 'completed'
        ORDER BY payment_id DESC
        LIMIT 1;
        """,
        {
            "user_id": user_id,
            "coach_id": contract["coach_id"],
        },
        fetch=True,
        commit=False,
    )

    if not created_payment:
        raise ValueError("Payment was created but could not be loaded")

    return get_payment_detail(created_payment[0]["payment_id"], user_id)
