# Google Flights API in Python: scrape flight prices, airlines, stops and layovers from Google Flights to JSON/CSV

A short tutorial for pulling **Google Flights search results** (total price, Google's low/typical/high price level, airlines, flight numbers, stops, layovers, departure and arrival times, aircraft, legroom, CO2 emissions) into Python with the [Google Flights Scraper](https://apify.com/rel8ble/google-flights-scraper) on Apify. Google has no public Flights API (the old QPX Express API was shut down in 2018); this works as an unofficial one.

> Disclosure: I built this actor; it's a paid tool on Apify ($0.50 per 1,000 itineraries). The code in this repo is MIT-licensed.

## How it works

You give it a route (IATA codes like `JFK` and `LAX`, several comma-separated airports, or a Google city id such as `/m/02_286` for all New York airports) and a date. The actor loads the Google Flights results page over plain HTTPS through Apify Proxy and parses the structured itinerary data Google embeds in it. No headless browser, no cookies, no Google account. One-way and round trips are supported; for round trips it can expand the top N outbound flights into full round-trip rows.

## Quick start (Python)

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")

run = client.actor("rel8ble/google-flights-scraper").call(run_input={
    "origin": "JFK",
    "destination": "LAX",
    "departureDate": "2026-11-12",
    "adults": 1,
    "cabinClass": "economy",
    "maxStops": "0",
    "maxResults": 10,
})

for f in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(f["price"], f["priceLevel"], f["departureTime"], f["flightNumbers"])
```

[`example.py`](example.py) is the runnable version: it searches one route on 7 departure dates in a single run, prints the cheapest nonstop per day and writes every itinerary to a CSV.

## Quick start (Node.js)

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/google-flights-scraper').call({
    origin: 'SFO', destination: 'ORD', departureDate: '2026-10-20', returnDate: '2026-10-23', maxResults: 10,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items.length, 'round trips');
```

## Input

| Field | Default | What it does |
|---|---|---|
| `origin` / `destination` | `JFK` / `LAX` | IATA code, comma-separated codes (`LHR,LGW`) or a Google city id |
| `departureDate` | today + 30 days | `YYYY-MM-DD`, up to ~11 months ahead |
| `returnDate` | none (one-way) | Set it for a round trip |
| `searches` | none | Many routes/dates in one run: `[{"origin": "JFK", "destination": "LAX", "departureDate": "2026-12-03"}]` |
| `adults`, `children`, `infantsInSeat`, `infantsOnLap` | 1, 0, 0, 0 | Prices are totals for all passengers (max 9) |
| `cabinClass` | `economy` | `premium_economy`, `business`, `first` |
| `maxStops` | `any` | `"0"` nonstop only, `"1"`, `"2"` |
| `airlines` | all | IATA codes (`["AA", "DL"]`) or `STAR_ALLIANCE`, `ONEWORLD`, `SKYTEAM` |
| `currency` | `USD` | Any ISO 4217 code |
| `maxResults` | 50 | Itineraries per search; `0` = everything Google shows |
| `returnFlightsForTopOutbound` | 3 | Round trips: expand the top N outbound flights into full round-trip rows (0-30) |
| `language` / `country` | `en` / `us` | Google `hl` / `gl`; `country` can change the fares shown |

## Output sample (one real itinerary, trimmed)

```json
{
  "searchId": "MAD-BCN 2026-10-15",
  "tripType": "one_way",
  "origin": "MAD",
  "destination": "BCN",
  "cabinClass": "economy",
  "currency": "USD",
  "position": 1,
  "category": "best",
  "price": 59,
  "priceLevel": "typical",
  "airlines": ["Air Europa"],
  "airlineCodes": ["UX"],
  "flightNumbers": ["UX 7701"],
  "stops": 0,
  "totalDurationMinutes": 85,
  "totalDuration": "1 hr 25 min",
  "departureAirport": "MAD",
  "departureDateTime": "2026-10-15T07:30:00+02:00",
  "arrivalAirport": "BCN",
  "arrivalDateTime": "2026-10-15T08:55:00+02:00",
  "layovers": [],
  "segments": [
    { "flightNumber": "UX 7701", "airline": "Air Europa", "aircraft": "Boeing 787",
      "durationMinutes": 85, "legroom": "31 in", "emissionsKg": 51 }
  ],
  "emissionsKg": 51,
  "typicalEmissionsKg": 64,
  "emissionsDifferencePercent": -20,
  "returnFlight": null,
  "googleFlightsUrl": "https://www.google.com/travel/flights/booking?tfs=CBwQAhpAEgoyMDI2LTEwLTE1IiAKA01BRBIKMjAyNi0xMC0xNRoDQkNOKgJVWDIENzcwMWoHCAESA01BRHIHCAESA0JDTkABSAFwAZgBAg&hl=en&gl=us&curr=USD"
}
```

Round-trip rows carry the same fields for the return leg in `returnFlight`, and `price` is the full round-trip total.

## Use cases

- **Cheapest-day finder**: put 7-30 dates for one route in `searches` and pick the lowest `price` per date (that's what `example.py` does).
- **Fare alerts**: schedule the same route daily on Apify and alert when `price` drops or `priceLevel` turns `low`.
- **Route and airline research**: compare carriers, nonstop share and durations across city pairs with `airlineCodes`, `stops` and `totalDurationMinutes`.
- **Travel and expense tools**: price trips per passenger mix and cabin, with CO2 per itinerary for sustainability reporting.

## Price

**$0.50 per 1,000 itineraries**, pay per result. A one-way search usually returns 10-40 itineraries, so one route/date costs about $0.005-$0.02. No start fee, no monthly rental. Apify's free plan includes $5 of monthly credit.

## Limits

- Returns what is on Google's initial results page (in tests: 36 JFK-LAX one-way options, 18 Madrid-Barcelona, 7 Charlotte-Tokyo).
- Multi-city (3+ legs) searches are not supported; one-way and round trip are.
- Per-agency booking prices (Expedia vs the airline) and baggage fees are not extracted; `googleFlightsUrl` opens the booking options on Google.
- Google sells about 11 months ahead, and at most 9 passengers per search.

## Links

- Actor on the Apify Store: https://apify.com/rel8ble/google-flights-scraper
- Apify Python client docs: https://docs.apify.com/api/client/python

## License

MIT
