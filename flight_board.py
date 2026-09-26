"""
Washington State live flight radar — data collector.
 
Polls the OpenSky Network REST API every 5 seconds for aircraft inside a
bounding box over Washington State, converts the raw state vectors into a
human-readable format, and writes the result to flight_data.json for the
web front end (index.html) to display.
 
Requires a `credentials.json` file next to this script, containing an
OpenSky API client id/secret:
 
    {
      "clientId": "your-client-id",
      "clientSecret": "your-client-secret"
    }
 
Without it, the script still runs, but against OpenSky's unauthenticated
(lower rate limit) endpoint.
"""

import requests
import time
import os
import json

url = "https://opensky-network.org/api/states/all"
auth_url = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

max_lat = 49.00
min_lat = 45.54
max_lon = -116.91
min_lon = -124.80

DEFAULT_CLIENT_ID = ""
DEFAULT_CLIENT_SECRET = ""

script_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(script_dir, "credentials.json")

client_id = None
client_secret = None

if os.path.exists(cred_path):
    try:
        with open(cred_path, "r") as f:
            creds = json.load(f)
            client_id = creds.get("clientId")
            client_secret = creds.get("clientSecret")
            print("Successfully loaded credentials from credentials.json!")
    except Exception as e:
        print(f"Error reading credentials.json: {e}")

if not client_id or not client_secret:
    print("Using direct client credentials from script variables.")
    client_id = DEFAULT_CLIENT_ID
    client_secret = DEFAULT_CLIENT_SECRET

def get_access_token():
    if not client_id or not client_secret:
        return None
    try:
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        res = requests.post(auth_url, data=data, timeout=10)
        if res.status_code == 200:
            token = res.json().get('access_token')
            print("Successfully acquired OAuth access token!")
            return token
        else:
            print(f"Auth failed with status {res.status_code}: {res.text}")
            return None
    except Exception as e:
        print(f"Failed to retrieve access token: {e}")
        return None

# Fetch initial access token
access_token = get_access_token()

print("Contacting radar for Washington State airspace")

while True:
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Updating Washington State Radar Data...")

        params = {
            'lamin': min_lat,
            'lamax': max_lat,
            'lomin': min_lon,
            'lomax': max_lon
        }

        headers = {}
        if access_token:
            headers['Authorization'] = f"Bearer {access_token}"

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 401 and client_id:
            print("Token expired. Fetching fresh access token...")
            access_token = get_access_token()
            if access_token:
                headers['Authorization'] = f"Bearer {access_token}"
                response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            wa_flights = []

            if data and 'states' in data and data['states'] is not None:

                # Flight Data Board
                for flight in data['states']:
                    callsign = flight[1]
                    country = flight[2]
                    lon = flight[5]
                    lat = flight[6]
                    altitude = flight[7]
                    velocity = flight[9]
                    track = flight[10]
                    vertical_rate = flight[11]

                    if lat is not None and lon is not None:
                        callsign = callsign.strip() if callsign and callsign.strip() != "" else "Unknown"
                        alt_display = "On Ground" if altitude is None else f"{int(altitude * 3.28084):,} ft" # converted m to ft
                        vel_display = "N/A" if velocity is None else f"{int(velocity * 2.23694)} mph"

                        if vertical_rate is None or vertical_rate == 0:
                            vrate_display = "Level"
                        else:
                            fpm = int(vertical_rate * 196.85)  # 1 m/s = ~196.85 fpm
                            vrate_display = f"+{fpm} fpm" if fpm > 0 else f"{fpm} fpm"

                        wa_flights.append({
                            "Callsign": callsign,
                            "Country": country if country else "Unknown",
                            "Latitude": round(lat, 4),
                            "Longitude": round(lon, 4),
                            "Altitude": alt_display,
                            "Velocity": vel_display,
                            "Track": track if track is not None else 0,
                            "VerticalRate": vrate_display
                        })

            with open("flight_data.json", "w") as file:
                json.dump(wa_flights, file)

            print(f"Successfully tracked {len(wa_flights)} aircraft across the US.")

        elif response.status_code == 429:
            print("Rate limited by OpenSky API (HTTP 429). Waiting for next cycle...")
        else:
            print(f"Server returned HTTP Status Code: {response.status_code}")

    except Exception as e:
        print(f"Error fetching data: {e}")

    time.sleep(10)


