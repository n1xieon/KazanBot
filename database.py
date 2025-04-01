import sqlite3
from datetime import datetime

DB_FILE = "users.db"

# === Инициализация БД ===
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                deadline TEXT,
                state TEXT
            )
        ''')
        conn.commit()

# === Сохранить пользователя ===
def save_user(user_id: int, deadline: datetime, state: str):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO users (user_id, deadline, state)
            VALUES (?, ?, ?)
        ''', (user_id, deadline.isoformat(), state))
        conn.commit()

# === Загрузить пользователя ===
def load_user(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT deadline, state FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if row:
            deadline = datetime.fromisoformat(row[0])
            state = row[1]
            return deadline, state
        return None

# === Удалить пользователя ===
def delete_user(user_id: int):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
