# Sample responses

The example responses published in the UAE Real Estate API's documentation, saved as
files. Field names and values are unchanged; a placeholder key standing for "the rest of
the record" was removed from the search example. All examples are from Bayut
(`platform=bayut`). PropertyFinder returns its own shapes for some endpoints.

| File | Request |
|---|---|
| `autocomplete.json` | `GET /autocomplete?platform=bayut&query=Dubai Marina` |
| `search-properties.json` | `GET /search-properties?platform=bayut&purpose=rent&location=Dubai Marina&bedrooms=1,2&price_max=100000` |
| `search-agencies.json` | `GET /search-agencies?platform=bayut&query=DAMAC` |
| `get-transactions.json` | `GET /get-transactions?platform=bayut&transaction_type=sale&location_id=5003&time_period=1y&sort=newest` (a live response from 20 Oct 2026, cut to two rows, because the documentation's example uses different field names from what the API returns) |
| `error-platform-limitation.json` | `GET /agent-details?platform=propertyfinder&agent_id=123` |

They are useful for writing parsers and tests before you subscribe. Live data changes
daily, so do not hard-code these values.
