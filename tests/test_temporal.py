"""Tests for the temporal grounding layer (raw-plays stats)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from orpheus.output.temporal import compute_temporal

T_NOW = datetime(2026, 5, 22, 23, 59, tzinfo=timezone.utc)


def _insert_track(conn, uri, name, artist):
    conn.execute(
        """INSERT OR IGNORE INTO tracks (track_uri, track_name, primary_artist, album_name)
           VALUES (?, ?, ?, ?)""",
        (uri, name, artist, "Album"),
    )


def _insert_play(conn, uri, ts, ms=180_000):
    conn.execute(
        "INSERT INTO plays (ts, track_uri, ms_played) VALUES (?, ?, ?)",
        (ts.strftime("%Y-%m-%dT%H:%M:%SZ"), uri, ms),
    )


def _seed(conn):
    _insert_track(conn, "spotify:track:aaa", "Alpha", "Artist One")
    _insert_track(conn, "spotify:track:bbb", "Beta", "Artist Two")
    _insert_track(conn, "spotify:track:ccc", "Gamma", "Artist One")

    # Song of the season: aaa played 6 times over the window.
    for d in range(6):
        _insert_play(conn, "spotify:track:aaa", T_NOW - timedelta(days=d * 3, hours=20))

    # Comeback track: bbb played twice, a 30-day silence, then twice more.
    for d in (80, 78, 40, 38):
        _insert_play(conn, "spotify:track:bbb", T_NOW - timedelta(days=d))

    # Biggest day: ccc played 5 times in one day (short plays).
    for h in range(5):
        _insert_play(conn, "spotify:track:ccc", T_NOW - timedelta(days=10, hours=h), ms=240_000)

    # A play outside the lookback window: must be excluded.
    _insert_play(conn, "spotify:track:aaa", T_NOW - timedelta(days=120))
    conn.commit()


def test_grounding_counts(tmp_db):
    _seed(tmp_db)
    result = compute_temporal(tmp_db, T_NOW, lookback_days=90)

    g = result["grounding"]
    assert g["plays"] == 15  # 6 + 4 + 5, excluding the 120-day-old play
    assert g["qualified_plays"] == 15
    assert g["distinct_tracks"] == 3
    assert g["distinct_artists"] == 2
    assert g["hours"] > 0


def test_song_of_season_and_biggest_day(tmp_db):
    _seed(tmp_db)
    result = compute_temporal(tmp_db, T_NOW, lookback_days=90)

    moments = result["moments"]
    assert moments["song_of_season"]["name"] == "Alpha"
    assert moments["song_of_season"]["qualified_plays"] == 6

    biggest = moments["biggest_day"]
    assert biggest["top_track"]["name"] == "Gamma"
    assert biggest["plays"] == 5


def test_comeback_track_detected(tmp_db):
    _seed(tmp_db)
    result = compute_temporal(tmp_db, T_NOW, lookback_days=90)

    comeback = result["moments"]["comeback_track"]
    assert comeback is not None
    assert comeback["name"] == "Beta"
    assert comeback["gap_days"] >= 21


def test_months_and_rhythm(tmp_db):
    _seed(tmp_db)
    result = compute_temporal(tmp_db, T_NOW, lookback_days=90)

    assert len(result["months"]) >= 2
    for month in result["months"]:
        assert month["hours"] >= 0
        assert month["top_track"] is not None

    rhythm = result["rhythm"]
    assert rhythm["peak_daypart"] in {"night", "morning", "afternoon", "evening"}
    shares = sum(b["share"] for b in rhythm["by_daypart"])
    assert 0.99 <= shares <= 1.01


def test_empty_window(tmp_db):
    result = compute_temporal(tmp_db, T_NOW, lookback_days=90)
    assert result["grounding"]["plays"] == 0
    assert result["moments"] is None
    assert result["months"] == []
