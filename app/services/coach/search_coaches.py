from app.services import run_query


def search_coaches(name, filters, is_certified=False, max_price=None, min_rating=None, sort_by=False):
    #  Base Query..if no filters are applied this will return all coaches. 
    #  We use DISTINCT to avoid getting the same coach multiple times if they several certs.
    query = """
        SELECT 
            u.user_id, u.first_name, c.price, c.coach_description, 
            ROUND(AVG(cr.rating), 1) as avg_rating,
            COUNT(cr.review_id) as review_count
        FROM users_immutables u 
        JOIN coach c ON u.user_id = c.coach_id
        LEFT JOIN coach_review cr ON c.coach_id = cr.coach_id
    """
    
    if is_certified:
        query += " JOIN certifications cf ON cf.coach_id = c.coach_id"

    query += " WHERE 1=1"
    params = {}

    if name:
        query += " AND u.first_name LIKE :name"
        params["name"] = f"%{name}%"

    if max_price is not None:
        query += " AND c.price <= :max_price"
        params["max_price"] = max_price

    if filters:
        for tag in filters:
            query += f" AND c.coach_description LIKE :tag_{tag}"
            params[f"tag_{tag}"] = f"%{tag}%"
    
    # Grouping is required when using AVG or COUNT
    query += " GROUP BY u.user_id, u.first_name, c.price, c.coach_description"

    if min_rating is not None:
        query += " HAVING AVG(cr.rating) >= :min_rating"
        params["min_rating"] = min_rating

    # Sorting (The Ordering)
    if sort_by == "rating":
        query += " ORDER BY avg_rating DESC, review_count DESC"
    else:
        query += " ORDER BY c.price ASC" # Default to cheapest first

    return run_query(query, params=params, fetch=True, commit=False)