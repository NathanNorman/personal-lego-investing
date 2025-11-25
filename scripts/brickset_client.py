"""
BrickSet API Client for fetching LEGO set data.

API Documentation: https://brickset.com/article/52664/api-version-3-documentation
Get your free API key: https://brickset.com/tools/webservices/requestkey
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://brickset.com/api/v3.asmx"


class BrickSetClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("BRICKSET_API_KEY")
        if not self.api_key:
            raise ValueError(
                "BrickSet API key required. Get one free at: "
                "https://brickset.com/tools/webservices/requestkey"
            )
        self.user_hash = None

    def _request(self, method: str, params: dict | None = None) -> dict:
        """Make a request to the BrickSet API."""
        url = f"{BASE_URL}/{method}"
        data = {"apiKey": self.api_key}
        if params:
            data.update(params)

        response = requests.get(url, params=data)
        response.raise_for_status()
        return response.json()

    def check_key(self) -> bool:
        """Verify the API key is valid."""
        result = self._request("checkKey")
        return result.get("status") == "success"

    def get_sets(
        self,
        year: int | None = None,
        theme: str | None = None,
        page_size: int = 500,
        page_number: int = 1,
        order_by: str = "YearFromDESC",
    ) -> list[dict]:
        """
        Fetch sets with optional filters.

        Args:
            year: Filter by release year
            theme: Filter by theme (e.g., 'Star Wars', 'Technic')
            page_size: Results per page (max 500)
            page_number: Page number for pagination
            order_by: Sort order (YearFromDESC, PiecesDESC, etc.)
        """
        params_dict = {}
        if year:
            params_dict["year"] = str(year)
        if theme:
            params_dict["theme"] = theme

        params = {
            "params": json.dumps(params_dict),
            "pageSize": page_size,
            "pageNumber": page_number,
            "orderBy": order_by,
        }

        result = self._request("getSets", params)
        if result.get("status") != "success":
            raise Exception(f"API Error: {result.get('message', 'Unknown error')}")

        return result.get("sets", [])

    def get_all_sets_for_years(self, years: list[int]) -> list[dict]:
        """Fetch all sets for multiple years, handling pagination."""
        all_sets = []

        for year in years:
            page = 1
            while True:
                sets = self.get_sets(year=year, page_number=page)
                if not sets:
                    break
                all_sets.extend(sets)
                print(f"Fetched {len(sets)} sets from {year}, page {page}")
                page += 1

        return all_sets

    def get_years(self, theme: str | None = None) -> list[dict]:
        """Get list of years with set counts."""
        params = {}
        if theme:
            params["theme"] = theme

        result = self._request("getYears", params)
        if result.get("status") != "success":
            raise Exception(f"API Error: {result.get('message', 'Unknown error')}")

        return result.get("years", [])


def extract_set_data(raw_set: dict) -> dict:
    """Extract relevant fields from a BrickSet API response."""
    # Get US retail price if available
    us_retail = None
    if raw_set.get("LEGOCom", {}).get("US", {}).get("retailPrice"):
        us_retail = raw_set["LEGOCom"]["US"]["retailPrice"]

    # Determine retirement status
    # If dateAddedToSAH is null and availability is "Retail", it's still available
    availability = raw_set.get("availability", "")
    is_retired = availability in ["Retired", "Unknown"] or "retired" in availability.lower()

    return {
        "set_number": raw_set.get("number"),
        "name": raw_set.get("name"),
        "year": raw_set.get("year"),
        "theme": raw_set.get("theme"),
        "subtheme": raw_set.get("subtheme"),
        "pieces": raw_set.get("pieces"),
        "minifigs": raw_set.get("minifigs"),
        "retail_price_usd": us_retail,
        "release_date": raw_set.get("launchDate"),
        "exit_date": raw_set.get("exitDate"),
        "is_retired": is_retired,
        "availability": availability,
        "rating": raw_set.get("rating"),
        "brickset_url": raw_set.get("bricksetURL"),
        "image_url": raw_set.get("image", {}).get("imageURL"),
    }


def fetch_recent_sets(output_path: str | None = None) -> list[dict]:
    """
    Fetch all sets from the last 24 months.

    Returns processed set data ready for analysis.
    """
    client = BrickSetClient()

    # Check API key first
    if not client.check_key():
        raise Exception("Invalid API key")

    # Get current year and previous year
    current_year = datetime.now().year
    years = [current_year, current_year - 1]
    if datetime.now().month <= 6:
        # If early in the year, include year before last too
        years.append(current_year - 2)

    print(f"Fetching sets for years: {years}")
    raw_sets = client.get_all_sets_for_years(years)

    # Process and filter to last 24 months
    cutoff_date = datetime.now() - timedelta(days=730)  # ~24 months
    processed_sets = []

    for raw_set in raw_sets:
        set_data = extract_set_data(raw_set)

        # Filter: must have a retail price and release date
        if not set_data["retail_price_usd"]:
            continue

        # Parse release date if available
        if set_data["release_date"]:
            try:
                release = datetime.strptime(set_data["release_date"], "%Y-%m-%dT%H:%M:%SZ")
                if release < cutoff_date:
                    continue
            except (ValueError, TypeError):
                pass

        processed_sets.append(set_data)

    print(f"Found {len(processed_sets)} sets with retail prices from last 24 months")

    # Save to file if path provided
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(processed_sets, f, indent=2, default=str)
        print(f"Saved to {output_path}")

    return processed_sets


if __name__ == "__main__":
    # Test the client
    output_file = Path(__file__).parent.parent / "data" / "processed" / "lego_sets.json"
    sets = fetch_recent_sets(str(output_file))
    print(f"\nSample set: {json.dumps(sets[0] if sets else {}, indent=2)}")
