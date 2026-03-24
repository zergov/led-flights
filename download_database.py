import requests
import json
import tempfile
import zipfile
import os
import sqlite3


def store_aircrafts(conn: sqlite3.Connection, file: str):
    print("inserting aircrafts...")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aircrafts (
        icao TEXT PRIMARY KEY,
        registration TEXT,
        type TEXT,
        name TEXT
    );
    """)

    with open(file, "r") as f:
        aircrafts = json.load(f)

        sql = "INSERT INTO aircrafts (icao, registration, type, name) VALUES (?, ?, ?, ?);"
        for icao, aircraft in aircrafts.items():
            registration = aircraft.get("r", "")
            aircraft_type = aircraft.get("t", "")
            name = aircraft.get("d", "")

            cursor.execute(sql, (icao, registration, aircraft_type, name))

    conn.commit()


def store_operators(conn: sqlite3.Connection, file: str):
    print("inserting operators...")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS operators (
        icao_id TEXT PRIMARY KEY,
        name TEXT,
        country TEXT
    );
    """)

    with open(file, "r") as f:
        operators = json.load(f)

        sql = "INSERT INTO operators (icao_id, name, country) VALUES (?, ?, ?);"
        for icao, operator in operators.items():
            name = operator.get("n", "")
            country = operator.get("c", "")

            cursor.execute(sql, (icao, name, country))

    conn.commit()


print("downloading mictronics database...")
url = "https://www.mictronics.de/aircraft-database/indexedDB_old.php"
response = requests.get(url, stream=True)

with tempfile.TemporaryDirectory() as tmp_dir:
    tmp = tempfile.TemporaryFile(dir=tmp_dir)

    for chunk in response.iter_content(1024 * 8):
        if chunk:
            tmp.write(chunk)

    print("extracting mictronics database...")
    zipfile.ZipFile(tmp, "r").extractall(tmp_dir)

    os.remove("db.sqlite")
    conn = sqlite3.connect("db.sqlite")

    store_aircrafts(conn, os.path.join(tmp_dir, "aircrafts.json"))
    store_operators(conn, os.path.join(tmp_dir, "operators.json"))
