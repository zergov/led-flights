import json
import re
import sqlite3
import sys
import time

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


def load_dump1090_aircraft_data(filepath: str) -> list[dict]:
    aircrafts = []

    with open(filepath) as f:
        data = json.loads(f.read())

        for aircraft_data in data["aircraft"]:
            aircrafts.append(aircraft_data)

    return aircrafts


dump1090_file = "./dump1090_aicraft.json"
if len(sys.argv) > 1:
    dump1090_file = sys.argv[1]

db_conn = sqlite3.connect("db.sqlite")

aircrafts_nearby: dict[str, Aircraft] = {}
while True:
    time.sleep(5)

    dump1090_aircrafts = load_dump1090_aircraft_data(dump1090_file)

    for aircraft_data in dump1090_aircrafts:
        icao = aircraft_data["hex"]

        if not icao:
            pass

        icao = icao.upper()
        aircraft = aircrafts_nearby.get(icao, Aircraft(aircraft_data))
        aircraft.update_dump1090_data(aircraft_data)
        aircrafts_nearby[icao] = aircraft

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
