from __future__ import annotations

import json
import re
from pathlib import Path
from time import sleep

import click

from orpheus.config import load_config, validate_config
from orpheus.db import ensure_schema, get_db, get_last_run, get_table_counts, run_migrations


def _load_cfg(ctx: click.Context) -> None:
    project_root = Path.cwd()
    try:
        ctx.ensure_object(dict)
        ctx.obj["config"] = load_config(project_root=project_root)
        ctx.obj["project_root"] = project_root
    except FileNotFoundError as e:
        raise click.ClickException(str(e))


def _missing_audio_feature_tracks(conn, limit: int | None = None) -> list[dict]:
    query = """SELECT t.track_uri, t.track_name, t.primary_artist, t.album_name
               FROM tracks t
               LEFT JOIN audio_features af ON t.track_uri = af.track_uri
               WHERE af.track_uri IS NULL
               ORDER BY t.primary_artist, t.track_name, t.track_uri"""
    params: tuple = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)

    return [dict(row) for row in conn.execute(query, params).fetchall()]


_PROFILE_NAME_RE = re.compile(r"^[a-zA-Z0-9_\- ]+$")


def _resolve_report_path(cfg, out: str | None, profile: str | None) -> Path | None:
    """Resolve where a report should be written.

    ``--out`` (an explicit path) and ``--profile`` are mutually exclusive. With a
    profile, the report is timestamped into ``<reports_dir>/<profile>/`` — the
    per-profile subdir the dashboard's dev server reads from. With neither, the
    caller's default (timestamp in the reports-dir root) is used.
    """
    if out and profile:
        raise click.UsageError("--out and --profile are mutually exclusive.")
    if out:
        return Path(out)
    if profile:
        if not _PROFILE_NAME_RE.match(profile):
            raise click.UsageError(
                "Invalid --profile name; allowed characters: letters, digits, space, '-', '_'."
            )
        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return cfg.reports_dir / profile / f"{ts}.json"
    return None


def _resolve_as_of(conn, as_of: str | None):
    """Resolve the window anchor: "now" (default), "latest-play", or an ISO timestamp.

    Spotify exports are always at least a little stale; anchoring to the latest
    recorded play keeps the state window meaningful when the export ends weeks
    before the report is generated. Returns (t_now, as_of_info-dict).
    """
    from datetime import datetime, timezone

    def _aware(dt: datetime) -> datetime:
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    if as_of and as_of == "latest-play":
        row = conn.execute("SELECT MAX(ts) FROM plays").fetchone()
        if row and row[0]:
            t = _aware(datetime.fromisoformat(row[0].replace("Z", "+00:00")))
            return t, {"as_of": t.isoformat(), "anchor": "latest_play"}
    elif as_of and as_of != "now":
        try:
            t = _aware(datetime.fromisoformat(as_of))
        except ValueError:
            raise click.UsageError(
                f"Invalid --as-of value {as_of!r}; use 'now', 'latest-play', or an ISO timestamp."
            )
        return t, {"as_of": t.isoformat(), "anchor": "explicit"}

    t = datetime.now(timezone.utc)
    return t, {"as_of": t.isoformat(), "anchor": "now"}


