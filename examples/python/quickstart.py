"""Resolve an area on Bayut, list rentals in it, and pull its recent sale transactions.

    python quickstart.py "Dubai Marina"
"""

import sys

from client import get, resolve_location, title

area = sys.argv[1] if len(sys.argv) > 1 else "Dubai Marina"
PLATFORM = "bayut"

# 1. Resolve the name to a platform-specific location_id (faster and unambiguous).
place = resolve_location(PLATFORM, area)
print(f"{place['name']}  id={place['location_id']}  ({place['path']})")

# 2. One and two-bedroom rentals, cheapest first. Prices are AED per year by default.
results = get(
    "/search-properties",
    PLATFORM,
    purpose="rent",
    location_id=place["location_id"],
    bedrooms="1,2",
    sort="price_low",
    rent_frequency="yearly",
)
print(f"\n{results['total']} rentals, page {results['page']} of {results['totalPages']}")
for row in results["properties"]:
    print(f"AED {row['price']:>9,} /{row['rentFrequency']:<7} {row['rooms']} bed  {title(row)}")
    # For /property-details on Bayut, pass externalID, not id.
    print(f"{'':>22}property_id for details: {row['externalID']}")

# 3. What actually sold in the last 12 months (paid prices, not asking prices).
sales = get(
    "/get-transactions",
    PLATFORM,
    transaction_type="sale",
    location_id=place["location_id"],
    time_period="1y",
    sort="newest",
)
# Bayut transaction rows are Algolia-shaped (hits, nbHits, nbPages) and every value is a
# string, so convert amounts before doing arithmetic with them.
print(f"\n{sales['nbHits']:,} sale transactions in the last year, newest:")
for deal in sales["hits"][:10]:
    print(
        f"{deal['date_transaction_nk'][:10]}  AED {float(deal['transaction_amount']):>13,.0f}  "
        f"{deal['beds']} bed  {deal['builtup_area_sqm']} m2  {deal['bayut_leaf_location_name_en']}"
    )
