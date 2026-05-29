from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from orpheus.config import OrpheusConfig

logger = logging.getLogger(__name__)

_PREVALENCE_THRESHOLDS = [
    (0.25, "dominant"),
    (0.15, "high"),
    (0.08, "moderate"),
    (0.03, "present"),
    (0.0, "not represented"),
]


def prevalence_label(score: float) -> str:
    for threshold, label in _PREVALENCE_THRESHOLDS:
        if score > threshold:
            return label
    return "not represented"


def depth_label_from_score(score: float, config: OrpheusConfig) -> str:
    for dl in config.depth_labels:
        if score <= dl.threshold:
            return dl.label
    return config.depth_labels[-1].label


def assemble_report(
    state: dict,
    trait: dict,
    shifts: list[dict],
    co_occurrences: list[dict],
    clusters: list[dict],
    config: OrpheusConfig,
    trends: list[dict] | None = None,
    safety_flags: list[dict] | None = None,
    clusters_status: str = "ok",
    state_co_occurrences: list[dict] | None = None,
    trait_co_occurrences: list[dict] | None = None,
) -> dict:
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_version": config.model_version,
        "windows": {
            "state": _format_window(state, config, co_occurrences=state_co_occurrences),
            "trait": _format_window(trait, config, co_occurrences=trait_co_occurrences),
        },
        "shifts": shifts,
        "trends": trends or [],
        "co_occurrences": co_occurrences,
        "clusters": clusters,
        "clusters_status": clusters_status,
        "safety_flags": safety_flags or [],
    }

    return report


def _format_window(
    window: dict, config: OrpheusConfig, co_occurrences: list[dict] | None = None
) -> dict:
    top_emotions = [
        {"category": cat, "prevalence": prevalence_label(score)}
        for cat, score in sorted(window["emotions"].items(), key=lambda x: x[1], reverse=True)
        if score > 0.03
    ]

    top_themes = [
        {"category": cat, "prevalence": prevalence_label(score)}
        for cat, score in sorted(window["themes"].items(), key=lambda x: x[1], reverse=True)
        if score > 0.03
    ]

    # Enrich top tracks with depth labels
    top_tracks = []
    for t in window.get("top_tracks", [])[:9]:
        depth_score = t.get("depth_score")
        if not isinstance(depth_score, int | float):
            depth_score = 0.5
        top_tracks.append({
            **t,
            "depth_label": depth_label_from_score(float(depth_score), config),
        })

    top_frequency_tracks = [
        dict(t)
        for t in window.get("top_frequency_tracks", [])[:9]
    ]

    return {
        # Numeric proportions (already normalized to sum to 1.0 in aggregation).
        # These are the source of truth for the UI; `top_*` prevalence labels are
        # a coarse 5-bucket summary kept for backward compatibility. Emit the full
        # maps (not just the > 0.03 slice) so the frontend can render real shares
        # and percentage-point deltas instead of quantizing labels back to numbers.
        "emotion": {cat: round(score, 6) for cat, score in window["emotions"].items()},
        "theme": {cat: round(score, 6) for cat, score in window["themes"].items()},
        "top_emotions": top_emotions,
        "top_themes": top_themes,
        "depth_label": depth_label_from_score(window["avg_depth"], config),
        "top_artists": window.get("top_artists", [])[:5],
        "top_tracks": top_tracks,
        "top_frequency_tracks": top_frequency_tracks,
        "from_date": window.get("from_date"),
        "to_date": window.get("to_date"),
        "coverage": window.get("coverage", {"scored_plays": 0, "total_plays": 0, "ratio": 0.0}),
        # Connections scoped to this window's evidence span (see
        # detect_co_occurrences_by_window). Empty when the span has too few
        # distinct played-and-scored tracks for the lift comparison to mean
        # anything — an honest empty state rather than borrowed all-time data.
        "co_occurrences": co_occurrences or [],
    }


def write_report(report: dict, output_path: Path) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False)
    output_path.write_text(content)
    return hashlib.sha256(content.encode()).hexdigest()


def record_run(
    conn: sqlite3.Connection,
    config: OrpheusConfig,
    output_path: Path,
    output_hash: str,
    started_at: datetime,
) -> str:
    run_id = str(uuid.uuid4())
    finished_at = datetime.now(timezone.utc)

    play_count = conn.execute("SELECT COUNT(*) FROM plays").fetchone()[0]
    track_count = conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]

    config_snapshot = json.dumps({
        "windows": {
            "state_half_life_days": config.windows.state_half_life_days,
            "trait_half_life_days": config.windows.trait_half_life_days,
        },
        "engagement_weights": {
            "full_play": config.engagement_weights.full_play,
            "partial_play": config.engagement_weights.partial_play,
            "early_skip": config.engagement_weights.early_skip,
            "boundary_skip": config.engagement_weights.boundary_skip,
            "shuffle_source": config.engagement_weights.shuffle_source,
            "library_play": config.engagement_weights.library_play,
        },
        "clustering": {
            "dbscan_min_pts": config.clustering.dbscan_min_pts,
            "gmm_components": config.clustering.gmm_components,
        },
    }, sort_keys=True)

    model_versions = json.dumps({
        "emotion_classifier": config.models.emotion_classifier,
        "semantic_embedding": config.models.semantic_embedding,
    })

    conn.execute(
        """INSERT INTO pipeline_runs
           (run_id, started_at, finished_at, config_snapshot, model_versions,
            play_count_processed, track_count_processed, output_path, output_hash)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            run_id, started_at.isoformat(), finished_at.isoformat(),
            config_snapshot, model_versions,
            play_count, track_count,
            str(output_path), output_hash,
        ),
    )
    conn.commit()

    return run_id
