"""Compare asking prices with what actually sold, and the gross rental yield, for one area.

    python asking_vs_paid.py "Dubai Marina" --bedrooms 1

Asking prices come from /search-properties (live listings), paid prices from
/get-transactions (recorded sales). The two answer different questions: listings show
what sellers hope for, transactions show what buyers paid.
"""

import argparse
from statistics import median

from client import get, resolve_location

PLATFORM = "bayut"


def listing_prices(location_id, purpose, bedrooms, pages, **extra):
    prices = []
    for page in range(1, pages + 1):
        data = get(
            "/search-properties",
            PLATFORM,
            purpose=purpose,
            location_id=location_id,
            bedrooms=bedrooms,
            page=page,
            **extra,
        )
        prices += [row["price"] for row in data["properties"] if row.get("price")]
        if not data.get("totalPages") or page >= data["totalPages"]:
            break
    return prices


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("area")
    parser.add_argument("--bedrooms", default="1", help="0 = studio")
    parser.add_argument("--property-type", default="apartment")
    parser.add_argument("--pages", type=int, default=3, help="listing pages to sample per side")
    args = parser.parse_args()

    place = resolve_location(PLATFORM, args.area)
    print(f"{place['name']} ({place['path']}), {args.bedrooms} bed {args.property_type}\n")

    asking_sale = listing_prices(
        place["location_id"], "buy", args.bedrooms, args.pages, property_type=args.property_type
    )
    asking_rent = listing_prices(
        place["location_id"], "rent", args.bedrooms, args.pages,
        property_type=args.property_type, rent_frequency="yearly",
    )
    sold = get(
        "/get-transactions",
        PLATFORM,
        transaction_type="sale",
        location_id=place["location_id"],
        property_type=args.property_type,
        bedrooms=args.bedrooms,
        time_period="1y",
    )
    # Bayut transaction amounts are strings ("1275000.00").
    paid = [float(deal["transaction_amount"]) for deal in sold["hits"] if deal.get("transaction_amount")]

    if not (asking_sale and asking_rent and paid):
        raise SystemExit("Not enough listings or transactions to compare; widen the filters.")

    m_ask, m_rent, m_paid = median(asking_sale), median(asking_rent), median(paid)
    print(f"median asking sale price   AED {m_ask:>12,.0f}  ({len(asking_sale)} listings)")
    print(f"median paid price (1 year) AED {m_paid:>12,.0f}  (newest {len(paid)} of {sold['nbHits']:,} transactions)")
    print(f"asking above paid          {(m_ask - m_paid) / m_paid:+.1%}")
    print(f"median asking rent         AED {m_rent:>12,.0f} a year  ({len(asking_rent)} listings)")
    print(f"gross yield on paid price  {m_rent / m_paid:.2%}")
    print(f"gross yield on asking      {m_rent / m_ask:.2%}")


if __name__ == "__main__":
    main()
