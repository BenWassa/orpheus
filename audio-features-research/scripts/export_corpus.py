#!/usr/bin/env python3
"""Export the full track corpus to CSV for external research.

Usage:
    python audio-features-research/scripts/export_corpus.py
    python audio-features-research/scripts/export_corpus.py --out /tmp/corpus.csv
"""
import argparse
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / "data" / "cache" / "orpheus.db"
DEFAULT_OUT = Path(__file__).parent.parent / "corpus_full.csv"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT track_uri, isrc, mbid, track_name, primary_artist, album_name, duration_ms "
        "FROM tracks ORDER BY track_name"
    ).fetchall()

    out = Path(args.out)
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["track_uri", "isrc", "mbid", "track_name", "primary_artist", "album_name", "duration_ms"]
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    print(f"Exported {len(rows)} tracks to {out}")
    conn.close()


if __name__ == "__main__":
    main()
