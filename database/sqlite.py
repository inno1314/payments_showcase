import sqlite3

with sqlite3.connect("tgbot_users.sqlite3") as db:
    cursor = db.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        name TEXT,
        balance INTEGER DEFAULT 0,
        label TEXT DEFAULT None
    )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS payments (
        payment_id TEXT PRIMARY KEY,
        user_id INTEGER,
        amount INTEGER,
        status TEXT DEFAULT created,
        service TEXT,
        date TEXT
    )"""
    )
