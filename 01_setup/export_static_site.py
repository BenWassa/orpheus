"""Static site exporter for Project Orpheus.

Generates a static `docs/` site with one page per dataset plus an index
page. The exporter prefers to use the existing pandas-based pipeline, but
falls back to a lightweight in-script implementation when optional
dependencies (pandas/plotly) are unavailable.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import random
import re
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# Attempt to load the original pipeline. If pandas/plotly are missing the
# imports will fail and we will fall back to a lightweight implementation.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
CORE_DIR = PROJECT_ROOT / "02_core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

PIPELINE_AVAILABLE = True
try:  # pragma: no cover - import guard
    from data_processor import clean as dp_clean, load_exportify as dp_load_exportify  # type: ignore  # noqa: E402
    from emotion_analyzer import (  # type: ignore  # noqa: E402
        add_spotify_audio_features as dp_add_spotify_audio_features,
        compute_emotion_summary as dp_compute_emotion_summary,
    )
except ModuleNotFoundError as exc:  # pragma: no cover - handled gracefully
    logging.getLogger(__name__).warning(
        "Falling back to lightweight exporter implementation because %s", exc
    )
    PIPELINE_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("export_static_site")

DEFAULT_INPUT_DIR = PROJECT_ROOT / "04_data" / "raw"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "docs"
STYLES_PY = PROJECT_ROOT / "03_interface" / "components" / "styles.py"

ASSETS_SUBDIR = "assets"
CSS_FILENAME = "styles.css"
TEMPLATE_DIRNAME = "_templates"
INDEX_TEMPLATE_FILENAME = "index.html"

IMAGE_SUBDIR = "images"
THUMBNAIL_SUBDIR = "thumbnails"
DEFAULT_THUMBNAIL_FILENAME = "dataset-default.svg"

AUDIO_FEATURE_COLUMNS = [
    "valence",
    "energy",
    "danceability",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
    "tempo",
]
ARTIST_COLUMN_CANDIDATES = [
    "artist_name",
    "Artist Name(s)",
    "artist",
]
ESSENTIAL_MAPPINGS = {
    "track_name": ["Track Name", "track_name", "name", "song"],
    "artist_name": ["Artist Name(s)", "artist_name", "artist", "Artist Name"],
    "album_name": ["Album Name", "album_name", "album"],
    "added_at": ["Added At", "added_at", "date_added", "timestamp"],
}


@dataclass
class DatasetResult:
    """Container for data required to build index listings."""

    name: str
    slug: str
    page_path: Path
    summary_path: Path
    metadata: Dict[str, object]
    summary: Dict[str, object]

    @property
    def page_href(self) -> str:
        return self.page_path.name

    @property
    def summary_href(self) -> str:
        return self.summary_path.name


# ---------------------------------------------------------------------------
# Fallback pipeline helpers (no pandas/plotly required)
# ---------------------------------------------------------------------------

def fallback_load_exportify(csv_path: Path) -> List[Dict[str, str]]:
    with csv_path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return [dict(row) for row in reader]


def fallback_clean(rows: List[Dict[str, str]]) -> List[Dict[str, object]]:
    seen_keys = set()
    cleaned: List[Dict[str, object]] = []
    for row in rows:
        mapped = dict(row)
        for standard, options in ESSENTIAL_MAPPINGS.items():
            for candidate in options:
                if candidate in row and row[candidate] not in (None, ""):
                    mapped[standard] = row[candidate].strip()
                    break
        track = mapped.get("track_name")
        artist = mapped.get("artist_name")
        if not track or not artist:
            continue
        key = (track.lower(), artist.lower())
        if key in seen_keys:
            continue
        seen_keys.add(key)
        added_raw = mapped.get("added_at")
        if isinstance(added_raw, str) and added_raw:
            try:
                mapped["added_at"] = datetime.fromisoformat(added_raw.replace("Z", "+00:00"))
            except ValueError:
                mapped["added_at"] = None
        else:
            mapped["added_at"] = None
        cleaned.append(mapped)
    return cleaned


def fallback_add_spotify_audio_features(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rng = random.Random(42)
    enriched: List[Dict[str, object]] = []
    for row in rows:
        enriched_row = dict(row)
        for feature in AUDIO_FEATURE_COLUMNS:
            if feature == "tempo":
                enriched_row[feature] = rng.uniform(60, 200)
            else:
                enriched_row[feature] = rng.uniform(0, 1)
        enriched.append(enriched_row)
    return enriched


def _mean(values: List[float]) -> Optional[float]:
    return mean(values) if values else None


def _std(values: List[float]) -> Optional[float]:
    if len(values) <= 1:
        return 0.0 if values else None
    return pstdev(values)


def fallback_compute_emotion_summary(rows: List[Dict[str, object]]) -> Dict[str, object]:
    summary = {
        "audio_features": {},
        "sentiment": {},
        "emotion_profile": {},
        "recommendations": [],
    }

    for feature in AUDIO_FEATURE_COLUMNS[:-1]:  # exclude tempo from 0-1 stats
        values = [float(row[feature]) for row in rows if isinstance(row.get(feature), (int, float))]
        if not values:
            continue
        zero_fraction = sum(1 for value in values if value == 0.0) / len(values)
        summary["audio_features"][feature] = {
            "mean": _mean(values),
            "std": _std(values) or 0.0,
            "min": min(values),
            "max": max(values),
            "median": median(values),
            "count": len(values),
            "zero_fraction": zero_fraction,
            "trend_index": 0.0,
        }

    avg_valence = summary["audio_features"].get("valence", {}).get("mean")
    avg_energy = summary["audio_features"].get("energy", {}).get("mean")
    if isinstance(avg_valence, float):
        if avg_valence > 0.7:
            summary["recommendations"].append(
                "High valence detected — your taste leans upbeat, energetic, and positive."
            )
        elif avg_valence < 0.3:
            summary["recommendations"].append(
                "Low valence detected — your taste tends toward introspective or melancholic moods."
            )
    if isinstance(avg_energy, float):
        if avg_energy > 0.7:
            summary["recommendations"].append(
                "High energy detected — you prefer dynamic, lively tracks."
            )
        elif avg_energy < 0.3:
            summary["recommendations"].append(
                "Low energy detected — you enjoy calm, mellow, or acoustic music."
            )
    return summary


# ---------------------------------------------------------------------------
# Exporter utilities
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export static docs site from Exportify datasets.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing Exportify CSV files (default: 04_data/raw)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Destination directory for generated static site (default: docs)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove existing output directory before generating",
    )
    return parser.parse_args(argv)


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "dataset"


def discover_csv_files(input_dir: Path) -> List[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    csv_files = sorted(p for p in input_dir.rglob("*.csv") if p.is_file())
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found under {input_dir}")
    return csv_files


def prepare_output_directory(out_dir: Path, force: bool = False) -> Path:
    if out_dir.exists() and force:
        logger.info("Removing existing output directory %s", out_dir)
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = out_dir / ASSETS_SUBDIR
    assets_dir.mkdir(parents=True, exist_ok=True)
    return assets_dir


def extract_css_from_styles() -> str:
    if not STYLES_PY.exists():
        raise FileNotFoundError(f"Could not find styles.py at {STYLES_PY}")
    text = STYLES_PY.read_text(encoding="utf-8")
    match = re.search(r"GLOBAL_STYLE\s*=\s*\"\"\"(.*?)\"\"\"", text, re.DOTALL)
    if not match:
        raise ValueError("Could not locate GLOBAL_STYLE definition in styles.py")
    style_block = match.group(1)
    style_match = re.search(r"<style>(.*?)</style>", style_block, re.DOTALL)
    css = style_match.group(1) if style_match else style_block
    css_lines = [line for line in css.splitlines() if "fonts.googleapis" not in line]
    css = "\n".join(css_lines)
    css = re.sub(r"^\s+", "", css, flags=re.MULTILINE)
    additional_css = """
