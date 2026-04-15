# app/services/contracts/client_Contracts.py
from app.services import run_query
from datetime import date

def requestContract(user_id, coach_id):
    # Check if an existing contract already exists
    existing = run_query(
        """
        SELECT contract_id FROM user_coach_contract
        WHERE user_id = :user_id AND coach_id = :coach_id
        """,
        {"user_id": user_id, "coach_id": coach_id},
        fetch=True, commit=False
    )

    if existing:
        raise Exception("A contract request for this coach already exists") 

    coach_info = run_query(
        "SELECT price FROM coach WHERE coach_id = :coach_id",
        {"coach_id": coach_id},
        fetch=True, commit=False
    )

    if not coach_info:
        raise Exception("Coach not found")

    actual_price = coach_info[0]['price']

    #  Insert with the coaches price
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