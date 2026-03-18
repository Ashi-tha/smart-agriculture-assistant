"""SQLite database helpers for prediction history."""
import sqlite3
import json
from datetime import datetime

DB_PATH = "agri.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            type        TEXT NOT NULL,
            inputs      TEXT NOT NULL,
            result      TEXT NOT NULL,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_prediction(pred_type: str, inputs: dict, result: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO predictions (type, inputs, result, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        pred_type,
        json.dumps(inputs),
        json.dumps(result),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


def get_history(limit=50):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, type, inputs, result, created_at
        FROM predictions
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "type": r["type"],
            "inputs": json.loads(r["inputs"]),
            "result": json.loads(r["result"]),
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def delete_prediction(pred_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM predictions WHERE id = ?", (pred_id,))
    conn.commit()
    conn.close()
