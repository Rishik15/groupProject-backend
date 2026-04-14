from app.services import run_query
from datetime import date


def getCoachContractsService(coach_id: int):
    try:
        ret = run_query(
            """
            SELECT
                ucc.user_id,
                ucc.contract_id,
                ucc.created_at,
                ucc.updated_at,
                ucc.start_date,
                ucc.end_date,
                ucc.agreed_price,
                ucc.contract_text,
                ucc.active
            FROM user_coach_contract AS ucc
            WHERE ucc.coach_id = :c_id
            ORDER BY ucc.created_at DESC
            """,
            {"c_id": coach_id},
            commit=False,
            fetch=True
        )
        return ret
    except Exception as e:
        raise e


def getUsersPerContract(user_id: int):
    try:
        ret = run_query(
            """
            SELECT
                first_name,
                last_name
            FROM users_immutables
            WHERE user_id = :user_id
            """,
            {"user_id": user_id},
            commit=False,
            fetch=True
        )
        return ret
    except Exception as e:
        raise e


def getCoachContractsByStatusService(coach_id: int, active: int):
    try:
        ret = run_query(
            """
            SELECT
                contract_id,
                coach_id,
                user_id,
                agreed_price,
                start_date,
                end_date,
                contract_text,
                active,
                created_at,
                updated_at
            FROM user_coach_contract
            WHERE coach_id = :coach_id
              AND active = :active
            ORDER BY created_at DESC
            """,
            {"coach_id": coach_id, "active": active},
            commit=False,
            fetch=True
        )
        return ret
    except Exception as e:
        raise e


def getSingleCoachContractService(coach_id: int, contract_id: int):
    try:
        ret = run_query(
            """
            SELECT
                contract_id,
                coach_id,
                user_id,
                agreed_price,
                start_date,
                end_date,
                contract_text,
                active,
                created_at,
                updated_at
            FROM user_coach_contract
            WHERE coach_id = :coach_id
              AND contract_id = :contract_id
            LIMIT 1
            """,
            {"coach_id": coach_id, "contract_id": contract_id},
            commit=False,
            fetch=True
        )
        return ret[0] if ret else None
    except Exception as e:
        raise e


def coachAcceptsContractService(contract_id: int):
    try:
        today = date.today().isoformat()
        run_query(
            """
            UPDATE user_coach_contract
            SET active = 1,
                start_date = :today
            WHERE contract_id = :contract_id
            """,
            {"contract_id": contract_id, "today": today},
            fetch=False,
            commit=True
        )
    except Exception as e:
        raise e


def coachRejectsContractService(contract_id: int):
    try:
        today = date.today().isoformat()
        run_query(
            """
            UPDATE user_coach_contract
            SET active = 0,
                end_date = :today
            WHERE contract_id = :contract_id
            """,
            {"contract_id": contract_id, "today": today},
            fetch=False,
            commit=True
        )
    except Exception as e:
        raise e


def coachTerminatesContractService(contract_id: int):
    try:
        today = date.today().isoformat()
        run_query(
            """
            UPDATE user_coach_contract
            SET active = 0,
                end_date = :today
            WHERE contract_id = :contract_id
            """,
            {"contract_id": contract_id, "today": today},
            fetch=False,
            commit=True
        )
    except Exception as e:
        raise e