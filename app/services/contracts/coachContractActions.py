from app.services import run_query
from datetime import datetime 
def getCoachContractsService(coach_id : int):
    try:
        ret = run_query(
            """
                select 
                    ucc.user_id, 
                    ucc.contract_id, 
                    ucc.created_at,  
                    ucc.start_date, 
                    ucc.end_date, 
                    ucc.agreed_price, 
                    ucc.contract_text,
                    ucc.active
                from
                    user_coach_contract as ucc 
                where
                    coach_id = :c_id
            """,
            {"c_id" : coach_id},
            commit=False,
            fetch=True
        )
        return ret
    except Exception as e: 
        raise e
        
def getUsersPerContract(user_id):
    try:
        ret = run_query(
            """
            select 
                first_name, 
                last_name
            from users_immutables 
            where user_id = :user_id
            """,
            {"user_id": user_id},
            commit=False,
            fetch=True
        )
        return ret
    except Exception as e: 
        raise e

def getCoachActiveContractsService(coach_id: int , active: int):
    try: 
        ret = 
        run_query(
            """
                select * 
                from user_coach_contract
                where coach_id = :coach_id AND active = :active;
            """,
            {"coach_id": coach_id, "active" : active},
            commit=False,
            fetch=True
        )
        return ret
    except Exception as e:
        raise e

def coachAcceptsContract():
