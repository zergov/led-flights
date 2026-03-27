import json
import sqlite3
import re

from aircraft import Aircraft


def load_aircraft_data_by_icao(conn: sqlite3.Connection, icao: str) -> dict:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aircrafts WHERE icao = ?", (icao.upper(),))

    aircraft = {}
    for row in cursor.fetchall():
        icao, registration, aircraft_type, name = row
        aircraft["icao"] = icao
        aircraft["registration"] = registration
        aircraft["type"] = aircraft_type
        aircraft["name"] = name

    return aircraft


def load_operator_data_by_callsign(conn: sqlite3.Connection, callsign: str) -> dict:
    callsign = callsign.upper()
    operator_prefix = re.split(r'(\d+)', callsign, maxsplit=1)[0]

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operators WHERE icao_id = ?", (operator_prefix,))

    operator = {}
    row = cursor.fetchone()
    if row:
        prefix, name, country = row
        operator["prefix"] = prefix
        operator["name"] = name
        operator["country"] = country

    return operator


def load_dump1090_aircraft_data(filepath: str) -> list[Aircraft]:
    aircrafts = []

    with open(filepath) as f:
        data = json.loads(f.read())

        for aircraft_data in data["aircraft"]:
            aircrafts.append(Aircraft(aircraft_data))

    return aircrafts


db_conn = sqlite3.connect("db.sqlite")
dump1090_aircrafts = load_dump1090_aircraft_data("./dump1090_aicraft.json")

for aircraft in dump1090_aircrafts:
    if not aircraft.has_aircraft_data():
        aircraft_data = load_aircraft_data_by_icao(db_conn, aircraft.icao_hex())
        aircraft.update_aircraft_data(aircraft_data)

    if aircraft.flight() and not aircraft.has_operator_data():
        operator_data = load_operator_data_by_callsign(db_conn, aircraft.flight())
        aircraft.update_operator_data(operator_data)

    print("------------------------------")
    print("ICAO: ", aircraft.icao_hex())
    print("SQUAWK: ", aircraft.squawk())
    print("NAME: ", aircraft.name())
    print("TYPE: ", aircraft.aircraft_type())
    print("FLIGHT: ", aircraft.flight())
    print("ALTITUDE: ", aircraft.altitude())
    print("REGISTRATION: ", aircraft.registration())
    print("OPERATOR PREFIX: ", aircraft.operator_prefix())
    print("OPERATOR NAME: ", aircraft.operator_name())
    print("OPERATOR COUNTRY: ", aircraft.operator_country())
