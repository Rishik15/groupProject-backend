from app.services import run_query 

def check_survey_status_service(user_id, today):
    query = """
        SELECT survey_id FROM mental_wellness_survey 
        WHERE user_id = :user_id AND survey_date = :s_date
        LIMIT 1
    """
    params = {"user_id": user_id, "s_date": today}
    result = run_query(query, params=params, fetch=True, commit=False)
    
    # Returns True if a survey exists, False otherwise
    return len(result) > 0