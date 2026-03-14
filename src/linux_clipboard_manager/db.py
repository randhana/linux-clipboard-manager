import sqlite3
import os

DB_PATH = os.path.expanduser('~/.local/share/clipboard_history.db')

def get_connection():
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clipboard_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT UNIQUE NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_item(content: str):
    if not content or not content.strip():
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    # Insert or update timestamp if it already exists to bring it to top
    cursor.execute('''
        INSERT INTO clipboard_items (content, timestamp)
        VALUES (?, CURRENT_TIMESTAMP)
        ON CONFLICT(content) DO UPDATE SET timestamp = CURRENT_TIMESTAMP
    ''', (content,))
    conn.commit()
    
    # Keep only the latest 100 items to prevent db from growing indefinitely
    cursor.execute('''
        DELETE FROM clipboard_items 
        WHERE id NOT IN (
            SELECT id FROM clipboard_items 
            ORDER BY timestamp DESC 
            LIMIT 100
        )
    ''')
    conn.commit()
    conn.close()

def get_items(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, content FROM clipboard_items
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    items = cursor.fetchall()
    conn.close()
    return items

def delete_item(item_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clipboard_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
