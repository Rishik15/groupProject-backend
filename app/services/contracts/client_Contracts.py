from app.services import run_query
from datetime import date
from app.services.contracts.contract_Status import get_contract_status

def requestContract(user_id, coach_id):
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
            "contract_text": f"Pending contract at ${actual_price}/session. Waiting for coach approval."
        },
        fetch=False, commit=True
    )