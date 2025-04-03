import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("agent_memory.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            topic TEXT,
            num_articles INTEGER,
            pdf_used INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_memory(topic, num_articles, pdf_used_count):
    conn = sqlite3.connect("agent_memory.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO memory (timestamp, topic, num_articles, pdf_used)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().isoformat(), topic, num_articles, pdf_used_count))
    conn.commit()
    conn.close()

def get_memory():
    conn = sqlite3.connect("agent_memory.db")
    c = conn.cursor()
    c.execute("SELECT * FROM memory ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows
