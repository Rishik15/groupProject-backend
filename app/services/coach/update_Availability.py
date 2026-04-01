from app.services import run_query

def update_coach_availability(u_id, num_days, days, starts, ends, recurring, active):
    """
    Updates coach availability by deleting old records and inserting new ones one by one.
    """
    try:

        #   Instead of checking if 'a certain day' was recurring before, we just DELETE and insert a new record which automatically handles:
        #   Deleting days the coach is no longer available.
        #   Changing a 'Recurring' day to 'One-Time' (and vice-versa) and changes in start / end time
        
        delete_sql = "DELETE FROM coach_availability WHERE coach_id = :u_id"
        run_query(delete_sql, {"u_id": u_id}, fetch=False, commit=True)

        for i in range(num_days):
            query = """
                INSERT INTO coach_availability 
                (coach_id, day_of_week, start_time, end_time, recurring, active)
                VALUES (:u_id, :day, :start, :end, :rec, :act)
            """
            params = {
                "u_id": u_id,
                "day": days[i],
                "start": starts[i],
                "end": ends[i],
                "rec": recurring[i],
                "act": active[i]
            }
            
            run_query(query, params, fetch=False, commit=True)
                
    except Exception as e:
        raise e