from app.services import run_query

def getCoachContractsService(coach_id : int):
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

def getUsersPerContract(contract):

