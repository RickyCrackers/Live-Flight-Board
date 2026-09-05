# Washington State Live Flight Radar

A live map of aircraft flying over Washington State, built to practice
consuming a real REST API, handling OAuth token refresh, and turning raw
data into something visual.

## What it does

- Polls the [OpenSky Network](https://opensky-network.org/) API every 5
  seconds for aircraft inside a bounding box over Washington State.
- Converts raw state vectors (altitude in meters, speed in m/s, etc.)
  into readable units (feet, mph, feet-per-minute climb/descent rate).
- Writes the result to `flight_data.json`.
- A Leaflet-based web page (`index.html`) reads that file and plots each
  aircraft on a map, with a sidebar list and a click-through detail panel.

## Why

This was a relearning project — refreshing on Python (my prior experience
is mostly Java) by working through something with a real external API:
OAuth client-credentials auth, token expiry/retry logic, JSON parsing,
and unit conversion.

## Setup

1. Install dependencies:
   ```bash
   pip install requests
   ```
2. (Optional, but recommended) Get a free OpenSky API client ID/secret
   from your [OpenSky account settings](https://opensky-network.org/my-opensky/account),
   then copy `credentials.example.json` to `credentials.json` and fill in
   your values. Without this file, the script still runs against
   OpenSky's public endpoint, just with a lower rate limit.
3. Run the collector:
   ```bash
   python flight_board.py
   ```
4. Open `index.html` in a browser (or serve the folder, e.g.
   `python -m http.server`) while the collector is running.

## Project structure

```
flight_board.py          # polls OpenSky, writes flight_data.json
index.html                # Leaflet map + sidebar UI, reads flight_data.json
flight_data.json          # generated at runtime — latest snapshot
credentials.example.json  # template for your own credentials.json
```

## What I'd add next

- Persist snapshots over time (SQLite) instead of overwriting the file
  each cycle, so historical queries are possible — busiest hour, average
  altitude, longest-flying aircraft, etc.
- Basic tests around the unit-conversion and state-parsing logic.
- Expand beyond Washington State bounding box to a configurable region.
