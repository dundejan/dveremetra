from flask import Flask, render_template, request, jsonify
from typing import List, Dict, Optional
import unicodedata
import re

app = Flask(__name__)


stations_a: List[str] = [
    "Nemocnice Motol", "Petřiny", "Nádraží Veleslavín", "Bořislavka", "Dejvická",
    "Hradčanská", "Malostranská", "Staroměstská", "Můstek", "Muzeum",
    "Náměstí Míru", "Jiřího z Poděbrad", "Flora", "Želivského", "Strašnická",
    "Skalka", "Depo Hostivař"
]


door_data_a: Dict[str, Dict[str, List[Dict[str, str | int]]]] = {
    "Nemocnice Motol": {
        # "to_motol": [{"car": 1, "door": 4, "exit": "Main exit"}, {"car": 5, "door": 1, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 1, "door": 1, "exit": "Main exit"}, {"car": 5, "door": 4, "exit": "Secondary exit"}]
    },
    "Petřiny": {
        # "to_motol": [{"car": 5, "door": 4, "exit": "Main exit"}, {"car": 3, "door": 2, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 5, "door": 1, "exit": "Main exit"}, {"car": 5, "door": 3, "exit": "Secondary exit"}]
    },
    "Nádraží Veleslavín": {
        # "to_motol": [{"car": 5, "door": 2, "exit": "Main exit"}, {"car": 1, "door": 1, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 1, "door": 1, "exit": "Main exit"}, {"car": 3, "door": 4, "exit": "Secondary exit"}]
    },
    "Bořislavka": {
        # "to_motol": [{"car": 2, "door": 1, "exit": "Main exit"}, {"car": 5, "door": 3, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 2, "door": 1, "exit": "Main exit"}, {"car": 2, "door": 1, "exit": "Secondary exit"}]
    },
    "Dejvická": {
        # "to_motol": [{"car": 1, "door": 3, "exit": "Main exit"}, {"car": 3, "door": 1, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 3, "door": 1, "exit": "Main exit"}, {"car": 4, "door": 2, "exit": "Secondary exit"}]
    },
    "Hradčanská": {
        # "to_motol": [{"car": 1, "door": 1, "exit": "Main exit"}, {"car": 4, "door": 2, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 5, "door": 1, "exit": "Main exit"}, {"car": 5, "door": 4, "exit": "Secondary exit"}]
    },
    "Malostranská": {
        # "to_motol": [{"car": 5, "door": 2, "exit": "Main exit"}, {"car": 4, "door": 2, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 2, "door": 3, "exit": "Main exit"}, {"car": 2, "door": 2, "exit": "Secondary exit"}]
    },
    "Staroměstská": {
        # "to_motol": [{"car": 2, "door": 3, "exit": "Main exit"}, {"car": 4, "door": 4, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 3, "door": 3, "exit": "Main exit"}, {"car": 5, "door": 3, "exit": "Secondary exit"}]
    },
    "Můstek": {
        # "to_motol": [{"car": 3, "door": 2, "exit": "Main exit"}, {"car": 2, "door": 2, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 2, "door": 2, "exit": "Main exit"}, {"car": 1, "door": 2, "exit": "Secondary exit"}]
    },
    "Muzeum": {
        # "to_motol": [{"car": 4, "door": 1, "exit": "Main exit"}, {"car": 2, "door": 1, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 4, "door": 4, "exit": "Main exit"}, {"car": 4, "door": 1, "exit": "Secondary exit"}]
    },
    "Náměstí Míru": {
        "to_motol": [{"car": 2, "door": 1, "exit": "Náměstí Míru"}],
        "to_hostivar": [{"car": 4, "door": 4, "exit": "Náměstí Míru"}]
    },
    "Jiřího z Poděbrad": {
        # "to_motol": [{"car": 3, "door": 3, "exit": "Main exit"}, {"car": 3, "door": 3, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 3, "door": 3, "exit": "Main exit"}, {"car": 5, "door": 4, "exit": "Secondary exit"}]
    },
    "Flora": {
        # "to_motol": [{"car": 3, "door": 4, "exit": "Main exit"}, {"car": 3, "door": 2, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 2, "door": 1, "exit": "Main exit"}, {"car": 1, "door": 1, "exit": "Secondary exit"}]
    },
    "Želivského": {
        # "to_motol": [{"car": 2, "door": 3, "exit": "Main exit"}, {"car": 5, "door": 3, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 1, "door": 2, "exit": "Main exit"}, {"car": 5, "door": 4, "exit": "Secondary exit"}]
    },
    "Strašnická": {
        # "to_motol": [{"car": 5, "door": 4, "exit": "Main exit"}, {"car": 3, "door": 3, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 1, "door": 4, "exit": "Main exit"}, {"car": 5, "door": 1, "exit": "Secondary exit"}]
    },
    "Skalka": {
        # "to_motol": [{"car": 1, "door": 1, "exit": "Main exit"}, {"car": 2, "door": 3, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 1, "door": 2, "exit": "Main exit"}, {"car": 1, "door": 1, "exit": "Secondary exit"}]
    },
    "Depo Hostivař": {
        # "to_motol": [{"car": 5, "door": 3, "exit": "Main exit"}, {"car": 2, "door": 2, "exit": "Secondary exit"}],
        # "to_hostivar": [{"car": 1, "door": 4, "exit": "Main exit"}, {"car": 5, "door": 3, "exit": "Secondary exit"}]
    }
}


# Preprocess station names for better typeahead
def preprocess_station_name(station: str) -> str:
    """Remove diacritics, punctuation, and convert to lowercase for comparison."""
    normalized = unicodedata.normalize('NFD', station)
    no_diacritics = ''.join(char for char in normalized if not unicodedata.combining(char))
    no_punctuation = re.sub(r'[^\w\s]', '', no_diacritics)
    return no_punctuation.lower()


stations_preprocessed: Dict[str, str] = {
    station: preprocess_station_name(station) for station in stations_a
}


def match_stations(query: str) -> List[str]:
    """Find matching stations based on user input."""
    query = preprocess_station_name(query)
    matched = [
        station for station, normalized in stations_preprocessed.items()
        if query in normalized
    ]
    return matched


def get_direction(start: str, end: str, stations: List[str]) -> str:
    """Určí směr podle pořadí stanic."""
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

        if start not in stations_a or end not in stations_a:
            error_message = "Zadané stanice nejsou platné."
        elif start == end:
            error_message = "Výchozí a cílová stanice nemohou být stejné."
        else:
            direction: str = get_direction(start, end, stations_a)
            suggestions = door_data_a.get(end, {}).get(direction, [])

    return render_template(
        'index.html',
        start=start,
        end=end,
        suggestions=suggestions,
        error_message=error_message,
        stations=stations_a
    )


@app.route('/stations', methods=['GET'])
def get_stations() -> str:
    query: str = request.args.get('query', '')
    matched_stations = match_stations(query) if query else stations_a
    return jsonify(matched_stations)


if __name__ == '__main__':
    app.run(debug=True)
