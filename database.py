"""SQLite persistence for users and user-owned prompt history."""
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.db")

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_input TEXT NOT NULL,
        style TEXT NOT NULL,
        style_label TEXT NOT NULL,
        aspect_ratio TEXT DEFAULT 'Square (1:1)',
        generated_prompt TEXT NOT NULL,
        negative_prompt TEXT,
        image_url TEXT,
        is_favorite INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    cols = {r['name'] for r in c.execute("PRAGMA table_info(prompts)").fetchall()}
    if 'user_id' not in cols:
        c.execute("ALTER TABLE prompts ADD COLUMN user_id INTEGER")
    if 'image_url' not in cols:
        c.execute("ALTER TABLE prompts ADD COLUMN image_url TEXT")
    conn.commit()
    conn.close()

def create_user(name, email, password):
    conn = get_connection()
    try:
        cur = conn.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                           (name.strip(), email.strip().lower(), generate_password_hash(password)))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def verify_password(user, password):
    return bool(user and check_password_hash(user['password_hash'], password))

def save_prompt(user_id, user_input, style, style_label, aspect_ratio, generated_prompt, negative_prompt, image_url=None):
    conn = get_connection()
    try:
        cur = conn.execute("""INSERT INTO prompts
        (user_id,user_input,style,style_label,aspect_ratio,generated_prompt,negative_prompt,image_url)
        VALUES(?,?,?,?,?,?,?,?)""",
        (user_id,user_input,style,style_label,aspect_ratio,generated_prompt,negative_prompt,image_url))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def _query(sql, args=()):
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]
    finally:
        conn.close()

def get_all_prompts(user_id, limit=50, offset=0):
    return _query("SELECT * FROM prompts WHERE user_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?", (user_id,limit,offset))
def get_prompts_by_style(user_id, style, limit=50):
    return _query("SELECT * FROM prompts WHERE user_id=? AND style=? ORDER BY created_at DESC LIMIT ?", (user_id,style,limit))
def get_favorite_prompts(user_id, limit=50):
    return _query("SELECT * FROM prompts WHERE user_id=? AND is_favorite=1 ORDER BY created_at DESC LIMIT ?", (user_id,limit))
def search_prompts(user_id, query, limit=50):
    return _query("SELECT * FROM prompts WHERE user_id=? AND user_input LIKE ? ORDER BY created_at DESC LIMIT ?", (user_id,f"%{query}%",limit))
def toggle_favorite(user_id, prompt_id):
    conn=get_connection()
    try:
        conn.execute("UPDATE prompts SET is_favorite=CASE WHEN is_favorite=1 THEN 0 ELSE 1 END WHERE id=? AND user_id=?", (prompt_id,user_id))
        conn.commit()
        row=conn.execute("SELECT is_favorite FROM prompts WHERE id=? AND user_id=?", (prompt_id,user_id)).fetchone()
        return dict(row) if row else None
    finally: conn.close()
def delete_prompt(user_id, prompt_id):
    conn=get_connection()
    try:
        cur=conn.execute("DELETE FROM prompts WHERE id=? AND user_id=?", (prompt_id,user_id))
        conn.commit()
        return cur.rowcount > 0
    finally: conn.close()
def get_stats(user_id):
    conn=get_connection()
    try:
        total=conn.execute("SELECT COUNT(*) n FROM prompts WHERE user_id=?", (user_id,)).fetchone()['n']
        fav=conn.execute("SELECT COUNT(*) n FROM prompts WHERE user_id=? AND is_favorite=1", (user_id,)).fetchone()['n']
        styles=[dict(r) for r in conn.execute("SELECT style_label,COUNT(*) count FROM prompts WHERE user_id=? GROUP BY style_label ORDER BY count DESC", (user_id,)).fetchall()]
        return {"total_prompts":total,"favorites":fav,"style_breakdown":styles}
    finally: conn.close()

def owns_image(user_id, image_url):
    conn = get_connection()
    try:
        row = conn.execute("SELECT 1 FROM prompts WHERE user_id=? AND image_url=? LIMIT 1",
                           (user_id, image_url)).fetchone()
        return row is not None
    finally:
        conn.close()
