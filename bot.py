import requests
import tweepy
import os
import json

STATE_FILE = "state.json"
JOLPICA = "https://api.jolpi.ca/ergast/f1"

# -----------------------
# STATE
# -----------------------

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def reset_state(round_number):
    return {
        "round": round_number,
        "practice_posted": False,
        "qualifying_posted": False,
        "sprint_posted": False,
        "race_final_posted": False,
        "last_lap": 0
    }

# -----------------------
# TWITTER
# -----------------------

def post_tweet(text):
    client = tweepy.Client(
        bearer_token=os.getenv("BEARER_TOKEN"),
        consumer_key=os.getenv("API_KEY"),
        consumer_secret=os.getenv("API_SECRET"),
        access_token=os.getenv("ACCESS_TOKEN"),
        access_token_secret=os.getenv("ACCESS_SECRET")
    )
    client.create_tweet(text=text)

# -----------------------
# JOLPICA HELPERS
# -----------------------

def get_current_round():
    try:
        r = requests.get(f"{JOLPICA}/current.json", timeout=10)
        data = r.json()
        races = data["MRData"]["RaceTable"]["Races"]
        if not races:
            return None
        return races[-1]["round"]
    except:
        return None

def get_session(endpoint):
    try:
        r = requests.get(endpoint, timeout=10)
        data = r.json()
        races = data["MRData"]["RaceTable"]["Races"]
        if not races:
            return None
        return races[0]
    except:
        return None

# -----------------------
# OPENF1 LIVE RACE
# -----------------------

def get_live_race_session():
    try:
        r = requests.get("https://api.openf1.org/v1/sessions?session_type=Race", timeout=10)
        sessions = r.json()
        for s in sessions:
            if s.get("session_status") == "Started":
                return s
        return None
    except:
        return None

def handle_live_race(state):
    session = get_live_race_session()
    if not session:
        return state

    session_key = session["session_key"]

    try:
        lap_resp = requests.get(
            f"https://api.openf1.org/v1/laps?session_key={session_key}",
            timeout=10
        )
        laps = lap_resp.json()
        if not laps:
            return state

        current_lap = max(l["lap_number"] for l in laps)

        if state.get("last_lap") == current_lap:
            return state

        pos_resp = requests.get(
            f"https://api.openf1.org/v1/position?session_key={session_key}&lap_number={current_lap}",
            timeout=10
        )
        positions = pos_resp.json()
        if not positions:
            return state

        positions = sorted(positions, key=lambda x: x["position"])
        top5 = positions[:5]

        lines = []
        for p in top5:
            lines.append(f"P{p['position']} Driver #{p['driver_number']}")

        post_tweet(f"🏁 Live Race Update - Lap {current_lap}\n\n" + "\n".join(lines))

        state["last_lap"] = current_lap

    except:
        pass

    return state

# -----------------------
# SESSION HANDLERS
# -----------------------

def handle_practice(state, round_number):
    if state.get("practice_posted"):
        return state

    endpoint = f"{JOLPICA}/current/{round_number}/results.json"
    race = get_session(endpoint)
    if not race:
        return state

    results = race.get("Results", [])
    if len(results) < 7:
        return state

    top7 = results[:7]
    lines = [f"P{r['position']} {r['Driver']['familyName']}" for r in top7]

    post_tweet("🟢 Practice Classification - Top 7\n\n" + "\n".join(lines))

    state["practice_posted"] = True
    return state

def handle_qualifying(state, round_number):
    if state.get("qualifying_posted"):
        return state

    endpoint = f"{JOLPICA}/current/{round_number}/qualifying.json"
    quali = get_session(endpoint)
    if not quali:
        return state

    results = quali.get("QualifyingResults", [])
    if len(results) < 20:
        return state

    q1 = results[15:20]
    q2 = results[10:15]
    q3 = results[:10]

    post_tweet("🚦 Q1 Eliminated\n\n" + "\n".join([f"P{r['position']} {r['Driver']['familyName']}" for r in q1]))
    post_tweet("🚦 Q2 Eliminated\n\n" + "\n".join([f"P{r['position']} {r['Driver']['familyName']}" for r in q2]))
    post_tweet("🏁 Qualifying Results\n\n" + "\n".join([f"P{r['position']} {r['Driver']['familyName']}" for r in q3]))

    state["qualifying_posted"] = True
    return state

def handle_sprint(state, round_number):
    if state.get("sprint_posted"):
        return state

    endpoint = f"{JOLPICA}/current/{round_number}/sprint.json"
    sprint = get_session(endpoint)
    if not sprint:
        return state

    results = sprint.get("SprintResults", [])
    if len(results) < 8:
        return state

    top8 = results[:8]
    lines = [f"P{r['position']} {r['Driver']['familyName']}" for r in top8]

    post_tweet("⚡ Sprint Race Results\n\n" + "\n".join(lines))

    state["sprint_posted"] = True
    return state

def handle_final_race(state, round_number):
    if state.get("race_final_posted"):
        return state

    endpoint = f"{JOLPICA}/current/{round_number}/results.json"
    race = get_session(endpoint)
    if not race:
        return state

    results = race.get("Results", [])
    if len(results) < 10:
        return state

    top10 = results[:10]
    lines = [f"P{r['position']} {r['Driver']['familyName']}" for r in top10]

    post_tweet("🏆 Final Race Results - Top 10\n\n" + "\n".join(lines))

    state["race_final_posted"] = True
    return state

# -----------------------
# MAIN
# -----------------------

def main():
    state = load_state()
    round_number = get_current_round()

    if not round_number:
        save_state(state)
        return

    if state.get("round") != round_number:
        state = reset_state(round_number)

    state = handle_practice(state, round_number)
    state = handle_qualifying(state, round_number)
    state = handle_sprint(state, round_number)
    state = handle_live_race(state)
    state = handle_final_race(state, round_number)

    save_state(state)

if __name__ == "__main__":
    main()
