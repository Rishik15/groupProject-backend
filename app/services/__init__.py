from sqlalchemy import text
from app import db


def run_query(query, params=None, fetch=True, commit=False, return_lastrowid=False):
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

    try:
        result = db.session.execute(text(query), params or {})

        lastrowid = result.lastrowid if return_lastrowid else None

        if commit:
            db.session.commit()

        if return_lastrowid:
            return lastrowid

        if fetch:
            return [dict(row) for row in result.mappings()]

        return None

    except Exception as e:
        db.session.rollback()
        raise e
