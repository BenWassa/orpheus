#!/usr/bin/env python3
"""Probe a candidate audio-feature API against 10 sample tracks.

Edit the CONFIG block below for the API you're testing, then run:
    python audio-features-research/scripts/probe_api.py

Prints: hit rate, raw response sample, and field mapping to Orpheus schema.
"""
import csv
import json
import time
from pathlib import Path

import requests

# ── CONFIG ────────────────────────────────────────────────────────────────────
API = "reccobeats"          # label for output; change as needed
BASE_URL = "https://api.reccobeats.com/v1/track"  # replace with actual endpoint
API_KEY = "YOUR_API_KEY_HERE"
RESOLUTION_KEY = "isrc"     # "isrc", "spotify_id", or "name+artist"
SAMPLE_SIZE = 10
DELAY_BETWEEN_REQUESTS = 0.5  # seconds; increase if rate-limited
# ─────────────────────────────────────────────────────────────────────────────

CORPUS = Path(__file__).parent.parent / "corpus_sample.csv"


def load_sample(n: int) -> list[dict]:
    rows = []
    with open(CORPUS, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if len(rows) >= n:
                break
    return rows


def fetch_reccobeats(row: dict) -> dict | None:
    """Example adapter — replace body with the real API shape."""
    isrc = row.get("isrc", "")
    if not isrc:
        return None
    resp = requests.get(
        BASE_URL,
        params={"isrc": isrc},
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=10,
    )
    if resp.status_code == 200:
        return resp.json()
    print(f"  HTTP {resp.status_code} for {isrc}: {resp.text[:120]}")
    return None


def map_to_orpheus(raw: dict) -> dict:
    """Map API response fields to Orpheus audio_features schema.
    Edit this for each API you test.
    """
    return {
        "valence": raw.get("valence"),
        "arousal": raw.get("arousal") or raw.get("energy"),  # arousal proxy
        "tempo": raw.get("tempo"),
        "key": raw.get("key"),
        "mode": raw.get("mode"),
        "energy": raw.get("energy"),
        "danceability": raw.get("danceability"),
        "acousticness": raw.get("acousticness"),
        "instrumentalness": raw.get("instrumentalness"),
        "loudness": raw.get("loudness"),
        "spectral_centroid": raw.get("spectral_centroid"),
        "spectral_complexity": raw.get("spectral_complexity"),
    }


def main():
    tracks = load_sample(SAMPLE_SIZE)
    print(f"Testing {API} against {len(tracks)} tracks (resolution: {RESOLUTION_KEY})\n")

    hits = 0
    for i, row in enumerate(tracks):
        label = f"{row['track_name']} — {row['primary_artist']}"
        raw = fetch_reccobeats(row)
        if raw:
            mapped = map_to_orpheus(raw)
            has_va = mapped["valence"] is not None and mapped["arousal"] is not None
            status = "HIT (V/A ok)" if has_va else "HIT (no V/A)"
            hits += 1
            print(f"[{i+1:2d}] {status}: {label}")
            if i == 0:
                print("     raw sample:", json.dumps(raw, indent=6)[:400])
        else:
            print(f"[{i+1:2d}] MISS: {label}")
        time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"\nHit rate: {hits}/{len(tracks)} ({100*hits//len(tracks)}%)")
    print("Extrapolated coverage for 4,243 tracks:", int(4243 * hits / len(tracks)))


if __name__ == "__main__":
    main()
