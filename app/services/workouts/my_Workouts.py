from app.services import run_query

def get_user_workouts(user_id: int):
    try:
        # We use a UNION to get both authored and assigned plans
        query = """
            SELECT 
                wp.plan_id, 
                wp.plan_name, 
                wpt.description, 
                'authored' as source,
                COUNT(pe.exercise_id) as total_exercises
            FROM workout_plan wp
            JOIN workout_plan_template wpt ON wp.plan_id = wpt.plan_id
            LEFT JOIN workout_day wd ON wp.plan_id = wd.plan_id
            LEFT JOIN plan_exercise pe ON wd.day_id = pe.day_id
            WHERE wpt.author_user_id = :uid
            GROUP BY wp.plan_id, wp.plan_name, wpt.description

            UNION

            SELECT 
                wp.plan_id, 
                wp.plan_name, 
                wpt.description, 
                'assigned' as source,
                COUNT(pe.exercise_id) as total_exercises
            FROM workout_plan wp
            JOIN coach_assignment_log cal ON wp.plan_id = cal.workout_plan_id
            JOIN workout_plan_template wpt ON wp.plan_id = wpt.plan_id
            LEFT JOIN workout_day wd ON wp.plan_id = wd.plan_id
            LEFT JOIN plan_exercise pe ON wd.day_id = pe.day_id
            WHERE cal.user_id = :uid
            GROUP BY wp.plan_id, wp.plan_name, wpt.description
            
            ORDER BY plan_name ASC;
        """
        
        return run_query(query, {"uid": user_id}, fetch=True, commit=False)

    except Exception as e:
        raise Exception(f"Failed to fetch user workouts: {str(e)}")