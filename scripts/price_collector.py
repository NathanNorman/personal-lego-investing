"""
Price collector for LEGO sets from secondary markets.

Currently supports:
- Manual price entry
- CSV import

Future enhancements (would require API keys):
- eBay API integration
- Amazon Product Advertising API
- BrickLink price guide
"""

import json
import csv
from datetime import datetime
from pathlib import Path


def load_sets(sets_path: str) -> list[dict]:
    """Load LEGO sets from JSON file."""
    with open(sets_path, "r") as f:
        return json.load(f)


def save_sets_with_prices(sets: list[dict], output_path: str) -> None:
    """Save sets with updated prices."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(sets, f, indent=2, default=str)
    print(f"Saved {len(sets)} sets to {output_path}")


def add_price_to_set(
    sets: list[dict],
    set_number: str,
    current_price: float,
    price_source: str = "manual",
    price_date: str | None = None,
) -> list[dict]:
    """Add current market price to a set."""
    if not price_date:
        price_date = datetime.now().strftime("%Y-%m-%d")

    for s in sets:
        if s["set_number"] == set_number:
            s["current_price"] = current_price
            s["price_source"] = price_source
            s["price_date"] = price_date
            s["price_premium_pct"] = round(
                (current_price - s["retail_price_usd"]) / s["retail_price_usd"] * 100, 2
            ) if s.get("retail_price_usd") else None
            print(f"Updated {set_number}: ${current_price} ({s.get('price_premium_pct', 0):+.1f}%)")
            return sets

    print(f"Set {set_number} not found")
    return sets


def import_prices_from_csv(sets: list[dict], csv_path: str) -> list[dict]:
    """
    Import prices from CSV file.

    CSV format: set_number,current_price,source
    Example:
    75192,899.99,ebay
    42115,459.99,amazon
    """
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sets = add_price_to_set(
                sets,
                row["set_number"],
                float(row["current_price"]),
                row.get("source", "csv_import"),
            )
    return sets


def generate_price_lookup_list(sets: list[dict], output_path: str) -> None:
    """
    Generate a CSV template for manual price lookup.

    This creates a list of sets to look up on eBay/Amazon.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "set_number",
            "name",
            "theme",
            "retail_price_usd",
            "is_retired",
            "current_price",
            "source",
            "ebay_search_url",
        ])

        for s in sets:
            # Generate eBay search URL
            search_term = f"lego {s['set_number']}"
            ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={search_term.replace(' ', '+')}&_sacat=19006&LH_Sold=1&LH_Complete=1"

            writer.writerow([
                s["set_number"],
                s["name"],
                s["theme"],
                s["retail_price_usd"],
                s["is_retired"],
                "",  # current_price - to be filled
                "",  # source - to be filled
                ebay_url,
            ])

    print(f"Generated price lookup template: {output_path}")
    print("Fill in 'current_price' and 'source' columns, then import back")


def calculate_portfolio_metrics(sets: list[dict]) -> dict:
    """Calculate aggregate metrics for sets with prices."""
    priced_sets = [s for s in sets if s.get("current_price") and s.get("retail_price_usd")]

    if not priced_sets:
        return {"error": "No sets with prices found"}

    total_retail = sum(s["retail_price_usd"] for s in priced_sets)
    total_current = sum(s["current_price"] for s in priced_sets)
    total_return = (total_current - total_retail) / total_retail * 100

    # Count winners/losers
    winners = [s for s in priced_sets if s["current_price"] > s["retail_price_usd"]]
    losers = [s for s in priced_sets if s["current_price"] < s["retail_price_usd"]]
    breakeven = [s for s in priced_sets if s["current_price"] == s["retail_price_usd"]]

    # Best and worst performers
    sorted_by_return = sorted(
        priced_sets,
        key=lambda x: (x["current_price"] - x["retail_price_usd"]) / x["retail_price_usd"],
        reverse=True,
    )

    return {
        "total_sets": len(priced_sets),
        "total_retail_value": round(total_retail, 2),
        "total_current_value": round(total_current, 2),
        "total_profit": round(total_current - total_retail, 2),
        "total_return_pct": round(total_return, 2),
        "winners": len(winners),
        "losers": len(losers),
        "breakeven": len(breakeven),
        "win_rate_pct": round(len(winners) / len(priced_sets) * 100, 2),
        "best_performers": [
            {
                "set_number": s["set_number"],
                "name": s["name"],
                "return_pct": round(
                    (s["current_price"] - s["retail_price_usd"]) / s["retail_price_usd"] * 100, 2
                ),
            }
            for s in sorted_by_return[:5]
        ],
        "worst_performers": [
            {
                "set_number": s["set_number"],
                "name": s["name"],
                "return_pct": round(
                    (s["current_price"] - s["retail_price_usd"]) / s["retail_price_usd"] * 100, 2
                ),
            }
            for s in sorted_by_return[-5:]
        ],
    }


if __name__ == "__main__":
    # Example usage
    data_dir = Path(__file__).parent.parent / "data" / "processed"
    sets_file = data_dir / "lego_sets.json"

    if sets_file.exists():
        sets = load_sets(str(sets_file))
        generate_price_lookup_list(sets, str(data_dir / "price_lookup_template.csv"))
    else:
        print("No sets file found. Run brickset_client.py first.")
