#!/usr/bin/env python3
"""One-time project setup for Orpheus v2."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main():
    project_root = Path(__file__).parent.parent

    dirs = [
        "data/raw",
        "data/cache",
        "data/output/reports",
    ]
    for d in dirs:
        path = project_root / d
        path.mkdir(parents=True, exist_ok=True)
        print(f"  Directory: {path}")

    config_template = project_root / "config.yaml.template"
    config_file = project_root / "config.yaml"
    if not config_file.exists():
        shutil.copy(config_template, config_file)
        print(f"  Created config.yaml from template")
    else:
        print(f"  config.yaml already exists")

    from orpheus.config import load_config, validate_config
    from orpheus.db import ensure_schema, get_db, run_migrations

    cfg = load_config(project_root=project_root)
    errors = validate_config(cfg)
    if errors:
        print(f"\n  Config validation errors:")
        for e in errors:
            print(f"    - {e}")
    else:
        print(f"  Config valid")

    conn = get_db(cfg.db_path)
    ensure_schema(conn)
    applied = run_migrations(conn)
    conn.close()
    print(f"  Database initialized at {cfg.db_path}")
    if applied:
        print(f"  Applied migrations: {applied}")

    print("\nNext steps:")
    print("  1. Edit config.yaml with your API credentials")
    print("  2. Place Spotify Extended Streaming History JSON in data/raw/")
    print("  3. Run: orpheus run-all --source data/raw/")
    print()
    print("API keys needed:")
    print("  - Genius: for lyrics")
    print("  - Spotify (optional): for live sync (deferred)")
    print()
    print("Note: audio-feature enrichment (valence/arousal) has no live source —")
    print("      see docs/C3_data_pipeline_spec.md. Clustering stays empty without it.")


if __name__ == "__main__":
    main()
