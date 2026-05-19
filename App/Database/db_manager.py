import sqlite3
import os
from datetime import datetime

class DBManager:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "feedback.db")
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        # Create table if not exists
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback(
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            text TEXT,
            audio TEXT
        )
        """)
        self.conn.commit()

    def insert(self, text, audio):
        self.conn.execute(
            "INSERT INTO feedback (timestamp, text, audio) VALUES (?,?,?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text, audio)
        )
        self.conn.commit()

    def fetch_all(self):
        return self.conn.execute("SELECT * FROM feedback ORDER BY id DESC").fetchall()

    def delete(self, record_id):
        row = self.conn.execute("SELECT audio FROM feedback WHERE id=?", (record_id,)).fetchone()
        if row and row[0] and os.path.exists(row[0]):
            try:
                os.remove(row[0])
            except OSError:
                pass

        self.conn.execute("DELETE FROM feedback WHERE id=?", (record_id,))
        self.conn.commit()

    def delete_all(self):
        rows = self.fetch_all()
        for r in rows:
            if r[3] and os.path.exists(r[3]):
                try:
                    os.remove(r[3])
                except OSError:
                    pass

        self.conn.execute("DELETE FROM feedback")
        self.conn.commit()