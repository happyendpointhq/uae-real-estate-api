"""Export historical sale or rental transactions for an area to CSV.

    python transactions_to_csv.py "Dubai Marina" --type sale --period 2y --out marina-sales.csv

Transaction rows are platform-specific, so this writes every field it finds (nested
objects are flattened to dotted column names) instead of a fixed column list.
"""

import argparse
import csv

from client import get, resolve_location


def rows_of(data):
    """Bayut returns rows under `hits`; fall back to the first list in the payload."""
    if isinstance(data, list):
        return data
    if "hits" in data:
        return data["hits"]
    return next((v for v in data.values() if isinstance(v, list)), [])


def flatten(row, prefix=""):
    flat = {}
    for key, value in row.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(flatten(value, f"{name}."))
        else:
            flat[name] = value
    return flat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("area")
    parser.add_argument("--platform", default="bayut", choices=["bayut", "propertyfinder"])
    parser.add_argument("--type", default="sale", choices=["sale", "rental"])
    parser.add_argument("--period", default="1y", choices=["3m", "6m", "1y", "2y"])
    parser.add_argument("--property-type", help="apartment, villa, townhouse, penthouse, ...")
    parser.add_argument("--bedrooms", help="comma-separated, 0 = studio")
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--out", default="transactions.csv")
    args = parser.parse_args()

    place = resolve_location(args.platform, args.area)
    print(f"{place['name']} ({place['path']}) on {args.platform}")

    rows = []
    for page in range(1, args.max_pages + 1):
        data = get(
            "/get-transactions",
            args.platform,
            transaction_type=args.type,
            location_id=place["location_id"],
            property_type=args.property_type,
            bedrooms=args.bedrooms,
            time_period=args.period,
            sort="newest",
            page=page,
        )
        batch = [flatten(r) for r in rows_of(data)]
        if not batch:
            break
        rows += batch
        print(f"page {page}: {len(rows)} rows")
        # Bayut pages like Algolia: nbHits rows over nbPages pages.
        pages = data.get("nbPages") if isinstance(data, dict) else None
        if pages is not None and page >= pages:
            break

    columns = sorted({key for row in rows for key in row})
    with open(args.out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
