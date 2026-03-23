# LED-flights

A toy project where I render flight data of planes that fly around my house on an LED screen. I do this by listening to ADS-B broadcasts via a USB software define radio (SDR) dongle.

## TODO
- automate downloading database from https://www.mictronics.de/aircraft-database/export.php every week
    - store JSON --> sqlite
- for each plane, lookup ICAO in sqlite, then draw on LED:
    - callsign - aircraft type
    - operator
    - From -> To
