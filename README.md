# LEGO Investment Tracker

Compare LEGO set appreciation against S&P 500 returns. Track which sets gain value after retirement and whether LEGO collecting beats the stock market.

## Live Dashboard

[View the Dashboard](https://nathannorman.github.io/personal-lego-investing/)

## Features

- Track LEGO sets from the last 24 months
- Compare returns vs S&P 500 (SPY ETF)
- Analyze performance by theme (Star Wars, Technic, etc.)
- See retired vs available set performance
- Visual charts and detailed data table

## Data Sources

- **LEGO Set Data**: [BrickSet API](https://brickset.com/tools/webservices/requestkey) (free)
- **Current Prices**: eBay sold listings, Amazon 3rd party sellers
- **S&P 500 Data**: Yahoo Finance via yfinance

## Setup

### 1. Install Dependencies

```bash
pip install -e .
```

### 2. Get a BrickSet API Key

1. Create a free account at [BrickSet.com](https://brickset.com)
2. Request an API key at [Web Services](https://brickset.com/tools/webservices/requestkey)
3. Create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your API key
```

### 3. Fetch LEGO Set Data

```bash
python scripts/brickset_client.py
```

### 4. Add Current Prices

The script generates a CSV template for price lookup:

```bash
python scripts/price_collector.py
```

This creates `data/processed/price_lookup_template.csv` with eBay search links.
Fill in the `current_price` column from your research, then import:

```python
from scripts.price_collector import load_sets, import_prices_from_csv, save_sets_with_prices

sets = load_sets("data/processed/lego_sets.json")
sets = import_prices_from_csv(sets, "data/processed/prices.csv")
save_sets_with_prices(sets, "data/processed/lego_sets.json")
```

### 5. Run Locally

Open `index.html` in a browser, or use a local server:

```bash
python -m http.server 8000
# Visit http://localhost:8000
```

## Project Structure

```
personal-lego-investing/
├── index.html              # Dashboard (GitHub Pages)
├── data/
│   └── processed/
│       └── sample_sets.json  # Sample data
├── scripts/
│   ├── brickset_client.py  # BrickSet API client
│   ├── market_data.py      # S&P 500 data
│   └── price_collector.py  # Price management
├── pyproject.toml          # Python dependencies
└── README.md
```

## Key Insights

From LEGO investment research:

1. **Retired sets appreciate faster** - Once a set retires from LEGO.com, scarcity drives prices up
2. **Themes matter** - Star Wars UCS, Modular Buildings, and Ideas sets tend to perform best
3. **Timing is key** - Best returns come from buying at retail and selling 1-2 years after retirement
4. **Storage costs** - Factor in the cost of storing sealed boxes

## Contributing

This is a personal project, but feel free to fork and adapt for your own LEGO investment tracking!

## License

MIT