def _write_current_report(
    cfg, output_path: Path | None = None, as_of: str | None = None
) -> tuple[Path, str, str]:
    from datetime import datetime, timezone

    from orpheus.aggregate.windows import compute_state_and_trait
    from orpheus.output.assemble import assemble_report, record_run, write_report
    from orpheus.output.narrative import compose_narrative
    from orpheus.output.perspectives import compute_perspectives
    from orpheus.output.temporal import compute_temporal
    from orpheus.pattern.cluster import cluster_gmm, clusters_status, filter_noise
    from orpheus.pattern.trends import (
        compare_state_trait,
        detect_co_occurrences_by_window,
        detect_trends,
    )
    from orpheus.safety.rumination import check_rumination

    conn = get_db(cfg.db_path)
    started_at = datetime.now(timezone.utc)

    try:
        t_now, as_of_info = _resolve_as_of(conn, as_of)
        windows = compute_state_and_trait(conn, cfg, t_now=t_now)
        if as_of_info["anchor"] == "now" and windows["state"]["coverage"]["total_plays"] == 0:
            click.echo(
                "Note: no plays fall in the recent window — the export data may end "
                "weeks ago. Use --as-of latest-play to anchor windows to the newest play.",
                err=True,
            )
        clean_points, clean_tracks, _ = filter_noise(conn, cfg)
        clusters = cluster_gmm(clean_points, clean_tracks, cfg) if len(clean_points) > 0 else []
        cl_status = clusters_status(conn, clusters, len(clean_points))
        trends = detect_trends(conn, t_now=t_now)
        co_occurrences = detect_co_occurrences_by_window(conn, cfg, t_now=t_now)
        shifts = compare_state_trait(windows["state"], windows["trait"])
        safety_flags = check_rumination(windows["state"], cfg)
        temporal = compute_temporal(conn, t_now)
        experimental = compute_perspectives(conn, cfg.model_version, t_now)
        narrative = compose_narrative(
            state=windows["state"], trait=windows["trait"],
            shifts=shifts, trends=trends, clusters=clusters,
            clusters_status=cl_status, temporal=temporal, as_of=as_of_info,
        )

        report_data = assemble_report(
            state=windows["state"], trait=windows["trait"],
            shifts=shifts, trends=trends, co_occurrences=co_occurrences["global"]["notable"],
            state_co_occurrences=co_occurrences["state"]["notable"],
            trait_co_occurrences=co_occurrences["trait"]["notable"],
            state_co_occurrence_matrix=co_occurrences["state"]["matrix"],
            trait_co_occurrence_matrix=co_occurrences["trait"]["matrix"],
            clusters=clusters, config=cfg, safety_flags=safety_flags,
            clusters_status=cl_status,
            temporal=temporal, narrative=narrative, as_of=as_of_info,
            experimental=experimental,
        )

        if output_path is None:
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
            output_path = cfg.reports_dir / f"{ts}.json"

        output_hash = write_report(report_data, output_path)
        run_id = record_run(conn, cfg, output_path, output_hash, started_at)
        return output_path, run_id, output_hash
    finally:
        conn.close()


@click.group()
@click.pass_context
def main(ctx):
    """Orpheus v2 — personal music listening analysis."""
    pass


@main.command("config")
@click.argument("action", type=click.Choice(["validate"]))
@click.pass_context
def config_cmd(ctx, action):
    """Validate configuration file."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    errors = validate_config(cfg)
    if errors:
        for e in errors:
            click.echo(f"  ERROR: {e}", err=True)
        raise click.ClickException(f"Config validation failed with {len(errors)} error(s)")
    click.echo("Config is valid.")


@main.group("db")
def db_group():
    """Database operations."""
    pass


@db_group.command("migrate")
@click.pass_context
def db_migrate(ctx):
    """Create or migrate the database schema."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    db_path = cfg.db_path
    click.echo(f"Database: {db_path}")

    conn = get_db(db_path)
    ensure_schema(conn)
    applied = run_migrations(conn)
    conn.close()

    if applied:
        click.echo(f"Applied migrations: {applied}")
    else:
        click.echo("Schema is up to date.")


