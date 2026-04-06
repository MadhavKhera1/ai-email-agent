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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT,
        subject TEXT,
        type TEXT,
        confidence REAL,
        action TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
