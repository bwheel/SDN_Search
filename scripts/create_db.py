import gzip
import os
import shutil
import requests
import sqlite3
import csv
from pathlib import Path

CSV_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"
DB_FILE = Path("docs/sdn.db")
CSV_FILE = Path("sdn.csv")


def build_db():
    if not CSV_FILE.exists():
        r = requests.get(CSV_URL)
        r.raise_for_status()
        text = r.text.replace("\x1a", "").strip().splitlines()
    else:
        text = CSV_FILE.read_text().splitlines()

    reader = csv.reader(text)
    rows = []
    for row in reader:
        # Replace "-0-" with None (for DB) and "" (for cleaned CSV)
        cleaned_row = [None if x.strip() == "-0-" else x.strip() for x in row]
        rows.append(cleaned_row)

    # Write cleaned CSV back to disk
    with open("sdn.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(["" if x is None else x for x in row])

    DB_FILE.parent.mkdir(exist_ok=True)  # ensure 'data/' directory exists
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS sdn;
        DROP TABLE IF EXISTS sdn_fts;

        CREATE TABLE sdn (
            ent_num     INTEGER PRIMARY KEY,
            sdn_name    TEXT,
            sdn_type    TEXT,
            program     TEXT,
            title       TEXT,
            call_sign   TEXT,
            vess_type   TEXT,
            tonnage     TEXT,
            grt         TEXT,
            vess_flag   TEXT,
            vess_owner  TEXT,
            remarks     TEXT
        );

        CREATE VIRTUAL TABLE sdn_fts USING fts5(
            sdn_name,
            sdn_type,
            program,
            title,
            call_sign,
            vess_type,
            tonnage,
            grt,
            vess_flag,
            vess_owner,
            remarks,
            content='sdn',
            content_rowid='ent_num'
        );
    """)
    for row in rows:
        if len(row) != 12:
            print("Skipping malformed row:", row)
            continue
        cur.execute(
            """
            INSERT INTO sdn (
                ent_num, sdn_name, sdn_type, program, title,
                call_sign, vess_type, tonnage, grt,
                vess_flag, vess_owner, remarks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            row,
        )

    # Build the FTS5 index on only the selected columns
    cur.execute("INSERT INTO sdn_fts(sdn_fts) VALUES('rebuild');")
    conn.commit()
    conn.execute("VACUUM;")
    conn.close()

    with open(DB_FILE, "rb") as f_in, gzip.open(f"{DB_FILE}.gz", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(DB_FILE.absolute())


if __name__ == "__main__":
    build_db()
