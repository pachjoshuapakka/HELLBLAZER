from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_PATH = os.path.join("data", "tickets.db")

# Función para conectar a SQLite
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Crear tabla si no existe
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            scanned INTEGER DEFAULT 0,
            scanned_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# Página de inicio
@app.route("/")
def index():
    return render_template("index.html")

# Página del escáner
@app.route("/scan-page")
def scan_page():
    return render_template("scan.html")

# Página de lista
@app.route("/list")
def list_tickets():
    conn = get_db_connection()
    tickets = conn.execute("SELECT * FROM tickets").fetchall()
    conn.close()
    return render_template("list.html", tickets=tickets)

# Endpoint de escaneo
@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()
    code = data.get("code")

    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM tickets WHERE code = ?", (code,)).fetchone()

    if not ticket:
        conn.close()
        return jsonify({"ok": False, "error": "Código no encontrado"}), 404

    if ticket["scanned"]:
        conn.close()
        return jsonify({"ok": False, "error": "Ya escaneado"}), 409

    scanned_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE tickets SET scanned = 1, scanned_at = ? WHERE code = ?", (scanned_at, code))
    conn.commit()
    conn.close()

    return jsonify({"ok": True})

# 🔥 Endpoint de estadísticas (para list.html en tiempo real)
@app.route("/stats")
def stats():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM tickets ORDER BY id").fetchall()
    conn.close()

    tickets = []
    scanned = 0
    for r in rows:
        scanned += 1 if r["scanned"] else 0
        tickets.append({
            "id": r["id"],
            "code": r["code"],
            "created_at": r["created_at"],
            "scanned": bool(r["scanned"]),
            "scanned_at": r["scanned_at"]
        })

    return jsonify({
        "total": len(rows),
        "scanned": scanned,
        "tickets": tickets
    })

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)







