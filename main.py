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


with open("./dump1090_aicraft.json") as f:
    data = json.loads(f.read())
    db_conn = sqlite3.connect("db.sqlite")

    for aircraft_data in data["aircraft"]:
        icao = aircraft_data["hex"]

        if not icao:
            pass

        db_data = load_aircraft_data_by_icao(db_conn, icao)
        aircraft = Aircraft(aircraft_data, db_data)

        print("------------------------------")
        print("ICAO: ", aircraft.icao_hex())
        print("SQUAWK: ", aircraft.squawk())
        print("NAME: ", aircraft.name())
        print("TYPE: ", aircraft.aircraft_type())
        print("FLIGHT: ", aircraft.flight())
        print("ALTITUDE: ", aircraft.altitude())
        print("REGISTRATION: ", aircraft.registration())

        if aircraft.flight():
            operator = load_operator_data_by_callsign(db_conn, aircraft.flight())

            print("OPERATOR PREFIX: ", operator.get("prefix", None))
            print("OPERATOR NAME: ", operator.get("name", None))
            print("OPERATOR COUNTRY: ", operator.get("country", None))
