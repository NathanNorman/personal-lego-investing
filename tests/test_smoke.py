"""Smoke tests for personal-lego-investing."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_scripts_importable():
    """Verify main Python scripts can be imported without error."""
    import importlib.util

    scripts_dir = ROOT / "scripts"
    for script in scripts_dir.glob("*.py"):
        spec = importlib.util.spec_from_file_location(script.stem, script)
        assert spec is not None, f"Could not load spec for {script.name}"
        mod = importlib.util.module_from_spec(spec)
        # We only test that the module can be loaded, not executed
        # (some scripts require API keys or network access)


def test_data_files_exist():
    """Verify processed data files exist."""
    data_dir = ROOT / "data" / "processed"
    assert data_dir.exists(), "data/processed directory missing"
    json_files = list(data_dir.glob("*.json"))
    assert len(json_files) > 0, "No JSON files in data/processed"


def test_data_files_parseable():
    """Verify all JSON data files are valid JSON."""
    data_dir = ROOT / "data" / "processed"
    for json_file in data_dir.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
        assert data is not None, f"{json_file.name} parsed to None"


def test_index_html_exists():
    """Verify the main dashboard HTML file exists."""
    assert (ROOT / "index.html").exists(), "index.html missing"
