from app.services import run_query

'''
For context this is what each table's purpose is in creating a workout plan assignment:
workout_plan — what is this plan called
workout_plan_template — who made it, is it public, what category/level/duration is it
plan_exercise — what exercises are in it and in what order
exercise — what are those exercises actually called and what equipment do they need
'''


def get_predefined_plans(category=None, days_per_week=None, duration=None, level=None):
    # fetch all public system-authored plans with their exercise count
    # author_user_id = 1 means system, is_public = 1 means visible in browse screen
    query = """
        SELECT
            wp.plan_id,
            wp.plan_name,
            wpt.description,
            COUNT(pe.exercise_id) as exercise_count
        FROM workout_plan wp
        JOIN workout_plan_template wpt ON wp.plan_id = wpt.plan_id
        JOIN plan_exercise pe ON wp.plan_id = pe.plan_id
        WHERE wpt.author_user_id = 1
        AND wpt.is_public = 1
    """

    params = {}

    # The description in the workout plan template is formatted specifically like shown : {Category} | {X} days/week | {Duration} min | {Level}
    # each filter uses LIKE against the description 
    if category:
        query += " AND wpt.description LIKE :category"
        params["category"] = f"%{category}%"
    if days_per_week:
        query += " AND wpt.description LIKE :days_per_week"
        params["days_per_week"] = f"%{days_per_week} days/week%"
    if duration:
        query += " AND wpt.description LIKE :duration"
        params["duration"] = f"%{duration} min%"
    if level:
        query += " AND wpt.description LIKE :level"
        params["level"] = f"%{level}%"

    query += " GROUP BY wp.plan_id, wp.plan_name, wpt.description"
    query += " ORDER BY wp.plan_name ASC"

    return run_query(query, params=params, fetch=True, commit=False)
