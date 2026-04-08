from app.services import run_query

def getCoachContractsService(coach_id : int):
    try:
        ret = run_query(
            """
                select 
                    ucc.contract_id, 
                    ucc.created_at,  
                    ucc.start_date, 
                    ucc.end_date, 
                    ucc.agreed_price, 
                    ucc.contract_text 
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