"""
SQLite Database Module
Handles all database operations for storing and retrieving generated prompts.
"""

import sqlite3
import os
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.db")


def get_connection():
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input      TEXT NOT NULL,
            style           TEXT NOT NULL,
            style_label     TEXT NOT NULL,
            aspect_ratio    TEXT DEFAULT 'Square (1:1)',
            generated_prompt TEXT NOT NULL,
            negative_prompt TEXT,
            image_url       TEXT,
            is_favorite     INTEGER DEFAULT 0,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add image_url column if upgrading from old schema
    try:
        cursor.execute("ALTER TABLE prompts ADD COLUMN image_url TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at {DATABASE_PATH}")


def save_prompt(user_input, style, style_label, aspect_ratio,
                generated_prompt, negative_prompt, image_url=None):
    """Save a generated prompt to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO prompts (user_input, style, style_label, aspect_ratio,
                             generated_prompt, negative_prompt, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_input, style, style_label, aspect_ratio,
          generated_prompt, negative_prompt, image_url))

    prompt_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prompt_id


def get_all_prompts(limit=50, offset=0):
    """Retrieve all prompts ordered by newest first."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM prompts
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_prompts_by_style(style, limit=50):
    """Retrieve prompts filtered by style."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM prompts
        WHERE style = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (style, limit))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_favorite_prompts(limit=50):
    """Retrieve favorite prompts."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM prompts
        WHERE is_favorite = 1
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def toggle_favorite(prompt_id):
    """Toggle the favorite status of a prompt."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE prompts
        SET is_favorite = CASE WHEN is_favorite = 1 THEN 0 ELSE 1 END
        WHERE id = ?
    """, (prompt_id,))

    conn.commit()

    # Return updated status
    cursor.execute("SELECT is_favorite FROM prompts WHERE id = ?", (prompt_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def delete_prompt(prompt_id):
    """Delete a prompt by ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def search_prompts(query, limit=50):
    """Search prompts by user input text."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM prompts
        WHERE user_input LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (f"%{query}%", limit))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_stats():
    """Get statistics about generated prompts."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM prompts")
    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT style_label, COUNT(*) as count
        FROM prompts
        GROUP BY style_label
        ORDER BY count DESC
    """)
    style_counts = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) as fav_count FROM prompts WHERE is_favorite = 1")
    favorites = cursor.fetchone()["fav_count"]

    conn.close()

    return {
        "total_prompts": total,
        "favorites": favorites,
        "style_breakdown": style_counts
    }
