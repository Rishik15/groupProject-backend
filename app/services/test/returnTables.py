from app.services import run_query


def tservice():
    query = "SHOW TABLES"

    result = run_query(query, params={}, fetch=True, commit=False)

    return result
