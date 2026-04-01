from .. import run_query

def getCoachInformation( coach_id: int):
    try:
        ret = run_query(
            """
                select 
                    ui.first_name, 
                    ui.last_name, 
                    c.price, 
                    c.coach_description,
                    um.profile_picture,
                    um.weight, 
                    um.height, 
                from coach as c 
                inner join 
                users_immutables as ui
                on c.coach_id = ui.user_id
                inner join 
                user_mutables as um
                on ui.user_id = um.user_id
                where coach_id = :cid; 
            """,
            {"cid" : coach_id},
            commit=False, 
            fetch=True 

        )
        return ret

    except Exception as e: 
        raise e