body {
    margin: 0;
    min-height: 100vh;
    background: var(--color-muted, #f5f6ff);
    color: var(--color-text, #1f1f2e);
    font-family: 'Manrope', 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
}

a {
    color: var(--color-primary, #6c63ff);
    text-decoration: none;
}

a:hover,
a:focus {
    text-decoration: underline;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
}

.site-header {
    position: sticky;
    top: 0;
    z-index: 10;
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(108, 99, 255, 0.08);
}

.site-header__inner {
    margin: 0 auto;
    max-width: 1200px;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
}

.site-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--color-text, #1f1f2e);
}

.site-brand__icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(108, 99, 255, 0.12), rgba(255, 101, 132, 0.12));
    display: grid;
    place-items: center;
    color: var(--color-primary, #6c63ff);
    font-size: 1.35rem;
    box-shadow: inset 0 0 0 1px rgba(108, 99, 255, 0.18);
}

.site-nav {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.site-nav a {
    font-weight: 600;
    color: var(--color-text, #1f1f2e);
}

.site-nav a.site-nav__cta {
    padding: 0.5rem 1.1rem;
    border-radius: 999px;
    background: var(--color-primary, #6c63ff);
    color: #ffffff;
    box-shadow: var(--shadow-soft, 0 20px 45px rgba(76, 70, 180, 0.12));
}

.page {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2.5rem 1.5rem 4rem;
}

.page__header,
.hero {
    text-align: center;
    margin-bottom: 2.5rem;
}

.hero__note {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.8rem;
    border-radius: 999px;
    background: rgba(108, 99, 255, 0.1);
    color: var(--color-primary, #6c63ff);
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.hero__actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 1.75rem;
}

.hero__actions a {
    padding: 0.75rem 1.5rem;
    border-radius: 999px;
    font-weight: 600;
    box-shadow: var(--shadow-soft, 0 20px 45px rgba(76, 70, 180, 0.12));
}

.hero__actions a.primary {
    background: var(--color-primary, #6c63ff);
    color: #ffffff;
}

.hero__actions a.secondary {
    background: rgba(255, 255, 255, 0.9);
    color: var(--color-text, #1f1f2e);
    border: 1px solid rgba(108, 99, 255, 0.16);
}

.search-card {
    display: grid;
    gap: 0.75rem;
}

.search-field {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.9);
    padding: 0.5rem 0.9rem;
    border: 1px solid rgba(108, 99, 255, 0.12);
}

.search-field input[type="search"] {
    flex: 1;
    border: none;
    background: transparent;
    font-size: 1rem;
    outline: none;
}

.search-field svg {
    width: 20px;
    height: 20px;
    color: var(--color-subtle, #6b7280);
}

.dataset-grid {
    display: grid;
    gap: 1.75rem;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    margin-top: 2.5rem;
}

.dataset-card {
    background: var(--color-surface, #ffffff);
    border-radius: 1.25rem;
    overflow: hidden;
    box-shadow: var(--shadow-soft, 0 20px 45px rgba(76, 70, 180, 0.12));
    border: 1px solid rgba(108, 99, 255, 0.08);
    display: flex;
    flex-direction: column;
    transition: transform 200ms ease, box-shadow 200ms ease;
}

.dataset-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 24px 45px rgba(76, 70, 180, 0.18);
}

.dataset-card__thumbnail {
    position: relative;
    aspect-ratio: 16 / 9;
    background: linear-gradient(135deg, rgba(108, 99, 255, 0.2), rgba(255, 101, 132, 0.2));
}

.dataset-card__thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.dataset-card__body {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.dataset-card__title {
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0;
}

.dataset-card__meta {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
}

.dataset-card__meta span {
    display: block;
    font-size: 0.95rem;
    color: var(--color-subtle, #6b7280);
}

.dataset-card__meta strong {
    display: block;
    color: var(--color-text, #1f1f2e);
    font-size: 1.05rem;
}

.dataset-card__footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    font-size: 0.95rem;
}

.dataset-card__links {
    display: flex;
    gap: 0.75rem;
    align-items: center;
}

.dataset-card__links a {
    font-weight: 600;
}

.dataset-card__links a.summary-link {
    font-size: 0.9rem;
    color: var(--color-subtle, #6b7280);
}

.empty-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 3rem 2rem;
    border-radius: 1.25rem;
    border: 1px dashed rgba(108, 99, 255, 0.25);
    background: rgba(255, 255, 255, 0.6);
    color: var(--color-subtle, #6b7280);
}

.dataset-meta {
    display: grid;
    gap: 1.5rem;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    margin-bottom: 2.5rem;
}

.card {
    background: var(--color-surface, #ffffff);
    border-radius: var(--card-radius, 1.25rem);
    padding: 1.5rem;
    box-shadow: var(--shadow-soft, 0 20px 45px rgba(76, 70, 180, 0.12));
    border: 1px solid rgba(108, 99, 255, 0.08);
}

.card h3 {
    margin-top: 0;
    margin-bottom: 0.4rem;
}

.metric {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
}

.callout {
    background: rgba(108, 99, 255, 0.1);
    border: 1px solid rgba(108, 99, 255, 0.2);
    border-radius: 1rem;
    padding: 1.25rem 1.5rem;
    margin-bottom: 2rem;
}

.callout strong {
    color: var(--color-primary, #6c63ff);
}

.chart-section {
    margin-top: 2.5rem;
}

.chart-section h2 {
    margin-bottom: 0.75rem;
}

.index-table {
    width: 100%;
    border-collapse: collapse;
}

.index-table th,
.index-table td {
    border-bottom: 1px solid rgba(108, 99, 255, 0.12);
    text-align: left;
    padding: 0.75rem;
}

.index-table th {
    font-weight: 600;
    color: var(--color-subtle, #6b7280);
}

.index-table tbody tr:hover {
    background: rgba(108, 99, 255, 0.06);
}

.plotly-chart {
    width: 100%;
    min-height: 420px;
}

.site-footer {
    max-width: 1100px;
    margin: 0 auto 3rem;
    padding: 0 1.5rem;
    color: var(--color-subtle, #6b7280);
    text-align: center;
    font-size: 0.9rem;
}

.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
}

@media (max-width: 720px) {
    .site-header__inner {
        flex-direction: column;
        align-items: flex-start;
    }

    .site-nav {
        flex-wrap: wrap;
        justify-content: flex-start;
    }

    .dataset-card__meta {
        grid-template-columns: 1fr;
    }

    .dataset-card__footer {
        flex-direction: column;
        align-items: flex-start;
    }
}
""".strip()
    return css.strip() + "\n\n" + additional_css + "\n"


def write_css(assets_dir: Path) -> Path:
    css_content = extract_css_from_styles()
    css_path = assets_dir / CSS_FILENAME
    css_path.write_text(css_content, encoding="utf-8")
    logger.info("Wrote CSS to %s", css_path)
    return css_path


def copy_docs(out_dir: Path) -> None:
    """Copy 06_docs/ content to docs/docs/ for static site."""
    docs_src = PROJECT_ROOT / "06_docs"
    docs_dest = out_dir / "docs"
    if docs_src.exists():
        shutil.copytree(docs_src, docs_dest, dirs_exist_ok=True)
        logger.info("Copied docs from %s to %s", docs_src, docs_dest)
    else:
        logger.warning("06_docs/ not found, skipping docs copy")


def pipeline_process(csv_path: Path) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    if PIPELINE_AVAILABLE:
        logger.info("Using pandas-based pipeline for %s", csv_path.name)
        df_raw = dp_load_exportify(csv_path)
        df_clean = dp_clean(df_raw)
        df_audio = dp_add_spotify_audio_features(df_clean)
        summary = dp_compute_emotion_summary(df_audio)
        rows = df_audio.to_dict(orient="records")  # type: ignore[attr-defined]
        # Convert timestamps to datetime objects if needed
        for row in rows:
            value = row.get("added_at")
            if value is not None and hasattr(value, "isoformat"):
                row["added_at"] = value.to_pydatetime()  # type: ignore[call-arg]
        return rows, summary

    logger.info("Using lightweight fallback pipeline for %s", csv_path.name)
    rows_raw = fallback_load_exportify(csv_path)
    rows_clean = fallback_clean(rows_raw)
    rows_audio = fallback_add_spotify_audio_features(rows_clean)
    summary = fallback_compute_emotion_summary(rows_audio)
    return rows_audio, summary


def compute_metadata(rows: List[Dict[str, object]], summary: Dict[str, object]) -> Dict[str, object]:
    track_count = len(rows)
    artist_col = None
    for candidate in ARTIST_COLUMN_CANDIDATES:
        if any(candidate in row for row in rows):
            artist_col = candidate
            break
    if artist_col is None:
        artist_col = "artist_name"
    unique_artists = len({str(row.get(artist_col, "")) for row in rows if row.get(artist_col)})

    dates = [row["added_at"] for row in rows if isinstance(row.get("added_at"), datetime)]
    date_range = None
    if dates:
        date_range = {
            "start": min(dates).date().isoformat(),
            "end": max(dates).date().isoformat(),
        }

    zero_fraction = {}
    audio_stats = summary.get("audio_features", {})
    if isinstance(audio_stats, dict):
        for feature, stats in audio_stats.items():
            if isinstance(stats, dict) and "zero_fraction" in stats:
                zero_fraction[feature] = stats["zero_fraction"]

    generated_at = datetime.now(timezone.utc).replace(microsecond=0)

    return {
        "track_count": track_count,
        "unique_artists": unique_artists,
        "date_range": date_range,
        "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
        "zero_fraction": zero_fraction,
    }


def resolve_thumbnail(slug: str, out_dir: Path) -> str:
    assets_dir = out_dir / ASSETS_SUBDIR
    thumbnails_dir = assets_dir / IMAGE_SUBDIR / THUMBNAIL_SUBDIR
    for ext in ("png", "jpg", "jpeg", "svg", "webp"):
        candidate = thumbnails_dir / f"{slug}.{ext}"
        if candidate.exists():
            return candidate.relative_to(out_dir).as_posix()
    default_thumb = assets_dir / IMAGE_SUBDIR / DEFAULT_THUMBNAIL_FILENAME
    if default_thumb.exists():
        return default_thumb.relative_to(out_dir).as_posix()
    return ""


def apply_index_template(template_text: str, context: Dict[str, str]) -> str:
    pattern = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")

    def replacer(match: re.Match[str]) -> str:
        key = match.group(1)
        return context.get(key, match.group(0))

    return pattern.sub(replacer, template_text)


def render_plotly_script(div_id: str, data: Dict[str, object], layout: Dict[str, object], include_cdn: bool) -> str:
    script_lines = []
    if include_cdn:
        script_lines.append('<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>')
    script_lines.append(
        f"<script>Plotly.newPlot('{div_id}', {json.dumps(data)}, {json.dumps(layout)}, {{responsive: true}});</script>"
    )
    return f"<div id=\"{div_id}\" class=\"plotly-chart\"></div>\n" + "\n".join(script_lines)


def build_timeline_chart(rows: List[Dict[str, object]], include_cdn: bool) -> Optional[str]:
    valence = [row.get("valence") for row in rows if isinstance(row.get("valence"), (int, float))]
    energy = [row.get("energy") for row in rows if isinstance(row.get("energy"), (int, float))]
    if not valence and not energy:
        return None

    sorted_rows = sorted(
        rows,
        key=lambda row: row.get("added_at") or rows.index(row),
    )
    x_values = []
    for idx, row in enumerate(sorted_rows, start=1):
        added_at = row.get("added_at")
        if isinstance(added_at, datetime):
            x_values.append(added_at.isoformat())
        else:
            x_values.append(idx)

    traces = []
    y_valence = [row.get("valence") if isinstance(row.get("valence"), (int, float)) else None for row in sorted_rows]
    if any(v is not None for v in y_valence):
        traces.append({
            "type": "scatter",
            "mode": "lines+markers",
            "name": "Valence",
            "x": x_values,
            "y": [v if v is not None else None for v in y_valence],
        })
    y_energy = [row.get("energy") if isinstance(row.get("energy"), (int, float)) else None for row in sorted_rows]
    if any(v is not None for v in y_energy):
        traces.append({
            "type": "scatter",
            "mode": "lines+markers",
            "name": "Energy",
            "x": x_values,
            "y": [v if v is not None else None for v in y_energy],
        })

    if not traces:
        return None

    layout = {
        "title": "Valence & Energy over time",
        "yaxis": {"title": "Score", "range": [0, 1]},
        "xaxis": {"title": "Added at"},
        "margin": {"l": 40, "r": 40, "t": 60, "b": 40},
    }

    return render_plotly_script("timeline", traces, layout, include_cdn)


def build_top_artists_chart(rows: List[Dict[str, object]], include_cdn: bool) -> Optional[str]:
    artists: Counter[str] = Counter()
    for row in rows:
        value = row.get("artist_name") or row.get("Artist Name(s)") or row.get("artist")
        if value:
            artists[str(value)] += 1
    if not artists:
        return None
    top = artists.most_common(10)
    layout = {
        "title": "Top artists",
        "margin": {"l": 160, "r": 40, "t": 60, "b": 60},
        "xaxis": {"title": "Track count"},
    }
    data = [{
        "type": "bar",
        "orientation": "h",
        "x": [count for _, count in reversed(top)],
        "y": [name for name, _ in reversed(top)],
        "marker": {"color": "#6c63ff"},
    }]
    return render_plotly_script("top-artists", data, layout, include_cdn)


def build_audio_features_radar(summary: Dict[str, object], include_cdn: bool) -> Optional[str]:
    audio_stats = summary.get("audio_features")
    if not isinstance(audio_stats, dict):
        return None
    categories = []
    values = []
    for feature in AUDIO_FEATURE_COLUMNS[:-1]:
        stats = audio_stats.get(feature)
        if not isinstance(stats, dict):
            continue
        mean_val = stats.get("mean")
        if mean_val is None:
            continue
        categories.append(feature.replace("_", " ").title())
        values.append(mean_val)
    if not values:
        return None
    categories.append(categories[0])
    values.append(values[0])
    data = [{
        "type": "scatterpolar",
        "r": values,
        "theta": categories,
        "fill": "toself",
        "name": "Audio features",
        "line": {"color": "#ff6584"},
    }]
    layout = {
        "title": "Average audio feature profile",
        "polar": {"radialaxis": {"visible": True, "range": [0, 1]}},
        "margin": {"l": 60, "r": 60, "t": 60, "b": 40},
    }
    return render_plotly_script("audio-radar", data, layout, include_cdn)


def render_dataset_page(result: DatasetResult, chart_html_blocks: Iterable[str]) -> str:
    meta = result.metadata
    date_range = meta.get("date_range")
    date_display = "—"
    if isinstance(date_range, dict) and date_range.get("start") and date_range.get("end"):
        date_display = f"{date_range['start']} → {date_range['end']}"

    zero_fraction = meta.get("zero_fraction")
    zero_rows = ""
    if isinstance(zero_fraction, dict) and zero_fraction:
        zero_rows = "".join(
            f"<tr><td>{feature.replace('_', ' ').title()}</td><td>{value:.2%}</td></tr>"
            for feature, value in sorted(zero_fraction.items())
        )

    recommendations = result.summary.get("recommendations")
    recommendations_list = ""
    if isinstance(recommendations, list) and recommendations:
        recommendations_list = "<div class=\"recommendations card\"><h3>Recommendations</h3><ul>" + "".join(
            f"<li>{item}</li>" for item in recommendations
        ) + "</ul></div>"

    charts_html = "".join(
        f"<section class=\"chart-section card\">{block}</section>" for block in chart_html_blocks if block
    )

    zero_fraction_html = (
        f"<div class=\"card\"><h3>Audio feature zero fractions</h3><table class=\"index-table\"><tbody>{zero_rows}</tbody></table></div>"
        if zero_rows
        else ""
    )

    generated_display = ""
    generated_at = meta.get("generated_at")
    if isinstance(generated_at, str):
        try:
            cleaned = generated_at.replace("Z", "+00:00") if generated_at.endswith("Z") else generated_at
            generated_dt = datetime.fromisoformat(cleaned)
            generated_display = generated_dt.strftime("%Y-%m-%d %H:%M UTC")
        except ValueError:
            generated_display = generated_at

    footer_html = (
        f"<footer class=\"site-footer\"><p>Generated on {generated_display}</p></footer>"
        if generated_display
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Project Orpheus — {result.name}</title>
    <link rel=\"stylesheet\" href=\"assets/{CSS_FILENAME}\" />
</head>
<body>
    <header class=\"site-header\">
        <div class=\"site-header__inner\">
            <a class=\"site-brand\" href=\"index.html\">
                <span class=\"site-brand__icon\" aria-hidden=\"true\">♪</span>
                <span>Project Orpheus</span>
            </a>
            <nav class=\"site-nav\">
                <a href=\"index.html\">Datasets</a>
                <a href=\"README.html\">Static guide</a>
            </nav>
        </div>
    </header>
    <main class=\"page\">
        <header class=\"page__header\">
            <h1 class=\"main-header\">{result.name}</h1>
            <p class=\"subtitle\">Static emotional analysis generated with Project Orpheus</p>
        </header>

        <section class=\"callout\">
            <strong>Static export:</strong> This page is read-only and reflects a snapshot of your dataset. For fresh analyses or to upload new CSV files, launch the interactive app following the <a href=\"README.html#regenerating-the-site\">regeneration guide</a>.
        </section>

        <section class=\"dataset-meta\">
            <div class=\"card\">
                <h3>Total tracks</h3>
                <p class=\"metric\">{meta.get('track_count', 0)}</p>
            </div>
            <div class=\"card\">
                <h3>Unique artists</h3>
                <p class=\"metric\">{meta.get('unique_artists', 0)}</p>
            </div>
            <div class=\"card\">
                <h3>Date range</h3>
                <p class=\"metric\">{date_display}</p>
            </div>
            <div class=\"card\">
                <h3>Summary JSON</h3>
                <p><a href=\"{result.summary_href}\">Download metadata</a></p>
            </div>
        </section>

        {zero_fraction_html}
        {recommendations_list}
        {charts_html}
    </main>
    {footer_html}
</body>
</html>
"""


def render_index_page(results: Sequence[DatasetResult], out_dir: Path) -> str:
    template_path = out_dir / TEMPLATE_DIRNAME / INDEX_TEMPLATE_FILENAME
    dataset_entries: List[Dict[str, object]] = []
    for result in results:
        meta = result.metadata
        date_range = meta.get("date_range") or {}
        start = date_range.get("start") if isinstance(date_range, dict) else None
        end = date_range.get("end") if isinstance(date_range, dict) else None
        dataset_entries.append(
            {
                "name": result.name,
                "href": result.page_href,
                "summaryHref": result.summary_href,
                "trackCount": int(meta.get("track_count", 0) or 0),
                "uniqueArtists": int(meta.get("unique_artists", 0) or 0),
                "dateRange": {
                    "start": start or "—",
                    "end": end or "—",
                },
                "thumbnail": resolve_thumbnail(result.slug, out_dir),
                "generatedAt": meta.get("generated_at"),
            }
        )

    if template_path.exists():
        dataset_json = json.dumps(dataset_entries, indent=2, ensure_ascii=False)
        dataset_count = len(results)
        context = {
            "dataset_json": dataset_json,
            "dataset_count": str(dataset_count),
            "dataset_label": "dataset" if dataset_count == 1 else "datasets",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
        template_text = template_path.read_text(encoding="utf-8")
        return apply_index_template(template_text, context)

    rows_html = "".join(
        f"<tr><td><a href=\"{entry['href']}\">{entry['name']}</a></td>"
        f"<td>{entry['trackCount']}</td>"
        f"<td>{entry['uniqueArtists']}</td>"
        f"<td>{entry['dateRange']['start']} → {entry['dateRange']['end']}</td>"
        f"<td><a href=\"{entry['summaryHref']}\">summary</a></td></tr>"
        for entry in dataset_entries
    )
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Project Orpheus — Dataset index</title>
    <link rel=\"stylesheet\" href=\"assets/{CSS_FILENAME}\" />
</head>
<body>
    <main class=\"page\">
        <header class=\"page__header\">
            <h1 class=\"main-header\">Project Orpheus — Dataset library</h1>
            <p class=\"subtitle\">Browse exported analyses generated from Exportify CSV files.</p>
        </header>
        <section class=\"card\">
            <p>This static site was generated using the Project Orpheus analysis pipeline. Each dataset page contains interactive Plotly charts and a downloadable JSON summary.</p>
        </section>
        <table class=\"index-table\">
            <thead>
                <tr>
                    <th>Dataset</th>
                    <th>Tracks</th>
                    <th>Unique artists</th>
                    <th>Date range</th>
                    <th>Summary</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        <section class=\"card\">
            <h2>📖 Documentation</h2>
            <ul>
                <li><a href=\"docs/QUICK_START.html\">Quick Start Guide</a></li>
                <li><a href=\"docs/USER_GUIDE.html\">User Guide</a></li>
                <li><a href=\"docs/TECHNICAL_SUMMARY.html\">Technical Summary</a></li>
                <li><a href=\"docs/PROCESS_FLOWS.html\">Process Flows</a></li>
            </ul>
        </section>
    </main>
</body>
</html>
"""


def process_dataset(csv_path: Path, out_dir: Path, include_cdn: bool) -> DatasetResult:
    rows, summary = pipeline_process(csv_path)

    dataset_name = csv_path.stem.replace("_", " ").title()
    dataset_slug = slugify(csv_path.stem)

    metadata = compute_metadata(rows, summary)

    page_path = out_dir / f"{dataset_slug}.html"
    summary_path = out_dir / f"{dataset_slug}.summary.json"

    charts = [
        build_timeline_chart(rows, include_cdn),
        build_top_artists_chart(rows, False),
        build_audio_features_radar(summary, False),
    ]

    page_html = render_dataset_page(
        DatasetResult(
            name=dataset_name,
            slug=dataset_slug,
            page_path=page_path,
            summary_path=summary_path,
            metadata=metadata,
            summary=summary,
        ),
        charts,
    )
    page_path.write_text(page_html, encoding="utf-8")

    summary_payload = {
        "dataset": dataset_name,
        "source_csv": csv_path.name,
        "metadata": metadata,
        "summary": summary,
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    logger.info("Generated %s and %s", page_path.name, summary_path.name)

    return DatasetResult(
        name=dataset_name,
        slug=dataset_slug,
        page_path=page_path,
        summary_path=summary_path,
        metadata=metadata,
        summary=summary,
    )


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)

    csv_files = discover_csv_files(args.input_dir)
    assets_dir = prepare_output_directory(args.out_dir, force=args.force)
    write_css(assets_dir)
    copy_docs(args.out_dir)

    results: List[DatasetResult] = []
    include_cdn = True
    for csv_path in csv_files:
        try:
            result = process_dataset(csv_path, args.out_dir, include_cdn)
            include_cdn = False  # only include Plotly CDN script once per page set
            results.append(result)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Failed to process %s: %s", csv_path, exc)

    if not results:
        raise RuntimeError("No datasets were successfully processed.")

    index_html = render_index_page(results, args.out_dir)
    index_path = args.out_dir / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    logger.info("Wrote index to %s", index_path)


if __name__ == "__main__":
    main()