@main.command()
@click.pass_context
def status(ctx):
    """Show database state, enrichment coverage, and last run info."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    db_path = cfg.db_path

    if not db_path.exists():
        click.echo(f"Database not found at {db_path}")
        click.echo("Run 'orpheus db migrate' to initialize.")
        return

    conn = get_db(db_path)
    counts = get_table_counts(conn)
    last_run = get_last_run(conn)

    click.echo(f"Database: {db_path}")
    click.echo(f"  Size: {db_path.stat().st_size / 1024:.1f} KB")
    click.echo()

    click.echo("Tables:")
    for table, count in counts.items():
        label = f"  {table}:"
        click.echo(f"{label:<25} {count:>8} rows")

    if counts["tracks"] > 0:
        enriched = conn.execute("SELECT COUNT(*) FROM tracks WHERE enriched_at IS NOT NULL").fetchone()[0]
        click.echo(f"\n  Enrichment coverage: {enriched}/{counts['tracks']} tracks ({100*enriched/counts['tracks']:.0f}%)")

    if counts["tracks"] > 0 and counts["track_scores"] >= 0:
        scored = conn.execute("SELECT COUNT(DISTINCT track_uri) FROM track_scores").fetchone()[0]
        click.echo(f"  Scoring coverage:    {scored}/{counts['tracks']} tracks ({100*scored/counts['tracks']:.0f}%)")

    click.echo()
    if last_run:
        click.echo(f"Last run: {last_run['finished_at']} → {last_run['output_path']}")
    else:
        click.echo("No pipeline runs recorded.")

    conn.close()


@main.command()
@click.option("--source", required=True, type=click.Path(exists=True), help="Path to Spotify export directory or JSON file")
@click.pass_context
def ingest(ctx, source):
    """Parse Spotify Extended Streaming History JSON into the database."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    conn = get_db(cfg.db_path)

    from orpheus.ingest.spotify_export import ingest_export

    stats = ingest_export(Path(source), conn)
    conn.close()

    click.echo(f"Ingested {stats['plays_inserted']} plays, {stats['tracks_resolved']} tracks "
               f"({stats['duplicates_skipped']} duplicates skipped)")


@main.command()
@click.pass_context
def enrich(ctx):
    """Fetch audio features and lyrics for unenriched tracks."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    conn = get_db(cfg.db_path)

    from orpheus.enrich import run_enrichment

    stats = run_enrichment(conn, cfg)
    conn.close()

    audio = stats["audio"]
    lyrics = stats["lyrics"]
    click.echo(f"Audio features: {audio['archive_hits']} archive, "
               f"{audio['missed']} missed (of {audio['total']})")
    click.echo(f"Lyrics: {lyrics['fetched']} fetched, {lyrics['no_lyrics']} no lyrics, "
               f"{lyrics['failed']} failed (of {lyrics['total']})")


@main.command()
@click.pass_context
def score(ctx):
    """Score enriched tracks for emotion, theme, and depth."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    conn = get_db(cfg.db_path)

    from orpheus.score.scoring import run_scoring

    stats = run_scoring(conn, cfg)
    conn.close()

    click.echo(f"Scored {stats['scored']} tracks (model: {cfg.model_version})")


@main.command()
@click.pass_context
def analyze(ctx):
    """Run aggregation, clustering, and trend detection."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    conn = get_db(cfg.db_path)

    from orpheus.aggregate.windows import compute_state_and_trait
    from orpheus.pattern.cluster import cluster_gmm, filter_noise
    from orpheus.pattern.trends import (
        compare_state_trait,
        detect_co_occurrences_by_window,
        detect_trends,
    )

    click.echo("Aggregating windows...")
    windows = compute_state_and_trait(conn, cfg)

    click.echo("Clustering...")
    clean_points, clean_tracks, noise_count = filter_noise(conn, cfg)
    clusters = cluster_gmm(clean_points, clean_tracks, cfg) if len(clean_points) > 0 else []

    click.echo("Detecting trends...")
    trends = detect_trends(conn)
    co_occurrences = detect_co_occurrences_by_window(conn, cfg)
    shifts = compare_state_trait(windows["state"], windows["trait"])

    conn.close()

    click.echo(f"Done. {len(clusters)} clusters, {len(trends)} trends, "
               f"{len(co_occurrences['global']['notable'])} co-occurrences "
               f"({len(co_occurrences['state']['notable'])} recent, "
               f"{len(co_occurrences['trait']['notable'])} usual), "
               f"{len(shifts)} shifts, {noise_count} noise tracks filtered.")


_AS_OF_HELP = (
    "Window anchor: 'now' (default), 'latest-play' (anchor to the newest play in the DB — "
    "use for stale exports), or an ISO timestamp."
)


@main.command()
@click.option("--out", type=click.Path(), default=None, help="Explicit output path for JSON report")
@click.option("--profile", default=None, help="Write a timestamped report into <reports_dir>/<profile>/ (where the dashboard reads it)")
@click.option("--as-of", "as_of", default="now", help=_AS_OF_HELP)
@click.pass_context
def report(ctx, out, profile, as_of):
    """Assemble and write the JSON report."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    output_path, run_id, output_hash = _write_current_report(
        cfg,
        _resolve_report_path(cfg, out, profile),
        as_of=as_of,
    )

    click.echo(f"Report written to {output_path}")
    click.echo(f"Run ID: {run_id}, Hash: {output_hash[:16]}...")


