import mysql.connector as connecter
from app.config import Config as c
def test():
    sql = """
        SHOW TABLES; 
    """
    with connecter.connect(**c.DB_CONFIG) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(sql)
            return cursor.fetchall()