from app.services import run_query


def getCoachContracts(coach_id: int):

    results = run_query(
        """
        SELECT 
            ucc.contract_id,
            ucc.user_id,
            ucc.start_date,
            ucc.end_date,
            ucc.active,
            ucc.agreed_price,
            ucc.contract_text,
            ui.first_name,
            ui.last_name
        FROM user_coach_contract ucc
        JOIN users_immutables ui ON ui.user_id = ucc.user_id
        WHERE ucc.coach_id = :coach_id
        ORDER BY ucc.created_at DESC
        """,
        {"coach_id": coach_id},
    )

    pending = []
    present = []
    history = []

    for r in results:
        contract = {
            "contract_id": r["contract_id"],
            "user_id": r["user_id"],
            "name": f"{r['first_name']} {r['last_name']}",
            "start_date": r["start_date"],
            "end_date": r["end_date"],
            "price": r["agreed_price"],
            "details": r["contract_text"],
        }

        if r["active"] == 1 and r["end_date"] is None:
            pending.append(contract)

        elif r["active"] == 1 and r["end_date"] is not None:
            # check if still ongoing
            from datetime import date

            if r["end_date"] >= date.today():
                present.append(contract)
            else:
                history.append(contract)

        else:
            history.append(contract)

    return {"pending": pending, "present": present, "history": history}
