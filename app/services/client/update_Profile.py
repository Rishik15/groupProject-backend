from app.services import run_query 

def update_client_metrics(user_id, weight=None, height=None, goal_weight=None):
    query = """
        UPDATE user_mutables 
        SET weight = COALESCE(:weight, weight), 
            height = COALESCE(:height, height), 
            goal_weight = COALESCE(:goal_weight, goal_weight)
        WHERE user_id = :user_id
    """
    params = {
        "user_id": user_id,
        "weight": weight,
        "height": height,
        "goal_weight": goal_weight
    }
    
    return run_query(query, params=params, fetch=False, commit=True)