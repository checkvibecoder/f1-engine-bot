import requests
from datetime import datetime
import traceback

JOLPICA = "https://api.jolpi.ca/ergast/f1"
OUTPUT_FILE = "index.html"

def safe_request(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def get_latest_race():
    data = safe_request(f"{JOLPICA}/current/last/results.json")

    if "error" in data:
        return None, None, data["error"]

    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    if not races:
        return None, None, "No race data available"

    race = races[0]
    return race["raceName"], race.get("Results", []), None

def get_latest_qualifying():
    data = safe_request(f"{JOLPICA}/current/last/qualifying.json")

    if "error" in data:
        return None, data["error"]

    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    if not races:
        return None, "No qualifying data available"

    return races[0].get("QualifyingResults", []), None

def build_html(race_name, race_results, quali_results, error_msg):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

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
                <td>{r.get('Q3', '-')}</td>
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
    background:#0f0f0f;
    color:#f1f1f1;
    font-family:Arial;
    margin:40px;
}}
h1 {{ color:#e10600; }}
table {{
    width:100%;
    border-collapse:collapse;
    margin-bottom:40px;
}}
th, td {{
    padding:10px;
    border-bottom:1px solid #333;
}}
th {{ background:#1c1c1c; }}
tr:hover {{ background:#222; }}
.timestamp {{ color:#888; font-size:14px; }}
.error {{ color:#ff4444; }}
</style>
</head>
<body>

<h1>🏎️ F1 Engine Dashboard</h1>
<p class="timestamp">Last updated: {timestamp} UTC</p>

{"<p class='error'>Error: " + error_msg + "</p>" if error_msg else ""}

<h2>🏁 Latest Race - {race_name if race_name else "Unavailable"}</h2>
<table>
<tr><th>Pos</th><th>Driver</th><th>Team</th><th>Points</th></tr>
{race_rows if race_rows else "<tr><td colspan='4'>No race results</td></tr>"}
</table>

<h2>🚦 Latest Qualifying (Top 10)</h2>
<table>
<tr><th>Pos</th><th>Driver</th><th>Q3</th></tr>
{quali_rows if quali_rows else "<tr><td colspan='3'>No qualifying results</td></tr>"}
</table>

</body>
</html>
"""

def main():
    try:
        race_name, race_results, race_error = get_latest_race()
        quali_results, quali_error = get_latest_qualifying()

        error_msg = race_error or quali_error

        html = build_html(race_name, race_results, quali_results, error_msg)

        with open(OUTPUT_FILE, "w") as f:
            f.write(html)

        print("index.html generated successfully")

    except Exception:
        fallback_html = f"""
        <html>
        <body style="background:black;color:red;font-family:Arial;">
        <h1>Critical Error</h1>
        <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        """
        with open(OUTPUT_FILE, "w") as f:
            f.write(fallback_html)

        print("Fallback error page written")

if __name__ == "__main__":
    main()
