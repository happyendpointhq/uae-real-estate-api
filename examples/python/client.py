"""Minimal client for the UAE Real Estate API (Bayut and PropertyFinder) on RapidAPI.

Set RAPIDAPI_KEY in your environment (or in a .env file at the repo root).
"""

import os

import requests

HOST = "uae-real-estate-api.p.rapidapi.com"


def _load_dotenv():
    """Read RAPIDAPI_KEY from a .env in the current folder or the repo root, if present."""
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    for path in (".env", os.path.join(root, ".env")):
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                key, sep, value = line.strip().partition("=")
                if sep and value and not key.startswith("#"):
                    os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


class ApiError(RuntimeError):
    """A `success: false` response. `code` is VALIDATION_ERROR, NOT_FOUND,
    PLATFORM_LIMITATION, PLATFORM_ERROR or INTERNAL_ERROR."""

    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def get(path, platform, **params):
    """GET an endpoint for one platform ("bayut" or "propertyfinder") and return `data`."""
    key = os.environ.get("RAPIDAPI_KEY")
    if not key:
        raise SystemExit("Set RAPIDAPI_KEY first (see .env.example).")
    response = requests.get(
        f"https://{HOST}{path}",
        params={"platform": platform, **{k: v for k, v in params.items() if v is not None}},
        headers={"x-rapidapi-host": HOST, "x-rapidapi-key": key},
        timeout=60,
    )
    try:
        body = response.json()
    except ValueError:
        response.raise_for_status()
        raise
    # Errors carry a code and a readable message; keep them instead of a bare HTTP status.
    if not body.get("success", False):
        raise ApiError(body.get("error", response.status_code), body.get("message", ""))
    response.raise_for_status()
    return body["data"]


def resolve_location(platform, name):
    """Return the best /autocomplete match for a place name on one platform.

    Location IDs are platform-specific, so resolve them per platform and check `path`
    to make sure the match is the area you meant.
    """
    matches = get("/autocomplete", platform, query=name)
    if not matches:
        raise SystemExit(f"No {platform} location matches {name!r}")
    return matches[0]


def title(listing):
    """Search rows carry the title as {"en": "..."}; fall back to a plain string."""
    value = listing.get("title")
    return value.get("en") if isinstance(value, dict) else value
