import requests
from datetime import datetime

JOLPICA = "https://api.jolpi.ca/ergast/f1"
OUTPUT_FILE = "index.html"

def get_latest_race():
    try:
        r = requests.get(f"{JOLPICA}/current/last/results.json", timeout=10)
        data = r.json()
        races = data["MRData"]["RaceTable"]["Races"]
        if not races:
            return None, None
        race = races[0]
        return race["raceName"], race["Results"]
    except:
        return None, None

def get_latest_qualifying():
    try:
        r = requests.get(f"{JOLPICA}/current/last/qualifying.json", timeout=10)
        data = r.json()
        races = data["MRData"]["RaceTable"]["Races"]
        if not races:
            return None
        return races[0]["QualifyingResults"]
    except:
        return None

def build_html(race_name, race_results, quali_results):
    race_rows = ""
    if race_results:
        for r in race_results[:10]:
            race_rows += f"""
            <tr>
                <td>{r['position']}</td>
                <td>{r['Driver']['givenName']} {r['Driver']['familyName']}</td>
                <td>{r['Constructor']['name']}</td>
                <td>{r['points']}</td>
            </tr>
            """

    quali_rows = ""
    if quali_results:
        for r in quali_results[:10]:
            quali_rows += f"""
            <tr>
                <td>{r['position']}</td>
                <td>{r['Driver']['familyName']}</td>
                <td>{r.get('Q3','-')}</td>
            </tr>
            """

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="60">
    <title>F1 Engine Dashboard</title>
    <style>
        body {{
            background-color: #0f0f0f;
            color: #f1f1f1;
            font-family: Arial, sans-serif;
            margin: 40px;
        }}
        h1 {{
            color: #e10600;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 40px;
        }}
        th, td {{
            padding: 10px;
            border-bottom: 1px solid #333;
            text-align: left;
        }}
        th {{
            background-color: #1c1c1c;
        }}
        tr:hover {{
            background-color: #222;
        }}
        .timestamp {{
            font-size: 14px;
            color: #888;
        }}
    </style>
</head>
<body>

<h1>🏎️ F1 Engine Dashboard</h1>
<p class="timestamp">Last updated: {datetime.utcnow()} UTC</p>

<h2>🏁 Latest Race - {race_name if race_name else "No race yet"}</h2>
<table>
<tr>
    <th>Pos</th>
    <th>Driver</th>
    <th>Team</th>
    <th>Points</th>
</tr>
{race_rows if race_rows else "<tr><td colspan='4'>No race data available</td></tr>"}
</table>

<h2>🚦 Latest Qualifying (Top 10)</h2>
<table>
<tr>
    <th>Pos</th>
    <th>Driver</th>
    <th>Q3 Time</th>
</tr>
{quali_rows if quali_rows else "<tr><td colspan='3'>No qualifying data available</td></tr>"}
</table>

</body>
</html>
"""

def main():
    race_name, race_results = get_latest_race()
    quali_results = get_latest_qualifying()

    html = build_html(race_name, race_results, quali_results)

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)

    print("Dashboard updated successfully")

if __name__ == "__main__":
    main()
