from app.services import run_query
from app.services.coach.getCoachInfo import getCoachInformation
from app.routes.coach.coachReview import getReviews


def get_coach_profile(coach_id):
    data = getCoachInformation(coach_id) 
    
    if not data:
        return None

    result = data[0]

    reviews_data = getReviews(coach_id)
    result["avg_rating"] = reviews_data.get("coach_avg_rating")
    result["reviews"] = reviews_data.get("reviews")
    
    clients = run_query(
        """
        SELECT COUNT(*) AS active_clients
        FROM user_coach_contract
        WHERE coach_id = :cid AND active = 1
        """,
        {"cid": coach_id},
        commit=False,
        fetch=True
    )

    if clients:
        result["active_clients"] = clients[0]["active_clients"]
    else:
        result["active_clients"] = 0


    certs = run_query(
        """
    SELECT cert_id, cert_name, provider_name, description, issued_date, expires_date
    FROM certifications
    WHERE coach_id = :cid
    ORDER BY issued_date DESC
        """,
        {"cid": coach_id},
        commit=False,
        fetch=True
    )
    
    formatted_certs = []
    for cert in certs:
        formatted_certs.append({
            "id": cert["cert_id"],
            "name": cert["cert_name"],
            "provider": cert["provider_name"],
            "description": cert["description"],
            "issued_date": str(cert["issued_date"]) if cert["issued_date"] else None,
            "expires_date": str(cert["expires_date"]) if cert["expires_date"] else None
        })
    
    result["certifications"] = formatted_certs

    availability = run_query(
        """
        SELECT day_of_week, start_time, end_time
        FROM coach_availability
        WHERE coach_id = :cid AND active = 1
        ORDER BY FIELD(day_of_week, 'Mon','Tue','Wed','Thu','Fri','Sat','Sun')
        """,
        {"cid": coach_id},
        commit=False,
        fetch=True
    )
    formatted_availability = []
    for slot in availability :
        formatted_availability.append({
            "day_of_week": slot["day_of_week"],
            "start_time": str(slot["start_time"]), 
            "end_time": str(slot["end_time"])      
        })

    result["availability"] = formatted_availability
    
    return result