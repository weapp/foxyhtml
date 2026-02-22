#!/usr/bin/env python3
"""
Downloads Wikipedia fixtures for the benchmarks.

Usage:
    python benchmarks/download_fixtures.py

Wikipedia content is licensed under CC-BY-SA 4.0.
"""
import urllib.request
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"

FIXTURES = {
    "wikipedia_actor.html": (
        "https://en.wikipedia.org/api/rest_v1/page/html/Charlie_Chaplin",
        "Charlie Chaplin — Wikipedia (CC-BY-SA 4.0)",
    ),
}

HEADERS = {
    "User-Agent": (
        "foxyhtml-benchmark/1.0 "
        "(educational HTML parsing benchmark; https://github.com/weapp/foxyhtml)"
    )
}


def download(name: str, url: str, description: str) -> None:
    dest = FIXTURES_DIR / name
    if dest.exists():
        kb = dest.stat().st_size / 1024
        print(f"  already exists: {name} ({kb:.0f} KB)")
        return

    print(f"  downloading: {description}")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read()
    dest.write_bytes(html)
    print(f"  saved:       {name} ({len(html) / 1024:.0f} KB)")


if __name__ == "__main__":
    print("Downloading benchmark fixtures...\n")
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    for name, (url, desc) in FIXTURES.items():
        download(name, url, desc)
    print("\nDone. Run: python benchmarks/bench.py")
