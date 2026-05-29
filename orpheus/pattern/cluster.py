from __future__ import annotations

import json
import logging
import sqlite3

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import NearestNeighbors

from orpheus.config import OrpheusConfig
from orpheus.score.emotion import EMOTION_CATEGORIES
from orpheus.score.theme import THEME_CATEGORIES

logger = logging.getLogger(__name__)


def clusters_status(conn: sqlite3.Connection, clusters: list[dict], n_clean_points: int) -> str:
    """Explain why clusters may be empty so the report can degrade honestly."""
    af_count = conn.execute("SELECT COUNT(*) FROM audio_features").fetchone()[0]
    if af_count == 0:
        return "no_audio_features"
    if n_clean_points == 0:
        return "insufficient_audio_data"
    if not clusters:
        return "no_clusters_found"
    return "ok"


_QUALIFIED_LISTEN_MS = 30_000


def _qualified_play_counts(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        """SELECT track_uri, COUNT(*) AS n
           FROM plays
           WHERE COALESCE(ms_played, 0) >= ?
           GROUP BY track_uri""",
        (_QUALIFIED_LISTEN_MS,),
    ).fetchall()
    return {row["track_uri"]: row["n"] for row in rows}


def _load_avd_data(conn: sqlite3.Connection) -> tuple[np.ndarray, list[dict]]:
    rows = conn.execute(
        """SELECT ts.track_uri, ts.emotion_scores, ts.theme_scores, ts.depth_score,
                  af.valence, af.arousal
           FROM track_scores ts
           JOIN audio_features af ON ts.track_uri = af.track_uri"""
    ).fetchall()

    play_counts = _qualified_play_counts(conn)

    tracks = []
    points = []
    for row in rows:
        v = row["valence"]
        a = row["arousal"]
        d = row["depth_score"]
        if v is None or a is None or d is None:
            continue
        points.append([v, a, d])
        tracks.append({
            "track_uri": row["track_uri"],
            "emotion_scores": json.loads(row["emotion_scores"]),
            "theme_scores": json.loads(row["theme_scores"]),
            "depth_score": d,
            # Qualified plays — used to express cluster prominence as a share of
            # listening rather than a share of the catalog.
            "play_count": play_counts.get(row["track_uri"], 0),
        })

    return np.array(points) if points else np.empty((0, 3)), tracks


def _auto_epsilon(points: np.ndarray, min_pts: int) -> float:
    if len(points) < min_pts + 1:
        return 0.5

    nn = NearestNeighbors(n_neighbors=min_pts)
    nn.fit(points)
    distances, _ = nn.kneighbors(points)
    k_distances = np.sort(distances[:, -1])

    diffs = np.diff(k_distances)
    if len(diffs) == 0:
        return float(np.median(k_distances))

    elbow_idx = np.argmax(diffs) + 1
    return float(k_distances[elbow_idx])


def filter_noise(
    conn: sqlite3.Connection,
    config: OrpheusConfig,
) -> tuple[np.ndarray, list[dict], int]:
    points, tracks = _load_avd_data(conn)

    if len(points) < config.clustering.dbscan_min_pts:
        return points, tracks, 0

    eps = _auto_epsilon(points, config.clustering.dbscan_min_pts)
    db = DBSCAN(eps=eps, min_samples=config.clustering.dbscan_min_pts)
    labels = db.fit_predict(points)

    core_mask = labels != -1
    noise_count = int(np.sum(~core_mask))

    return points[core_mask], [t for t, m in zip(tracks, core_mask) if m], noise_count


def cluster_gmm(
    points: np.ndarray,
    tracks: list[dict],
    config: OrpheusConfig,
    seed: int = 42,
) -> list[dict]:
    n_components = min(config.clustering.gmm_components, len(points))
    if n_components < 1 or len(points) < n_components:
        return []

    gmm = GaussianMixture(n_components=n_components, random_state=seed)
    gmm.fit(points)
    probs = gmm.predict_proba(points)

    # Play counts weight membership so cluster prominence and mood reflect how
    # much each track was actually listened to, not just how many tracks fall in
    # the region. Tracks never played still shape the GMM fit but contribute no
    # listening share.
    play_counts = np.array([max(t.get("play_count", 0), 0) for t in tracks], dtype=float)
    total_listening = float(play_counts.sum())

    clusters = []
    for k in range(n_components):
        member_weights = probs[:, k]
        listen_weights = member_weights * play_counts
        centroid = gmm.means_[k].tolist()

        emotion_agg = {cat: 0.0 for cat in EMOTION_CATEGORIES}
        theme_agg = {cat: 0.0 for cat in THEME_CATEGORIES}
        total_w = 0.0

        for i, lw in enumerate(listen_weights):
            if member_weights[i] < 0.1 or lw <= 0:
                continue
            for cat in EMOTION_CATEGORIES:
                emotion_agg[cat] += lw * tracks[i]["emotion_scores"].get(cat, 0.0)
            for cat in THEME_CATEGORIES:
                theme_agg[cat] += lw * tracks[i]["theme_scores"].get(cat, 0.0)
            total_w += lw

        if total_w > 0:
            emotion_agg = {k: v / total_w for k, v in emotion_agg.items()}
            theme_agg = {k: v / total_w for k, v in theme_agg.items()}

        dom_emotions = sorted(emotion_agg.items(), key=lambda x: x[1], reverse=True)[:3]
        dom_themes = sorted(theme_agg.items(), key=lambda x: x[1], reverse=True)[:3]

        # True share of listening: this cluster's play-weighted membership over
        # all listening. Memberships sum to 1 per track, so shares sum to ~100%.
        share = float(listen_weights.sum() / total_listening) if total_listening > 0 else 0.0
        label = _label_cluster(centroid)

        clusters.append({
            "label": label,
            "centroid_avd": [round(c, 3) for c in centroid],
            "dominant_emotions": [{"category": c, "weight": round(w, 3)} for c, w in dom_emotions],
            "dominant_themes": [{"category": c, "weight": round(w, 3)} for c, w in dom_themes],
            "share_of_listening": f"approximately {int(round(share * 100))}%",
            "track_count": int(np.sum(member_weights > 0.3)),
        })

    return clusters


def _label_cluster(centroid: list[float]) -> str:
    v, a, d = centroid
    if v > 0.6 and a > 0.5:
        return "energetic bright"
    if v > 0.6 and a < 0.4:
        return "serene core"
    if v < 0.4 and d > 0.6:
        return "introspective core"
    if v < 0.4 and a > 0.5:
        return "intense dark"
    if d > 0.6:
        return "deep reflective"
    return "balanced middle"
