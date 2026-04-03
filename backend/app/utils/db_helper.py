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
