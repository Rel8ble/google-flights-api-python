"""Find the cheapest day to fly with Python via the Google Flights Scraper on Apify.

Searches one route on several departure dates in a single run, keeps the cheapest
itinerary per date and writes every itinerary to a CSV.

pip install -r requirements.txt
set APIFY_TOKEN in your environment (or paste it below)
python example.py
"""
import csv
import os
from datetime import date, timedelta

from apify_client import ApifyClient

client = ApifyClient(os.environ.get("APIFY_TOKEN", "<YOUR_APIFY_TOKEN>"))

ORIGIN, DESTINATION = "JFK", "LAX"
first_day = date.today() + timedelta(days=30)
dates = [(first_day + timedelta(days=i)).isoformat() for i in range(7)]

run_input = {
    "searches": [{"origin": ORIGIN, "destination": DESTINATION, "departureDate": d} for d in dates],
    "adults": 1,
    "cabinClass": "economy",
    "maxStops": "0",                  # nonstop only; use "any" for everything
    "currency": "USD",
    "maxResults": 10,                 # you pay per itinerary, keep it small while testing
}

run = client.actor("rel8ble/google-flights-scraper").call(run_input=run_input)
flights = list(client.dataset(run["defaultDatasetId"]).iterate_items())
print(f"Got {len(flights)} itineraries for {len(dates)} dates")

cheapest = {}
for f in flights:
    if f.get("price") is None:
        continue
    d = f["searchDepartureDate"]
    if d not in cheapest or f["price"] < cheapest[d]["price"]:
        cheapest[d] = f

for d in sorted(cheapest):
    f = cheapest[d]
    print(f"{d}  ${f['price']:>5}  {f['departureTime']}-{f['arrivalTime']}  "
          f"{', '.join(f['flightNumbers'])}  ({f.get('priceLevel') or 'n/a'})")

if cheapest:
    best = min(cheapest.values(), key=lambda f: f["price"])
    print(f"Cheapest day: {best['searchDepartureDate']} at ${best['price']}")

fields = ["searchId", "searchDepartureDate", "price", "currency", "priceLevel", "airlines",
          "flightNumbers", "stops", "totalDuration", "departureTime", "arrivalTime",
          "emissionsKg", "googleFlightsUrl"]
with open("google_flights.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    for f in flights:
        row = dict(f)
        row["airlines"] = ", ".join(f.get("airlines") or [])
        row["flightNumbers"] = ", ".join(f.get("flightNumbers") or [])
        w.writerow(row)
print("Saved all itineraries to google_flights.csv")
