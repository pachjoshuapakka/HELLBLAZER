# generate_qr.py
import os
import csv
import uuid
import sqlite3
import qrcode
from datetime import datetime

DB_PATH = "data/tickets.db"
OUT_DIR = "qr_codes"
NUM = 180  # cambia si quieres más o menos

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Inicializa DB si no existe
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    created_at TEXT,
    scanned INTEGER DEFAULT 0,
    scanned_at TEXT
)
""")
conn.commit()

generated = []
for i in range(NUM):
    code = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    # Inserta en DB
    c.execute("INSERT INTO tickets (code, created_at, scanned) VALUES (?, ?, 0)", (code, created_at))
    conn.commit()
    # Contenido del QR: el código UUID
    qr_data = code
    img = qrcode.make(qr_data)
    filename = f"{OUT_DIR}/{i+1:03d}_{code}.png"
    img.save(filename)
    generated.append((i+1, code, filename, created_at))
    print(f"Generado: {filename}")

# Export a CSV con los códigos
csv_path = os.path.join(OUT_DIR, "tickets_list.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["index", "code", "file", "created_at"])
    for row in generated:
        writer.writerow(row)

print(f"\nGenerados {NUM} QR en {OUT_DIR} y listado en {csv_path}")
conn.close()
