# app/services/client/account_service.py
from datetime import date

from app.services import run_query 
from flask import jsonify, request

def delete_account_service(user_id):
    query = "DELETE FROM users_immutables WHERE user_id = :id"
    params = {"id": user_id}
    
    # We set commit=True because we are changing the database 
    return run_query(query, params=params, fetch=False, commit=True) 

def submit_mental_survey_service(user_id, score, notes, today):
    query = """
        INSERT INTO mental_wellness_survey (user_id, survey_date, mood_score, notes) 
        VALUES (:user_id, :s_date, :score, :notes)
    """
    params = {
        "user_id": user_id, 
        "s_date": today, 
        "score": score, 
        "notes": notes
    }
    
    return run_query(query, params=params, fetch=False, commit=True)