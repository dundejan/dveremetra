from flask import Flask, render_template, request, jsonify
from typing import List, Dict, Optional
import unicodedata
import re
import json
from pathlib import Path

app = Flask(__name__)

# Metro line stations
stations_a: List[str] = [
    "Nemocnice Motol", "Petřiny", "Nádraží Veleslavín", "Bořislavka", "Dejvická",
    "Hradčanská", "Malostranská", "Staroměstská", "Můstek", "Muzeum",
    "Náměstí Míru", "Jiřího z Poděbrad", "Flora", "Želivského", "Strašnická",
    "Skalka", "Depo Hostivař"
]

stations_b: List[str] = [
    "Zličín", "Stodůlky", "Luka", "Lužiny", "Hůrka", "Nové Butovice", "Jinonice",
    "Radlická", "Smíchovské nádraží", "Anděl", "Karlovo náměstí", "Národní třída",
    "Můstek", "Náměstí Republiky", "Florenc", "Křižíkova", "Invalidovna",
    "Palmovka", "Českomoravská", "Vysočanská", "Kolbenova", "Hloubětín",
    "Rajská zahrada", "Černý Most"
]

stations_c: List[str] = [
    "Letňany", "Prosek", "Střížkov", "Ládví", "Kobylisy", "Nádraží Holešovice",
    "Vltavská", "Florenc", "Hlavní nádraží", "Muzeum", "I.P. Pavlova",
    "Vyšehrad", "Pražského povstání", "Pankrác", "Budějovická", "Kačerov",
    "Roztyly", "Chodov", "Opatov", "Háje"
]

# Load door data from JSON files
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
door_data_a = json.load(open(DATA_DIR / "door_data_a.json", encoding="utf-8"))
door_data_b = json.load(open(DATA_DIR / "door_data_b.json", encoding="utf-8"))
door_data_c = json.load(open(DATA_DIR / "door_data_c.json", encoding="utf-8"))


# Preprocess station names for better typeahead
def preprocess_station_name(station: str) -> str:
    """Remove diacritics, punctuation, and convert to lowercase for comparison."""
    normalized = unicodedata.normalize('NFD', station)
    no_diacritics = ''.join(char for char in normalized if not unicodedata.combining(char))
    no_punctuation = re.sub(r'[^\w\s]', '', no_diacritics)
    return no_punctuation.lower()


stations_preprocessed: Dict[str, str] = {
    station: preprocess_station_name(station) for station in (stations_a + stations_b + stations_c)
}


# Match stations based on query and related station
def match_stations(query: str, related_to: str) -> List[str]:
    """Find matching stations based on query and related station line."""
    query = preprocess_station_name(query)

    # Determine relevant line
    if related_to in stations_a:
        relevant_stations = stations_a
    elif related_to in stations_b:
        relevant_stations = stations_b
    elif related_to in stations_c:
        relevant_stations = stations_c
    else:
        relevant_stations = stations_a + stations_b + stations_c

    return [
        station for station in relevant_stations
        if query in preprocess_station_name(station)
    ]


# Determine direction based on station order
def get_direction(start: str, end: str, stations: List[str]) -> str:
    """Determine direction based on station order."""
    start_index: int = stations.index(start)
    end_index: int = stations.index(end)
    return "to_hostivar" if start_index < end_index else "to_motol"


@app.route('/', methods=['GET', 'POST'])
def home() -> str:
    start: Optional[str] = None
    end: Optional[str] = None
    suggestions: Optional[List[Dict[str, str | int]]] = None
    error_message: Optional[str] = None

    if request.method == 'POST':
        start = request.form['start']
        end = request.form['end']

        # Determine which line to use
        if start in stations_a and end in stations_a:
            relevant_stations = stations_a
            door_data = door_data_a
        elif start in stations_b and end in stations_b:
            relevant_stations = stations_b
            door_data = door_data_b
        elif start in stations_c and end in stations_c:
            relevant_stations = stations_c
            door_data = door_data_c
        else:
            relevant_stations = None
            door_data = None

        if relevant_stations is None or start not in relevant_stations or end not in relevant_stations:
            error_message = "Zadané stanice nejsou platné nebo nejsou na stejné lince."
        elif start == end:
            error_message = "Výchozí a cílová stanice nemohou být stejné."
        else:
            direction: str = get_direction(start, end, relevant_stations)
            suggestions = door_data.get(end, {}).get(direction, [])

    return render_template(
        'index.html',
        start=start,
        end=end,
        suggestions=suggestions,
        error_message=error_message,
        stations=stations_a + stations_b + stations_c
    )


@app.route('/stations', methods=['GET'])
def get_stations() -> str:
    query: str = request.args.get('query', '')
    related_to: str = request.args.get('related_to', '')  # Line context

    # Define transfer stations with special icons
    transfer_stations = {
        "Můstek": {
            "lines": [stations_a, stations_b],
            "icon": "/static/mustek.svg"
        },
        "Muzeum": {
            "lines": [stations_a, stations_c],
            "icon": "/static/muzeum.svg"
        },
        "Florenc": {
            "lines": [stations_b, stations_c],
            "icon": "/static/florenc.svg"
        }
    }

    # Determine relevant stations and line metadata
    station_line_map = {}
    for station in stations_a:
        station_line_map[station] = {"line": "a", "icon": "/static/line_a.svg"}
    for station in stations_b:
        station_line_map[station] = {"line": "b", "icon": "/static/line_b.svg"}
    for station in stations_c:
        station_line_map[station] = {"line": "c", "icon": "/static/line_c.svg"}

    # Overwrite icons for transfer stations
    for transfer_station, data in transfer_stations.items():
        station_line_map[transfer_station] = {"line": "transfer", "icon": data["icon"]}

    # Determine relevant stations based on related_to
    if related_to in transfer_stations:
        relevant_stations = [station for line in transfer_stations[related_to]["lines"] for station in line]
    elif related_to in stations_a:
        relevant_stations = stations_a
    elif related_to in stations_b:
        relevant_stations = stations_b
    elif related_to in stations_c:
        relevant_stations = stations_c
    else:
        relevant_stations = stations_a + stations_b + stations_c

    # Remove duplicates and add metadata
    matched_stations = [
        {"name": station, **station_line_map[station]}
        for station in dict.fromkeys(relevant_stations)  # Remove duplicates
        if query.lower() in preprocess_station_name(station)
    ]

    return jsonify(matched_stations)


if __name__ == '__main__':
    app.run(debug=True)
