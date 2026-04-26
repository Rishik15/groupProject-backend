from app.services import run_query
from datetime import date
from app.services.contracts.contract_Status import get_contract_status


def get_client_active_contract(user_id):
    result = run_query(
        """
        SELECT contract_id, coach_id, user_id
        FROM user_coach_contract
        WHERE user_id = :user_id
        AND active = 1
        LIMIT 1
        """,
        {"user_id": user_id},
        fetch=True,
        commit=False,
    )

    return result[0] if result else None


def requestContract(
    user_id,
    coach_id,
    training_reason,
    goals,
    preferred_schedule,
    notes,
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

    contract_text = f"""
Training Reason:
{training_reason}

Goals:
{goals}

Preferred Schedule:
{preferred_schedule if preferred_schedule else "Not provided"}

Extra Notes:
{notes if notes else "Not provided"}

Requested Price:
${actual_price}/session

Status:
Waiting for coach approval.
""".strip()

    run_query(
        """
        INSERT INTO user_coach_contract
            (coach_id, user_id, agreed_price, start_date, contract_text, active)
        VALUES
            (:coach_id, :user_id, :agreed_price, :start_date, :contract_text, 0)
        """,
        {
            "coach_id": coach_id,
            "user_id": user_id,
            "agreed_price": actual_price,
            "start_date": date.today(),
            "contract_text": contract_text,
        },
        fetch=False,
        commit=True,
    )