@main.command()
@click.option("--out", type=click.Path(), default=None, help="Explicit output path for JSON report")
@click.option("--profile", default=None, help="Write a timestamped report into <reports_dir>/<profile>/ (where the dashboard reads it)")
@click.option("--as-of", "as_of", default="now", help=_AS_OF_HELP)
@click.pass_context
def refresh(ctx, out, profile, as_of):
    """Refresh the report from the current database."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    output_path, run_id, output_hash = _write_current_report(
        cfg,
        _resolve_report_path(cfg, out, profile),
        as_of=as_of,
    )

    click.echo(f"Latest report: {output_path}")
    click.echo(f"Run ID: {run_id}")
    click.echo(f"Hash:   {output_hash[:16]}...")


@main.command("run-all")
@click.option("--source", type=click.Path(exists=True), default=None, help="Path to Spotify export (optional if already ingested)")
@click.option("--out", type=click.Path(), default=None, help="Explicit output path for JSON report")
@click.option("--profile", default=None, help="Write a timestamped report into <reports_dir>/<profile>/ (where the dashboard reads it)")
@click.option("--as-of", "as_of", default="now", help=_AS_OF_HELP)
@click.pass_context
def run_all(ctx, source, out, profile, as_of):
    """Run the full pipeline end-to-end."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    report_path = _resolve_report_path(cfg, out, profile)

    conn = get_db(cfg.db_path)
    ensure_schema(conn)
    run_migrations(conn)

    from datetime import datetime, timezone

    from orpheus.aggregate.windows import compute_state_and_trait
    from orpheus.enrich import run_enrichment
    from orpheus.output.assemble import assemble_report, record_run, write_report
    from orpheus.output.narrative import compose_narrative
    from orpheus.output.perspectives import compute_perspectives
    from orpheus.output.temporal import compute_temporal
    from orpheus.pattern.cluster import cluster_gmm, clusters_status, filter_noise
    from orpheus.pattern.trends import (
        compare_state_trait,
        detect_co_occurrences_by_window,
        detect_trends,
    )
    from orpheus.safety.rumination import check_rumination
    from orpheus.score.scoring import run_scoring

    started_at = datetime.now(timezone.utc)

    if source:
        from orpheus.ingest.spotify_export import ingest_export
        click.echo("Ingesting...")
        stats = ingest_export(Path(source), conn)
        click.echo(f"  {stats['plays_inserted']} plays, {stats['tracks_resolved']} tracks")

    click.echo("Enriching...")
    enrich_stats = run_enrichment(conn, cfg)
    click.echo(f"  Audio: {enrich_stats['audio']['archive_hits']} archive, "
               f"{enrich_stats['audio']['missed']} missed")

    click.echo("Scoring...")
    score_stats = run_scoring(conn, cfg)
    click.echo(f"  {score_stats['scored']} tracks scored")

    click.echo("Analyzing...")
    t_now, as_of_info = _resolve_as_of(conn, as_of)
    windows = compute_state_and_trait(conn, cfg, t_now=t_now)
    clean_points, clean_tracks, noise_count = filter_noise(conn, cfg)
    clusters = cluster_gmm(clean_points, clean_tracks, cfg) if len(clean_points) > 0 else []
    cl_status = clusters_status(conn, clusters, len(clean_points))
    trends = detect_trends(conn, t_now=t_now)
    co_occurrences = detect_co_occurrences_by_window(conn, cfg, t_now=t_now)
    shifts = compare_state_trait(windows["state"], windows["trait"])
    safety_flags = check_rumination(windows["state"], cfg)
    temporal = compute_temporal(conn, t_now)
    experimental = compute_perspectives(conn, cfg.model_version, t_now)
    narrative = compose_narrative(
        state=windows["state"], trait=windows["trait"],
        shifts=shifts, trends=trends, clusters=clusters,
        clusters_status=cl_status, temporal=temporal, as_of=as_of_info,
    )

    click.echo("Assembling report...")
    report_data = assemble_report(
        state=windows["state"], trait=windows["trait"],
        shifts=shifts, trends=trends, co_occurrences=co_occurrences["global"]["notable"],
        state_co_occurrences=co_occurrences["state"]["notable"],
        trait_co_occurrences=co_occurrences["trait"]["notable"],
        state_co_occurrence_matrix=co_occurrences["state"]["matrix"],
        trait_co_occurrence_matrix=co_occurrences["trait"]["matrix"],
        clusters=clusters, config=cfg, safety_flags=safety_flags,
        clusters_status=cl_status,
        temporal=temporal, narrative=narrative, as_of=as_of_info,
        experimental=experimental,
    )

    if report_path is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        report_path = cfg.reports_dir / f"{ts}.json"
    output_path = report_path
    output_hash = write_report(report_data, output_path)
    run_id = record_run(conn, cfg, output_path, output_hash, started_at)
    conn.close()

    click.echo(f"\nReport: {output_path}")
    click.echo(f"Run ID: {run_id}")
    click.echo(f"Hash:   {output_hash[:16]}...")


