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
from datetime import datetime
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
    css = re.sub(r"^\s+", "", css, flags=re.MULTILINE)
    additional_css = """
body {
    margin: 0;
    background: var(--color-muted, #f5f6ff);
    color: var(--color-text, #1f1f2e);
    font-family: 'Manrope', sans-serif;
}

a {
    color: var(--color-primary, #6c63ff);
}

.page {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
}

.page__header {
    text-align: center;
    margin-bottom: 2rem;
}

.dataset-meta {
    display: grid;
    gap: 1.5rem;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    margin-bottom: 2rem;
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
}

.recommendations {
    margin-top: 2rem;
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
    margin-top: 2rem;
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
""".strip()
    return css.strip() + "\n\n" + additional_css + "\n"


def write_css(assets_dir: Path) -> Path:
    css_content = extract_css_from_styles()
    css_path = assets_dir / CSS_FILENAME
    css_path.write_text(css_content, encoding="utf-8")
    logger.info("Wrote CSS to %s", css_path)
    return css_path


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

    return {
        "track_count": track_count,
        "unique_artists": unique_artists,
        "date_range": date_range,
        "generated_at": datetime.utcnow().isoformat(),
        "zero_fraction": zero_fraction,
    }


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

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Project Orpheus — {result.name}</title>
    <link rel=\"stylesheet\" href=\"assets/{CSS_FILENAME}\" />
</head>
<body>
    <main class=\"page\">
        <header class=\"page__header\">
            <p><a href=\"index.html\">← Back to index</a></p>
            <h1 class=\"main-header\">{result.name}</h1>
            <p class=\"subtitle\">Static emotional analysis generated with Project Orpheus</p>
        </header>

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
</body>
</html>
"""


def render_index_page(results: Sequence[DatasetResult]) -> str:
    rows_html = "".join(
        f"<tr><td><a href=\"{result.page_href}\">{result.name}</a></td>"
        f"<td>{result.metadata.get('track_count', 0)}</td>"
        f"<td>{result.metadata.get('unique_artists', 0)}</td>"
        f"<td>{(result.metadata.get('date_range') or {}).get('start', '—')} → {(result.metadata.get('date_range') or {}).get('end', '—')}</td>"
        f"<td><a href=\"{result.summary_href}\">summary</a></td></tr>"
        for result in results
    )
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Project Orpheus — Dataset index</title>
    <link rel=\"stylesheet\" href=\"assets/{CSS_FILENAME}\" />
    <script src=\"https://cdn.plot.ly/plotly-2.27.0.min.js\"></script>
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

    index_html = render_index_page(results)
    index_path = args.out_dir / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    logger.info("Wrote index to %s", index_path)


if __name__ == "__main__":
    main()
