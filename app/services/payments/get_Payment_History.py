from app.services import run_query


def get_payment_history(user_id: int):
    return run_query(
        """
        SELECT
            p.payment_id,
            p.amount,
            p.currency,
            p.status,
            p.payment_type,
            p.description,
            p.paid_at,
            c.coach_id,
            ui.first_name AS coach_first_name,
            ui.last_name  AS coach_last_name,
            pm.card_brand,
            pm.card_last_four,
            pm.expiry_month,
            pm.expiry_year
        FROM payment p
        LEFT JOIN coach c
            ON p.coach_id = c.coach_id
        LEFT JOIN users_immutables ui
            ON c.coach_id = ui.user_id
        LEFT JOIN user_payment_method pm
            ON p.payment_method_id = pm.payment_method_id
        WHERE p.user_id = :user_id
        ORDER BY p.paid_at DESC
        """,
        {"user_id": user_id},
        fetch=True, commit=False
    )