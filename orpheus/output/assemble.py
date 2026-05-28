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
) -> dict:
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_version": config.model_version,
        "windows": {
            "state": _format_window(state, config),
            "trait": _format_window(trait, config),
        },
        "shifts": shifts,
        "trends": trends or [],
        "co_occurrences": co_occurrences,
        "clusters": clusters,
        "safety_flags": safety_flags or [],
    }

    return report


def _format_window(window: dict, config: OrpheusConfig) -> dict:
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

    return {
        "top_emotions": top_emotions,
        "top_themes": top_themes,
        "depth_label": depth_label_from_score(window["avg_depth"], config),
        "top_artists": window.get("top_artists", [])[:5],
        "top_tracks": window.get("top_tracks", [])[:5],
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
            "repeat_session": config.engagement_weights.repeat_session,
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
