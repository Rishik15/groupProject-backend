from app.services import run_query

def delete_account_service(user_id):
    query = "DELETE FROM users_immutables WHERE user_id = :id"
    params = {"id": user_id}
    
    # We set commit=True because we are changing the database 
    return run_query(query, params=params, fetch=False, commit=True) 