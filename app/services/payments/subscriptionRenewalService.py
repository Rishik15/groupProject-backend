from app.services import run_query
from app.sockets.notifications.notifications import send_notification


def get_due_subscription_contracts():
    return run_query(
        """
        SELECT
            contract_id,
            user_id,
            coach_id,
            agreed_price,
            start_date,
            next_billing_date
        FROM user_coach_contract
        WHERE active = 1
          AND is_recurring = 1
          AND next_billing_date IS NOT NULL
          AND next_billing_date <= CURDATE();
        """,
        {},
        fetch=True,
        commit=False,
    )


def get_default_payment_method(user_id: int):
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

    return result[0]["payment_method_id"] if result else None


def payment_exists_for_billing_period(
    user_id: int,
    coach_id: int,
    billing_start,
    billing_end,
):
    result = run_query(
        """
        SELECT payment_id
        FROM payment
        WHERE user_id = :user_id
          AND coach_id = :coach_id
          AND payment_type IN ('subscription', 'coaching_fee')
          AND status = 'completed'
          AND DATE(paid_at) >= :billing_start
          AND DATE(paid_at) < :billing_end
        LIMIT 1;
        """,
        {
            "user_id": user_id,
            "coach_id": coach_id,
            "billing_start": billing_start,
            "billing_end": billing_end,
        },
        fetch=True,
        commit=False,
    )

    return result[0] if result else None


def create_subscription_payment(
    user_id: int,
    coach_id: int,
    payment_method_id,
    amount,
    billing_start,
    billing_end,
):
    description = (
        f"Monthly subscription payment for coach #{coach_id}. "
        f"Billing period: {billing_start} to {billing_end}."
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
                'subscription',
                :description,
                NOW()
            );
        """,
        {
            "user_id": user_id,
            "coach_id": coach_id,
            "payment_method_id": payment_method_id,
            "amount": amount,
            "description": description,
        },
        fetch=False,
        commit=True,
    )


def move_next_billing_date(contract_id: int):
    run_query(
        """
        UPDATE user_coach_contract
        SET next_billing_date = DATE_ADD(next_billing_date, INTERVAL 1 MONTH)
        WHERE contract_id = :contract_id
          AND active = 1
          AND is_recurring = 1;
        """,
        {"contract_id": contract_id},
        fetch=False,
        commit=True,
    )


def notify_subscription_payment_completed(
    user_id: int,
    coach_id: int,
    contract_id: int,
    amount,
    billing_start,
    billing_end,
):
    amount_text = f"${float(amount):.2f}"

    return send_notification(
        user_id=user_id,
        mode="client",
        notification_type="subscription_payment",
        title="Subscription payment completed",
        body=(
            f"Your monthly coach subscription payment of {amount_text} "
            f"has been added to your payment history."
        ),
        route="/client/billing",
        metadata={
            "route": "/client/billing",
            "coach_id": coach_id,
            "contract_id": contract_id,
            "amount": str(amount),
            "billing_start": str(billing_start),
            "billing_end": str(billing_end),
        },
        reference_id=contract_id,
        extra_event="subscription_payment_completed",
        extra_payload={
            "route": "/client/billing",
            "coach_id": coach_id,
            "contract_id": contract_id,
            "amount": str(amount),
            "billing_start": str(billing_start),
            "billing_end": str(billing_end),
        },
    )


def process_due_subscription_payments():
    contracts = get_due_subscription_contracts()

    processed_count = 0
    skipped_count = 0
    results = []

    for contract in contracts:
        contract_id = contract["contract_id"]
        user_id = contract["user_id"]
        coach_id = contract["coach_id"]
        amount = contract["agreed_price"]
        billing_end = contract["next_billing_date"]

        billing_period = run_query(
            """
            SELECT DATE_SUB(:billing_end, INTERVAL 1 MONTH) AS billing_start;
            """,
            {"billing_end": billing_end},
            fetch=True,
            commit=False,
        )

        billing_start = billing_period[0]["billing_start"]

        existing_payment = payment_exists_for_billing_period(
            user_id=user_id,
            coach_id=coach_id,
            billing_start=billing_start,
            billing_end=billing_end,
        )

        if existing_payment:
            move_next_billing_date(contract_id)

            skipped_count += 1
            results.append(
                {
                    "contract_id": contract_id,
                    "user_id": user_id,
                    "coach_id": coach_id,
                    "status": "skipped_existing_payment",
                    "billing_start": str(billing_start),
                    "billing_end": str(billing_end),
                }
            )

            continue

        payment_method_id = get_default_payment_method(user_id)

        create_subscription_payment(
            user_id=user_id,
            coach_id=coach_id,
            payment_method_id=payment_method_id,
            amount=amount,
            billing_start=billing_start,
            billing_end=billing_end,
        )

        notification = notify_subscription_payment_completed(
            user_id=user_id,
            coach_id=coach_id,
            contract_id=contract_id,
            amount=amount,
            billing_start=billing_start,
            billing_end=billing_end,
        )

        move_next_billing_date(contract_id)

        processed_count += 1
        results.append(
            {
                "contract_id": contract_id,
                "user_id": user_id,
                "coach_id": coach_id,
                "status": "processed",
                "billing_start": str(billing_start),
                "billing_end": str(billing_end),
                "amount": str(amount),
                "notification_id": notification.get("id") if notification else None,
            }
        )

    return {
        "processed_count": processed_count,
        "skipped_count": skipped_count,
        "total_due": len(contracts),
        "results": results,
    }
