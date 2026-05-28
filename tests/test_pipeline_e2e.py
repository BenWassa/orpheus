"""End-to-end integration test for the full Orpheus pipeline.

Uses synthetic data and mocked scoring (no transformer model loading).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone


from orpheus.aggregate.windows import compute_state_and_trait
from orpheus.config import load_config
from orpheus.db import ensure_schema, get_db
from orpheus.ingest.spotify_export import ingest_export
from orpheus.output.assemble import assemble_report, record_run, write_report
from orpheus.pattern.cluster import cluster_gmm, filter_noise
from orpheus.pattern.trends import compare_state_trait, detect_co_occurrences, detect_trends
from orpheus.safety.rumination import check_rumination
from orpheus.score.emotion import EMOTION_CATEGORIES
from orpheus.score.theme import THEME_CATEGORIES


def _insert_synthetic_enrichment(conn, track_uris):
    """Insert synthetic audio features and lyrics for test tracks."""
    import random
    random.seed(42)

    for i, uri in enumerate(track_uris):
        v = random.random()
        a = random.random()
        conn.execute(
            """INSERT OR IGNORE INTO audio_features
               (track_uri, source, valence, arousal, tempo, key, mode, energy,
                danceability, acousticness, instrumentalness, loudness,
                spectral_centroid, spectral_complexity, fetched_at)
               VALUES (?, 'synthetic', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (uri, v, a, 120 + i * 5, i % 12, i % 2,
             a * 0.9, random.random(), random.random(), 0.0,
             -5.0 - i, None, random.random(),
             datetime.now(timezone.utc).isoformat()),
        )

        words = ["love", "heart", "pain", "light", "dark", "running", "fire",
                 "away", "home", "dream", "night", "soul", "break", "free"]
        lyrics = " ".join(random.choices(words, k=50))
        conn.execute(
            """INSERT OR IGNORE INTO lyrics
               (track_uri, raw_text, cleaned_text, has_lyrics, fetched_at)
               VALUES (?, ?, ?, ?, ?)""",
            (uri, lyrics, lyrics, True, datetime.now(timezone.utc).isoformat()),
        )

        conn.execute(
            "UPDATE tracks SET enriched_at = ? WHERE track_uri = ?",
            (datetime.now(timezone.utc).isoformat(), uri),
        )

    conn.commit()


def _insert_synthetic_scores(conn, track_uris, model_version):
    """Insert synthetic scores bypassing transformer models."""
    import random
    random.seed(42)

    for uri in track_uris:
        emotion_scores = {cat: random.random() for cat in EMOTION_CATEGORIES}
        total = sum(emotion_scores.values())
        emotion_scores = {k: v / total for k, v in emotion_scores.items()}

        theme_scores = {cat: random.random() for cat in THEME_CATEGORIES}
        total = sum(theme_scores.values())
        theme_scores = {k: v / total for k, v in theme_scores.items()}

        depth_score = random.random()
        depth_label = "surface" if depth_score < 0.33 else "engaged" if depth_score < 0.66 else "immersive"

        conn.execute(
            """INSERT OR REPLACE INTO track_scores
               (track_uri, model_version, emotion_scores, theme_scores,
                depth_score, depth_label, confidence, scored_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                uri, model_version,
                json.dumps(emotion_scores), json.dumps(theme_scores),
                depth_score, depth_label,
                json.dumps({"emotion": 0.8, "theme": 0.7, "depth": 0.6}),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    conn.commit()


def test_full_pipeline_e2e(tmp_project, sample_export_path):
    """Run the full pipeline on synthetic data and verify output structure."""
    cfg = load_config(project_root=tmp_project)
    conn = get_db(cfg.db_path)
    ensure_schema(conn)

    # Step 1: Ingest
    stats = ingest_export(sample_export_path, conn)
    assert stats["plays_inserted"] > 0

    track_uris = [r["track_uri"] for r in conn.execute("SELECT track_uri FROM tracks").fetchall()]
    assert len(track_uris) > 0

    # Step 2: Synthetic enrichment (skip real API calls)
    _insert_synthetic_enrichment(conn, track_uris)

    # Step 3: Synthetic scoring (skip transformer loading)
    _insert_synthetic_scores(conn, track_uris, cfg.model_version)

    # Step 4: Aggregation
    windows = compute_state_and_trait(conn, cfg)
    assert "state" in windows
    assert "trait" in windows
    assert len(windows["state"]["emotions"]) == len(EMOTION_CATEGORIES)

    # Step 5: Pattern detection
    clean_points, clean_tracks, noise_count = filter_noise(conn, cfg)
    clusters = cluster_gmm(clean_points, clean_tracks, cfg) if len(clean_points) > 0 else []

    trends = detect_trends(conn)
    co_occurrences = detect_co_occurrences(conn)
    shifts = compare_state_trait(windows["state"], windows["trait"])

    # Step 6: Safety check
    safety_flags = check_rumination(windows["state"], cfg)
    assert safety_flags == []  # safety.active=false in template

    # Step 7: Output assembly
    report_data = assemble_report(
        state=windows["state"], trait=windows["trait"],
        shifts=shifts, trends=trends, co_occurrences=co_occurrences,
        clusters=clusters, config=cfg, safety_flags=safety_flags,
    )

    # Verify report structure per C2 schema
    assert "generated_at" in report_data
    assert "model_version" in report_data
    assert "windows" in report_data
    assert "state" in report_data["windows"]
    assert "trait" in report_data["windows"]

    state_window = report_data["windows"]["state"]
    assert "top_emotions" in state_window
    assert "top_themes" in state_window
    assert "depth_label" in state_window
    assert state_window["depth_label"] in ("surface", "engaged", "immersive")

    for e in state_window["top_emotions"]:
        assert "category" in e
        assert "prevalence" in e
        assert e["prevalence"] in ("dominant", "high", "moderate", "present", "not represented")

    assert "shifts" in report_data
    assert "co_occurrences" in report_data
    assert "clusters" in report_data
    assert "safety_flags" in report_data

    # Step 8: Write report
    output_path = cfg.reports_dir / "test_report.json"
    output_hash = write_report(report_data, output_path)
    assert output_path.exists()
    assert len(output_hash) == 64  # SHA-256

    # Step 9: Record run
    started_at = datetime.now(timezone.utc)
    run_id = record_run(conn, cfg, output_path, output_hash, started_at)
    assert run_id

    last_run = conn.execute(
        "SELECT * FROM pipeline_runs WHERE run_id = ?", (run_id,)
    ).fetchone()
    assert last_run is not None
    assert last_run["output_hash"] == output_hash

    # Verify the written JSON is valid
    written = json.loads(output_path.read_text())
    assert written["model_version"] == cfg.model_version

    conn.close()
