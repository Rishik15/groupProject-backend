from app.services import run_query

def add_coach_certification(coach_id, incoming_json):

    cert_name = incoming_json.get("cert_name")
    provider = incoming_json.get("provider_name")
    description = incoming_json.get("description")
    issued_date = incoming_json.get("issued_date")
    expires_date = incoming_json.get("expires_date")

    query = """
        INSERT INTO certifications (coach_id, cert_name, provider_name, description, issued_date, expired_date)
        VALUES (:id, :name, :org, :desc, :issued_date, :expires_date)
    """
    
    params = {
        "id": coach_id,
        "name": cert_name,
        "org": provider,
        "desc": description,
        "issued_date": issued_date,
        "expires_date": expires_date
    }

    try:
        run_query(query, params=params, fetch=False, commit=True)
        return {"message": "Certificate added successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 500