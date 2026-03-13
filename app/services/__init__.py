from sqlalchemy import text
from app import db


def run_query(query, params=None, fetch=True, commit=False):
    """
    Helper to run SQL queries.

    input:
        query (str): SQL query string
        params (dict): parameters for parameterized queries
        fetch (bool): whether to return results (for SELECT)
        commit (bool): whether to commit transaction (for INSERT/UPDATE/DELETE)

    output:
        list[dict] | None
    """

    result = db.session.execute(text(query), params or {})

    if commit:
        db.session.commit()

    if fetch:
        return [dict(row) for row in result.mappings().all()]

    return None
