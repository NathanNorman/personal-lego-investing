# Contributing to LEGO Investment Tracker

Thanks for your interest in contributing!

## Development Setup

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -e .
   ```
3. Copy the environment file:
   ```bash
   cp .env.example .env
   ```
4. Add your [BrickSet API key](https://brickset.com/tools/webservices/requestkey) to `.env`

## Running Locally

Open `index.html` in a browser, or use a local server:

```bash
python -m http.server 8000
# Visit http://localhost:8000
```

## Data Pipeline

1. Fetch LEGO set data: `python scripts/brickset_client.py`
2. Generate price template: `python scripts/price_collector.py`
3. Fill in current prices in the generated CSV
4. Import prices back into the dataset

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-change`)
3. Make your changes
4. Test the dashboard locally in a browser
5. Commit with a clear message
6. Open a pull request

## Project Structure

- `index.html` - Dashboard (served via GitHub Pages)
- `scripts/` - Python data collection and processing
- `data/processed/` - Processed data for the dashboard
- `pyproject.toml` - Python project configuration
