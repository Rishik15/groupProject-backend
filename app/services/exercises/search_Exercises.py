from app.services import run_query

def search_exercises(name, filters):

    query = """
        SELECT 
            exercise_id, 
            exercise_name, 
            equipment, 
            video_url 
        FROM exercise 
        WHERE 1=1
    """
    params = {}

    if name:
        query += " AND exercise_name LIKE :name"
        params["name"] = f"%{name}%"

    if filters:
        for equip in filters:
            # We create a unique parameter key for each equipment item in the list
            query += f" AND equipment LIKE :equip_{equip}"
            params[f"equip_{equip}"] = f"%{equip}%"

    query += " ORDER BY exercise_name ASC"

    return run_query(query, params=params, fetch=True, commit=False)