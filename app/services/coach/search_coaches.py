from app.services import run_query


def search_coaches(name, filters, is_certified=False, max_price=None, min_rating=None, sort_by=False):
    #  Base Query..if no filters are applied this will return all coaches. 
    #  We use DISTINCT to avoid getting the same coach multiple times if they have several certs.
    # print("received filters:", filters)
    query = """
        SELECT 
            u.user_id as coach_id, u.first_name, u.last_name, c.price, c.coach_description, 
            ROUND(AVG(cr.rating), 1) as avg_rating,
            COUNT(cr.review_id) as review_count,
            GROUP_CONCAT(DISTINCT cf.cert_name SEPARATOR ', ') as certifications
        FROM users_immutables u 
        JOIN coach c ON u.user_id = c.coach_id
        LEFT JOIN coach_review cr ON c.coach_id = cr.coach_id
        LEFT JOIN certifications cf ON c.coach_id = cf.coach_id
    """

    query += " WHERE u.user_id != 1"
    params = {}

    if is_certified:
        query += " AND cf.cert_name IS NOT NULL"

    if name:
        query += " AND CONCAT(u.first_name, ' ', u.last_name) LIKE :full_name"
        params["full_name"] = f"%{name}%"

    if max_price is not None:
        query += " AND c.price <= :max_price"
        params["max_price"] = max_price

    if filters:
        for tag in filters:
            query += f" AND LOWER(c.coach_description) LIKE LOWER(:tag_{tag})"
            params[f"tag_{tag}"] = f"%{tag}%"
    
    query += " GROUP BY u.user_id, u.first_name, u.last_name, c.price, c.coach_description"

    if min_rating is not None and min_rating > 0:
        query += " HAVING AVG(cr.rating) >= :min_rating"
        params["min_rating"] = min_rating

    # Sorting
    if sort_by == "rating":
        query += " ORDER BY avg_rating DESC, review_count DESC"
    else:
        query += " ORDER BY c.price ASC"
    print(query, params)
    return run_query(query, params=params, fetch=True, commit=False)