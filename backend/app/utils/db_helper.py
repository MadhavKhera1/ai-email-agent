from app.core.db import get_connection

def is_email_processed(email_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "select id from processed_emails where id=?",
        (email_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None

def mark_email_processed(email_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "insert into processed_emails (id) values (?)",
        (email_id,)
    )

    conn.commit()
    conn.close()

def save_log(email_id, subject, type_, confidence, action):
    from app.core.db import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs (email_id, subject, type, confidence, action)
        VALUES (?, ?, ?, ?, ?)
    """, (email_id, subject, type_, confidence, action))

    conn.commit()
    conn.close()