@main.group("live")
def live_group():
    """Spotify Web API live sync (deferred)."""
    pass


@live_group.command("sync")
@click.pass_context
def live_sync(ctx):
    """Pull latest data from Spotify Web API."""
    click.echo("Deferred — not yet implemented.")
    click.echo(
        "Note: the Web API has no full-history endpoint. /me/player/recently-played\n"
        "returns only the last 50 plays, so a live sync can only ever be a frequent\n"
        "(roughly daily) top-up — a monthly pull would drop plays beyond the most\n"
        "recent 50. The complete record comes from the GDPR Extended Streaming\n"
        "History export ingested via `orpheus ingest`. See docs/C3_data_pipeline_spec.md."
    )


@main.group("archive")
def archive_group():
    """Audio-feature archive operations."""
    pass


@archive_group.command("import")
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def archive_import(ctx, path):
    """Bulk-import audio features from CSV or SQLite archive."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    archive_path = Path(path)

    from orpheus.enrich.audio_import import import_from_csv, import_from_sqlite

    conn = get_db(cfg.db_path)
    try:
        suffix = archive_path.suffix.lower()
        if suffix == ".csv":
            stats = import_from_csv(conn, archive_path)
        elif suffix in {".db", ".sqlite", ".sqlite3"}:
            stats = import_from_sqlite(conn, archive_path)
        else:
            raise click.ClickException(
                "Unsupported archive format. Use .csv, .db, .sqlite, or .sqlite3."
            )
    except ValueError as e:
        raise click.ClickException(str(e))
    finally:
        conn.close()

    click.echo(f"Imported audio features from {archive_path}")
    _echo_stats(stats)


@archive_group.command("fill-gaps")
@click.option(
    "--limit",
    type=click.IntRange(min=1),
    default=None,
    help="Maximum number of missing tracks to request. Use this for small test runs.",
)
@click.option(
    "--batch-size",
    type=click.IntRange(min=1),
    default=None,
    help="Override reccobeats.batch_size for this run.",
)
@click.option(
    "--delay",
    type=click.FloatRange(min=0),
    default=None,
    help="Override reccobeats.delay between batches for this run.",
)
@click.option(
    "--not-found-out",
    type=click.Path(),
    default=None,
    help="Write tracks not found in this run to a JSON file.",
)
@click.pass_context
def archive_fill_gaps(ctx, limit, batch_size, delay, not_found_out):
    """Fill missing audio features via ReccoBeats."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]

    from orpheus.enrich.audio_import import spotify_id_from_track_uri
    from orpheus.enrich.enrich import _insert_audio_features
    from orpheus.enrich.reccobeats import ReccoBeatsClient

    conn = get_db(cfg.db_path)
    rows = _missing_audio_feature_tracks(conn, limit=limit)

    ids_by_uri = [
        (row, spotify_id_from_track_uri(row["track_uri"]))
        for row in rows
    ]
    not_found_tracks = [
        {**row, "reason": "missing_spotify_id"}
        for row, spotify_id in ids_by_uri
        if not spotify_id
    ]
    ids_by_uri = [(row, spotify_id) for row, spotify_id in ids_by_uri if spotify_id]

    stats = {
        "total_unmatched": len(rows),
        "fetched": 0,
        "not_found": len(not_found_tracks),
        "errors": 0,
    }
    client = ReccoBeatsClient()
    batch_size = batch_size or cfg.reccobeats.batch_size
    delay = cfg.reccobeats.delay if delay is None else delay

    try:
        for start in range(0, len(ids_by_uri), batch_size):
            batch = ids_by_uri[start:start + batch_size]
            spotify_ids = [spotify_id for _, spotify_id in batch]
            result = client.fetch_features(spotify_ids)
            if result == {} and spotify_ids:
                stats["errors"] += len(spotify_ids)
                not_found_tracks.extend(
                    {**row, "reason": "fetch_error"}
                    for row, _ in batch
                )
            else:
                for row, spotify_id in batch:
                    features = result.get(spotify_id)
                    if features is None:
                        stats["not_found"] += 1
                        not_found_tracks.append({**row, "reason": "not_found"})
                        continue
                    _insert_audio_features(conn, row["track_uri"], features)
                    stats["fetched"] += 1

            conn.commit()
            if delay > 0 and start + batch_size < len(ids_by_uri):
                sleep(delay)
    finally:
        conn.close()

    click.echo("Filled audio-feature gaps from ReccoBeats")
    _echo_stats(stats)
    if not_found_out:
        out_path = Path(not_found_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(not_found_tracks, indent=2, ensure_ascii=False))
        click.echo(f"Not-found tracks written to {out_path}")


@archive_group.command("missing-audio")
@click.option("--limit", type=click.IntRange(min=1), default=25, help="Rows to print.")
@click.option("--out", type=click.Path(), default=None, help="Write full missing list to JSON.")
@click.pass_context
def archive_missing_audio(ctx, limit, out):
    """List tracks that still lack audio features."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    conn = get_db(cfg.db_path)
    try:
        all_rows = _missing_audio_feature_tracks(conn)
    finally:
        conn.close()

    click.echo(f"Tracks missing audio features: {len(all_rows)}")

    if out:
        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(all_rows, indent=2, ensure_ascii=False))
        click.echo(f"Missing tracks written to {out_path}")

    for row in all_rows[:limit]:
        title = row.get("track_name") or row["track_uri"]
        artist = row.get("primary_artist") or "Unknown artist"
        click.echo(f"  {artist} - {title} ({row['track_uri']})")


def _echo_stats(stats: dict) -> None:
    width = max(len(key) for key in stats) if stats else 0
    for key, value in stats.items():
        click.echo(f"  {key:<{width}}  {value}")
