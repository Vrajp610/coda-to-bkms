import psycopg2
from psycopg2.extras import DictCursor

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="bkms_values",
        port="5432",
        user="vrajpatel"
    )

def get_config_value(key):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT value FROM config WHERE key = %s", (key,))
            result = cur.fetchone()
            return result['value'] if result else None
    finally:
        conn.close()