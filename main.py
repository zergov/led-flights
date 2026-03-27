import json

from aircraft import Aircraft






with open("/tmp/aircraft.json", "r") as f:
    data = json.loads(f.read())
    aircrafts: dict[str, Aircraft] = {}

    for aircraft_data in data["aircraft"]:
        icao = aircraft_data["hex"]

        if not icao:
            pass

        aircraft = Aircraft(aircraft_data)

        print("------------------------------")
        print("ICAO: ", aircraft.icao_hex())
        print("FLIGHT: ", aircraft.flight())
        print("ALTITUDE: ", aircraft.altitude())
        print("SQUAWK: ", aircraft.squawk())

        aircrafts[aircraft.icao_hex()] = aircraft
