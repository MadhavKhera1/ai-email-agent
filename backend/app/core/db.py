import _sqlite3
DB_NAME = "emails.db"

def get_connection():
    return _sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    create table if not exists processed_emails(
       id text primary key            
    )
    """)

    conn.commit()
    conn.close()
