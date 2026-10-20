# UAE Real Estate API and Scraper

The UAE Real Estate API returns property data from Bayut and PropertyFinder, the UAE's two
largest property portals, through one REST API and one key: listings for sale and rent,
agents, agencies and brokers, and historical sale and rental transactions, as JSON. Neither
portal offers a public listings API, so this is the way to get UAE property data into your
own code without running a Bayut or PropertyFinder scraper. Switching portals is one
parameter.

Built and maintained by [Happy Endpoint](https://happyendpoint.com/library/uae-realestate-api?utm_source=github&utm_medium=readme&utm_campaign=uae-real-estate-api).

- Subscribe and test every endpoint on RapidAPI: https://rapidapi.com/happyendpoint/api/uae-real-estate-api
- Product page: https://happyendpoint.com/library/uae-realestate-api?utm_source=github&utm_medium=readme&utm_campaign=uae-real-estate-api
- Hosted docs: https://docs.happyendpoint.com/uae-realestate/

---

## At a glance

| | |
|---|---|
| Base URL | `https://uae-real-estate-api.p.rapidapi.com` |
| Auth | `x-rapidapi-key` and `x-rapidapi-host` headers |
| Endpoints | 10, plus `/health`, all `GET` |
| Sources | Bayut (200,000+ listings) and PropertyFinder (250,000+ listings), chosen per request with `platform` |
| Coverage | All seven emirates: Dubai, Abu Dhabi, Sharjah, Ajman, Ras Al Khaimah, Fujairah, Umm Al Quwain |
| Currency and units | Prices in AED; area filters in square feet |
| Format | JSON, every response wrapped in `{"success": ..., "platform": ..., "data": ...}` |

---

## What data you get

**Locations**
- Location autocomplete with platform-specific IDs, the location's path and coordinates

**Listings**
- Property search for rent or sale with 15+ filters: property type, bedrooms, bathrooms, price, area, furnishing, completion status (ready or off-plan), rent frequency
- Four sort orders: popular, newest, cheapest, most expensive
- Full property records by ID

**Agents, agencies and brokers**
- Agent and agency (Bayut) or broker (PropertyFinder) search by location, and by name on Bayut
- Agency and agent profiles on Bayut, and every listing an agent or agency has live on either portal

**Transactions**
- Historical sale and rental transactions for an area over 3 months, 6 months, 1 year or 2 years, filtered by property type and bedrooms

---

## Quick start

### 1. Get an API key

Subscribe on [RapidAPI](https://rapidapi.com/happyendpoint/api/uae-real-estate-api). Current plans are listed there. Copy `.env.example` to `.env` and paste your key.

### 2. Make a request

Every request names its portal with `platform=bayut` or `platform=propertyfinder`. Resolve
the area first, then search with its ID:

```bash
curl "https://uae-real-estate-api.p.rapidapi.com/autocomplete?platform=bayut&query=Dubai%20Marina" \
  -H "x-rapidapi-host: uae-real-estate-api.p.rapidapi.com" \
  -H "x-rapidapi-key: YOUR_RAPIDAPI_KEY"

curl "https://uae-real-estate-api.p.rapidapi.com/search-properties?platform=bayut&purpose=rent&location_id=5003&bedrooms=1,2" \
  -H "x-rapidapi-host: uae-real-estate-api.p.rapidapi.com" \
  -H "x-rapidapi-key: YOUR_RAPIDAPI_KEY"
```

You can also pass `location=Dubai Marina` and let the API resolve the name, at the cost of
an extra lookup on every call.

### Python

```bash
pip install -r requirements.txt
cd examples/python
python quickstart.py "Dubai Marina"
```

```python
from client import get, resolve_location

place = resolve_location("bayut", "Dubai Marina")
results = get("/search-properties", "bayut", purpose="rent", location_id=place["location_id"])
for row in results["properties"]:
    print(row["price"], row["rentFrequency"], row["title"]["en"])
```

### JavaScript

```bash
RAPIDAPI_KEY=your_key node examples/javascript/quickstart.mjs "Dubai Marina"
```

---

## Example response

`GET /search-properties?platform=bayut&purpose=rent&location=Dubai Marina&bedrooms=1,2&price_max=100000`,
from the example in the API's public documentation. The other documented examples are in
[`samples/`](samples/).

```json
{
  "success": true,
  "platform": "bayut",
  "data": {
    "properties": [
      {
        "id": "10935141",
        "externalID": "14354275",
        "title": { "en": "Stunning Marina View | 1 Bedroom Unfurnished" },
        "purpose": "for-rent",
        "price": 85000,
        "rentFrequency": "yearly",
        "rooms": 1,
        "baths": 2,
        "area": 64.27,
        "isVerified": true,
        "completionStatus": "completed",
        "amenities": ["Parking", "Swimming Pool", "Gym", "Security"]
      }
    ],
    "total": 1432,
    "page": 1,
    "totalPages": 58,
    "hitsPerPage": 25
  }
}
```

---

## Endpoints

Base URL: `https://uae-real-estate-api.p.rapidapi.com`. Every endpoint takes `platform`
(`bayut` or `propertyfinder`).

### Properties

| Endpoint | Returns |
|---|---|
| `GET /autocomplete` | Locations matching a name, with platform-specific `location_id`, path and coordinates |
| `GET /search-properties` | Listings for rent or sale in a location, with filters, sorting and paging |
| `GET /property-details` | The full record for one listing |

### Agents

| Endpoint | Returns |
|---|---|
| `GET /search-agents` | Agents in a location, or by name on Bayut |
| `GET /agent-details` | An agent's profile (Bayut only) |
| `GET /agent-properties` | Every listing an agent has live |

### Agencies and brokers

| Endpoint | Returns |
|---|---|
| `GET /search-agencies` | Agencies (Bayut) or brokers (PropertyFinder) in a location, or by name on Bayut |
| `GET /agency-details` | An agency's profile (Bayut only) |
| `GET /agency-properties` | Every listing an agency or broker has live |

### Transactions

| Endpoint | Returns |
|---|---|
| `GET /get-transactions` | Historical sale or rental transactions for a location and time period |
| `GET /health` | Service health |

---

## Things to know about the data

The mistakes that give wrong numbers rather than errors:

- **IDs belong to one portal.** `location_id`, `property_id`, `agent_id` and `agency_id` are
  Bayut IDs or PropertyFinder IDs, never both. Resolve a place on each portal separately with
  `/autocomplete`, and check the match's `path` (`UAE > Dubai > Dubai Marina`) so a broad
  match such as the whole emirate does not slip through.
- **On Bayut, `/property-details` wants `externalID`, not `id`.** A search row carries both
  (`"id": "10935141"`, `"externalID": "14354275"` in the documented example). On
  PropertyFinder, use the row's `property_id`.
- **Rents are yearly unless you say otherwise.** UAE rents are quoted per year and
  `rent_frequency` defaults to `yearly`; each row reports its own `rentFrequency`. Do not
  compare a monthly figure with a yearly one, and keep `rent_frequency` fixed in a series.
- **Listings are asking prices; transactions are what was paid.** `/search-properties`
  shows what sellers and landlords ask, `/get-transactions` what was recorded. Yields and
  price trends built on asking prices read high. `asking_vs_paid.py` puts the two side by
  side.
- **Check the area unit before converting.** The `area_min` and `area_max` filters are in
  square feet. The unit of the `area` field in responses is not stated, and the documented
  one-bedroom example has `"area": 64.27`, which reads like square metres. Confirm against
  a listing you know before mixing the two.
- **The vocabulary changes between endpoints.** Search takes `purpose=rent|buy` and returns
  `"purpose": "for-rent"`; transactions take `transaction_type=sale|rental`; agent and agency
  listings take `transaction_type=sale|rental` on PropertyFinder only.
- **PropertyFinder does not report totals.** On PropertyFinder searches `total` is `null`,
  so page until a page comes back empty instead of computing the page count.
- **Some calls exist on Bayut only.** Agent and agency profiles, and searching agents or
  agencies by name, are Bayut-only. On PropertyFinder they return `success: false` with
  `"error": "PLATFORM_LIMITATION"`, and agent or broker search needs a location.
- **Agent listings use a different ID on Bayut.** `/agent-properties` on Bayut takes the
  `ownerID` from `/agent-details`, not the ID from `/search-agents`. Its `sort` and
  `transaction_type` apply to PropertyFinder only.
- **PropertyFinder transactions take one filter value.** For `property_type` and `bedrooms`,
  PropertyFinder uses only the first of several comma-separated values.
- **Bayut transactions are Algolia-shaped strings.** Rows come under `hits`, with `nbHits` and
  `nbPages` for paging (20 rows a page in our live test). Every value is a string:
  `"transaction_amount": "1275000.00"`, `"builtup_area_sqm": "66.34"`, `"beds": "1"`. The
  row also carries `transaction_per_sqm_amount`, the building in `bayut_leaf_location_name_en`
  and, for a resale, `date_previous_sale_transaction_nk`. On sales, `date_start_nk` is a
  `1970-01-01` placeholder, not a date.
- **Property details and transaction rows are platform-specific.** The two portals return
  their own shapes for these, so map fields per platform. `transactions_to_csv.py` writes
  whatever fields come back rather than assuming a column list.
- **Errors come with a code.** `success: false` responses carry `error` (`VALIDATION_ERROR`,
  `NOT_FOUND`, `PLATFORM_LIMITATION`, `PLATFORM_ERROR`, `INTERNAL_ERROR`) and a readable
  `message`. `client.get()` raises them as `ApiError`.

---

## Examples in this repo

| File | What it does |
|---|---|
| [`examples/python/quickstart.py`](examples/python/quickstart.py) | Resolves an area, lists its rentals, then its sale transactions from the last year |
| [`examples/python/asking_vs_paid.py`](examples/python/asking_vs_paid.py) | Median asking price against median paid price for an area, plus gross yield on both |
| [`examples/python/transactions_to_csv.py`](examples/python/transactions_to_csv.py) | Exports sale or rental transactions for an area to CSV, on either portal |
| [`examples/javascript/quickstart.mjs`](examples/javascript/quickstart.mjs) | Resolves an area on both portals and lists Bayut rentals, in Node 18+ with no dependencies |
| [`samples/`](samples/) | The documented example responses |

---

## API, Apify scraper or dataset

| You need | Use |
|---|---|
| Live listings, agents and transactions inside your own app | This API |
| Listings without writing code, exported to a spreadsheet | The [UAE Real Estate Scraper](https://apify.com/happyendpoint/uae-real-estate-scraper) (Bayut) or [PropertyFinder Scraper](https://apify.com/happyendpoint/propertyfinder-scraper) on Apify |
| Years of Dubai transactions in one file | The [Dubai transactions dataset](https://happyendpoint.com/datasets/dubai-transactions-sample?utm_source=github&utm_medium=readme&utm_campaign=uae-real-estate-api) (free 50-row sample) |
| Price drops and delistings tracked every day | The [PropertyFinder Dubai price-change feed](https://happyendpoint.com/data-feeds/propertyfinder-dubai-price-changes?utm_source=github&utm_medium=readme&utm_campaign=uae-real-estate-api) |

A homemade Bayut or PropertyFinder scraper has to follow two different sites, their search
IDs and their anti-bot rules. This API keeps one documented contract for both, so the work
you keep is the analysis.

---

## Use it from Claude, Cursor or any MCP client

RapidAPI exposes every endpoint as an MCP tool, so an AI assistant can query UAE property
data without code:

```json
{
  "mcpServers": {
    "uae-real-estate": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.rapidapi.com",
        "--header",
        "x-api-host: uae-real-estate-api.p.rapidapi.com",
        "--header",
        "x-api-key: YOUR_RAPIDAPI_KEY"
      ]
    }
  }
}
```

| Client | Config path |
|---|---|
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Cursor | `~/.cursor/mcp.json` |
| Claude Code | `.mcp.json` in your project root |

---

## FAQ

### Is there a UAE real estate API?

Bayut and PropertyFinder do not publish public listings APIs. This API, built and maintained
by Happy Endpoint and independent of both portals, returns their listings, agents, agencies
and transactions as JSON. For official Dubai records, the Dubai Land Department also runs
an [API gateway](https://dubailand.gov.ae/en/eservices/api-gateway/).

### Is there a free UAE real estate API?

Yes. The [RapidAPI listing](https://rapidapi.com/happyendpoint/api/uae-real-estate-api) has a free plan, and every endpoint can be tried on it.

### Can I get Bayut and PropertyFinder data with one API key?

Yes. Every endpoint takes `platform=bayut` or `platform=propertyfinder`; the key and the
endpoint structure are the same. IDs and some response shapes differ per portal (see
"Things to know about the data").

### How do I use the UAE real estate API in Python?

Install `requests`, set `RAPIDAPI_KEY`, and use [`examples/python/client.py`](examples/python/client.py).
`get()` adds the headers and the `platform` parameter and raises the API's error codes;
`resolve_location()` turns a place name into a location ID.

### Can I get Dubai property transaction history?

Yes. `/get-transactions` returns sale or rental transactions for a location over 3 months
to 2 years, filtered by property type and bedrooms. For a bulk historical file, see the
[Dubai transactions dataset](https://happyendpoint.com/datasets/dubai-transactions-sample?utm_source=github&utm_medium=readme&utm_campaign=uae-real-estate-api).

### Does it cover Abu Dhabi and the northern emirates?

Yes, all seven emirates, including Abu Dhabi areas such as Al Reem Island, Yas Island and
Saadiyat Island.

### Is there an API for Bayut or PropertyFinder only?

Yes. The [bayut-api](https://github.com/happyendpointhq/bayut-api) and
[propertyfinder-api](https://github.com/happyendpointhq/propertyfinder-api) repos cover the
single-portal APIs, which go deeper into each site.

---

## Related repos

- [bayut-api](https://github.com/happyendpointhq/bayut-api) - the Bayut-only API, with off-plan projects and developers
- [propertyfinder-api](https://github.com/happyendpointhq/propertyfinder-api) - the PropertyFinder-only API
- [uae-real-estate-data-guide](https://github.com/happyendpointhq/uae-real-estate-data-guide) - every way to get UAE property data: APIs, datasets and official sources
- [dubai-rental-yield-calculator](https://github.com/happyendpointhq/dubai-rental-yield-calculator) - gross and net yields by Dubai area
- [awesome-real-estate-apis](https://github.com/happyendpointhq/awesome-real-estate-apis) - real estate APIs and data sources by country

---

## Disclaimer

Happy Endpoint is an independent provider. This project is **not affiliated
with, endorsed by, sponsored by, or connected to** any of the websites,
platforms, retailers, or marketplaces referenced here or reachable through the
underlying APIs.

All product names, brands, trademarks, and registered trademarks are the
property of their respective owners. Any reference to them is descriptive only,
to identify the subject matter of the data, and does not imply any association
or endorsement.

Users are responsible for ensuring their use of any data complies with
applicable laws and the terms of service of the relevant source.

---

## About Happy Endpoint

[Happy Endpoint](https://happyendpoint.com) builds and maintains real-time data
APIs for property portals, retailers, and marketplaces. All APIs are available on
RapidAPI with a free tier.

- Catalogue: [happyendpoint.com/library](https://happyendpoint.com/library)
- Datasets: [happyendpoint.com/datasets](https://happyendpoint.com/datasets)
- Documentation: [docs.happyendpoint.com](https://docs.happyendpoint.com)
- Contact: happyendpointhq@gmail.com

## Licence

MIT. See [LICENSE](LICENSE).
