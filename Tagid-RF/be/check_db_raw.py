import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


def check_db():
    conn_str = "postgresql://postgres:postgres@127.0.0.1:5435/shifty"
    print(f"Connecting to: {conn_str}")
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check Business table
        print("\n--- Business Table Columns ---")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'Business'
            ORDER BY ordinal_position;
        """)
        for row in cur.fetchall():
            print(row)

        # Check User table
        print("\n--- User Table Columns ---")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'User'
            ORDER BY ordinal_position;
        """)
        for row in cur.fetchall():
            print(row)

        cur.close()
        conn.close()
    except Exception as e:
        print(f"FAILED: {e}")


if __name__ == "__main__":
    check_db()
