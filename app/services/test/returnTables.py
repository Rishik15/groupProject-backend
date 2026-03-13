from sqlalchemy import text
from app import db


def tservice():
    sql = text("SHOW TABLES")

    result = db.session.execute(sql)

    return [dict(row._mapping) for row in result]
