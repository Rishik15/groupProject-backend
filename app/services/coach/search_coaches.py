from app.services import run_query


def search_coaches(name, filters):
    query = "SELECT u.first_name, c.price, c.coach_description FROM users_immutables u JOIN coach c ON u.user_id = c.coach_id WHERE 1=1"
    params = {}
    if name:
        query += " AND u.first_name LIKE :name"
        params["name"] = f"%{name}%" # Adding wildcard character to the name
    if filters:
        for tag in filters:
            query += f" AND c.coach_description LIKE :tag_{tag}" 
            params[f"tag_{tag}"] = f"%{tag}%"
    return run_query(query, params=params, fetch=True, commit=False)