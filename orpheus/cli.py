from __future__ import annotations

from pathlib import Path

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
    click.echo(f"Audio features: {audio['archive_hits']} archive, {audio['soundnet_hits']} SoundNet, "
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
    from orpheus.pattern.trends import compare_state_trait, detect_co_occurrences, detect_trends

    click.echo("Aggregating windows...")
    windows = compute_state_and_trait(conn, cfg)

    click.echo("Clustering...")
    clean_points, clean_tracks, noise_count = filter_noise(conn, cfg)
    clusters = cluster_gmm(clean_points, clean_tracks, cfg) if len(clean_points) > 0 else []

    click.echo("Detecting trends...")
    trends = detect_trends(conn)
    co_occurrences = detect_co_occurrences(conn)
    shifts = compare_state_trait(windows["state"], windows["trait"])

    conn.close()

    click.echo(f"Done. {len(clusters)} clusters, {len(trends)} trends, "
               f"{len(co_occurrences)} co-occurrences, {len(shifts)} shifts, "
               f"{noise_count} noise tracks filtered.")


@main.command()
@click.option("--out", type=click.Path(), default=None, help="Output path for JSON report")
@click.pass_context
def report(ctx, out):
    """Assemble and write the JSON report."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]
    conn = get_db(cfg.db_path)

    from datetime import datetime, timezone

    from orpheus.aggregate.windows import compute_state_and_trait
    from orpheus.output.assemble import assemble_report, record_run, write_report
    from orpheus.pattern.cluster import cluster_gmm, filter_noise
    from orpheus.pattern.trends import compare_state_trait, detect_co_occurrences, detect_trends
    from orpheus.safety.rumination import check_rumination

    started_at = datetime.now(timezone.utc)

    windows = compute_state_and_trait(conn, cfg)
    clean_points, clean_tracks, _ = filter_noise(conn, cfg)
    clusters = cluster_gmm(clean_points, clean_tracks, cfg) if len(clean_points) > 0 else []
    trends = detect_trends(conn)
    co_occurrences = detect_co_occurrences(conn)
    shifts = compare_state_trait(windows["state"], windows["trait"])
    safety_flags = check_rumination(windows["state"], cfg)

    report_data = assemble_report(
        state=windows["state"], trait=windows["trait"],
        shifts=shifts, co_occurrences=co_occurrences,
        clusters=clusters, config=cfg, safety_flags=safety_flags,
    )

    if out:
        output_path = Path(out)
    else:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        output_path = cfg.reports_dir / f"{ts}.json"

    output_hash = write_report(report_data, output_path)
    run_id = record_run(conn, cfg, output_path, output_hash, started_at)
    conn.close()

    click.echo(f"Report written to {output_path}")
    click.echo(f"Run ID: {run_id}, Hash: {output_hash[:16]}...")


@main.command("run-all")
@click.option("--source", type=click.Path(exists=True), default=None, help="Path to Spotify export (optional if already ingested)")
@click.pass_context
def run_all(ctx, source):
    """Run the full pipeline end-to-end."""
    _load_cfg(ctx)
    cfg = ctx.obj["config"]

    conn = get_db(cfg.db_path)
    ensure_schema(conn)
    run_migrations(conn)

    from datetime import datetime, timezone

    from orpheus.aggregate.windows import compute_state_and_trait
    from orpheus.enrich import run_enrichment
    from orpheus.output.assemble import assemble_report, record_run, write_report
    from orpheus.pattern.cluster import cluster_gmm, filter_noise
    from orpheus.pattern.trends import compare_state_trait, detect_co_occurrences, detect_trends
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
               f"{enrich_stats['audio']['soundnet_hits']} SoundNet, "
               f"{enrich_stats['audio']['missed']} missed")

    click.echo("Scoring...")
    score_stats = run_scoring(conn, cfg)
    click.echo(f"  {score_stats['scored']} tracks scored")

    click.echo("Analyzing...")
    windows = compute_state_and_trait(conn, cfg)
    clean_points, clean_tracks, noise_count = filter_noise(conn, cfg)
    clusters = cluster_gmm(clean_points, clean_tracks, cfg) if len(clean_points) > 0 else []
    trends = detect_trends(conn)
    co_occurrences = detect_co_occurrences(conn)
    shifts = compare_state_trait(windows["state"], windows["trait"])
    safety_flags = check_rumination(windows["state"], cfg)

    click.echo("Assembling report...")
    report_data = assemble_report(
        state=windows["state"], trait=windows["trait"],
        shifts=shifts, co_occurrences=co_occurrences,
        clusters=clusters, config=cfg, safety_flags=safety_flags,
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    output_path = cfg.reports_dir / f"{ts}.json"
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


@main.group("archive")
def archive_group():
    """Anna's Archive bulk operations."""
    pass


@archive_group.command("import")
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def archive_import(ctx, path):
    """Bulk-import audio features from Anna's Archive dump."""
    _load_cfg(ctx)
    click.echo("Not yet implemented.")
