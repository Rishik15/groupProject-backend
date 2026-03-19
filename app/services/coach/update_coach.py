from app.services import run_query


def update_coach_profile(coach_id, update_json):
    query = "UPDATE coach SET "
    params = {"id": coach_id}
    
    has_fields = False

    if "price" in update_json:
        query += "price = :price"
        params["price"] = update_json["price"]
        has_fields = True

    if "coach_description" in update_json:
        if has_fields:
            query += ", "
        
        query += "coach_description = :desc"
        params["desc"] = update_json["coach_description"]
        has_fields = True

    if not has_fields:
        return {"message": "No valid fields provided"}, 400

    query += " WHERE coach_id = :id"

    try:
        run_query(query, params=params, fetch=False, commit=True)
        return {"message": "Profile Updated successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500