"""Temporal grounding layer: stats computed from *raw* plays.

Everything here draws on the full `plays` table (no join to `track_scores`),
so it has 100% coverage regardless of scoring backlog. These are the honest,
Wrapped-style grounding numbers — hours listened, rhythm, months, moments —
that anchor the mood narrative in verifiable listening behaviour.

Timestamps in Spotify exports are UTC; daypart/weekday buckets inherit that,
which is flagged in `rhythm.timezone_note` rather than silently localised.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

QUALIFIED_LISTEN_MS = 30_000

# Minimum gap between plays of the same track for it to count as a "comeback"
# (a song you left behind and returned to), and the minimum plays on each side
# of the gap so a one-off replay doesn't qualify.
COMEBACK_MIN_GAP_DAYS = 21
COMEBACK_MIN_PLAYS_EACH_SIDE = 2

_DAYPARTS = [
    ("night", 0, 6),
    ("morning", 6, 12),
    ("afternoon", 12, 18),
    ("evening", 18, 24),
]

_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _parse_ts(ts: str) -> datetime:
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def compute_temporal(
    conn: sqlite3.Connection,
    t_now: datetime,
    lookback_days: float = 90,
) -> dict:
    """Grounding stats over all plays in the lookback window ending at t_now."""
    window_start = t_now - timedelta(days=lookback_days)

    rows = conn.execute(
        """SELECT p.ts, p.ms_played, p.track_uri,
                  t.track_name, t.primary_artist
           FROM plays p
           JOIN tracks t ON p.track_uri = t.track_uri
           ORDER BY p.ts""",
    ).fetchall()

    plays = []
    for row in rows:
        t_play = _parse_ts(row["ts"])
        if window_start <= t_play <= t_now:
            plays.append((t_play, row))

    if not plays:
        return {
            "lookback_days": lookback_days,
            "from_date": None,
            "to_date": None,
            "grounding": {
                "hours": 0.0,
                "plays": 0,
                "qualified_plays": 0,
                "distinct_tracks": 0,
                "distinct_artists": 0,
                "days_with_listening": 0,
            },
            "rhythm": None,
            "months": [],
            "moments": None,
        }

    total_ms = 0
    qualified = 0
    tracks: set[str] = set()
    artists: set[str] = set()
    days: dict[str, dict] = {}
    daypart_ms = {name: 0 for name, _, _ in _DAYPARTS}
    weekday_ms = {day: 0 for day in _WEEKDAYS}
    months: dict[str, dict] = {}
    track_stats: dict[str, dict] = {}

    for t_play, row in plays:
        ms = row["ms_played"] or 0
        total_ms += ms
        uri = row["track_uri"]
        tracks.add(uri)
        if row["primary_artist"]:
            artists.add(row["primary_artist"])

        day_key = t_play.strftime("%Y-%m-%d")
        day = days.setdefault(day_key, {"ms": 0, "plays": 0, "track_ms": {}})
        day["ms"] += ms
        day["plays"] += 1
        day["track_ms"][uri] = day["track_ms"].get(uri, 0) + ms

        for name, start, end in _DAYPARTS:
            if start <= t_play.hour < end:
                daypart_ms[name] += ms
                break
        weekday_ms[_WEEKDAYS[t_play.weekday()]] += ms

        month_key = t_play.strftime("%Y-%m")
        month = months.setdefault(month_key, {"ms": 0, "plays": 0, "artist_ms": {}, "track_ms": {}})
        month["ms"] += ms
        month["plays"] += 1
        if row["primary_artist"]:
            month["artist_ms"][row["primary_artist"]] = (
                month["artist_ms"].get(row["primary_artist"], 0) + ms
            )
        month["track_ms"][uri] = month["track_ms"].get(uri, 0) + ms

        stat = track_stats.setdefault(
            uri,
            {
                "name": row["track_name"],
                "artist": row["primary_artist"],
                "ms": 0,
                "qualified_plays": 0,
                "qualified_ts": [],
            },
        )
        stat["ms"] += ms
        if ms >= QUALIFIED_LISTEN_MS:
            qualified += 1
            stat["qualified_plays"] += 1
            stat["qualified_ts"].append(t_play)

    def _hours(ms: int) -> float:
        return round(ms / 3_600_000, 1)

    total_hours = _hours(total_ms)

    # Rhythm: share of listening time by daypart and weekday.
    def _shares(bucket_ms: dict[str, int]) -> list[dict]:
        return [
            {
                "bucket": name,
                "hours": _hours(ms),
                "share": round(ms / total_ms, 3) if total_ms else 0.0,
            }
            for name, ms in bucket_ms.items()
        ]

    daypart_shares = _shares(daypart_ms)
    weekday_shares = _shares(weekday_ms)
    rhythm = {
        "by_daypart": daypart_shares,
        "by_weekday": weekday_shares,
        "peak_daypart": max(daypart_shares, key=lambda b: b["hours"])["bucket"],
        "peak_weekday": max(weekday_shares, key=lambda b: b["hours"])["bucket"],
        "timezone_note": "Buckets use UTC timestamps from the Spotify export.",
    }

    def _track_summary(uri: str) -> dict:
        stat = track_stats[uri]
        return {"uri": uri, "name": stat["name"], "artist": stat["artist"]}

    months_out = []
    for month_key in sorted(months):
        month = months[month_key]
        top_artist = (
            max(month["artist_ms"], key=month["artist_ms"].get) if month["artist_ms"] else None
        )
        top_track_uri = (
            max(month["track_ms"], key=month["track_ms"].get) if month["track_ms"] else None
        )
        months_out.append(
            {
                "month": month_key,
                "hours": _hours(month["ms"]),
                "plays": month["plays"],
                "top_artist": top_artist,
                "top_track": _track_summary(top_track_uri) if top_track_uri else None,
            }
        )

    # Moments -------------------------------------------------------------
    biggest_day_key = max(days, key=lambda d: days[d]["ms"])
    biggest_day = days[biggest_day_key]
    biggest_day_track = max(biggest_day["track_ms"], key=biggest_day["track_ms"].get)

    season_uri = max(
        track_stats,
        key=lambda u: (track_stats[u]["qualified_plays"], track_stats[u]["ms"]),
    )
    season = track_stats[season_uri]

    artist_ms: dict[str, int] = {}
    for stat in track_stats.values():
        if stat["artist"]:
            artist_ms[stat["artist"]] = artist_ms.get(stat["artist"], 0) + stat["ms"]
    top_artist_name = max(artist_ms, key=artist_ms.get) if artist_ms else None

    comeback = _find_comeback(track_stats)

    moments = {
        "biggest_day": {
            "date": biggest_day_key,
            "hours": _hours(biggest_day["ms"]),
            "plays": biggest_day["plays"],
            "top_track": _track_summary(biggest_day_track),
        },
        "song_of_season": {
            **_track_summary(season_uri),
            "qualified_plays": season["qualified_plays"],
            "hours": _hours(season["ms"]),
        },
        "top_artist": (
            {"artist": top_artist_name, "hours": _hours(artist_ms[top_artist_name])}
            if top_artist_name
            else None
        ),
        "comeback_track": comeback,
    }

    return {
        "lookback_days": lookback_days,
        "from_date": plays[0][0].strftime("%Y-%m-%d"),
        "to_date": plays[-1][0].strftime("%Y-%m-%d"),
        "grounding": {
            "hours": total_hours,
            "plays": len(plays),
            "qualified_plays": qualified,
            "distinct_tracks": len(tracks),
            "distinct_artists": len(artists),
            "days_with_listening": len(days),
        },
        "rhythm": rhythm,
        "months": months_out,
        "moments": moments,
    }


def _find_comeback(track_stats: dict[str, dict]) -> dict | None:
    """The track with the longest silence between qualified plays.

    Requires at least COMEBACK_MIN_PLAYS_EACH_SIDE qualified plays on both
    sides of the gap so a single stray replay doesn't read as a return.
    """
    best_uri = None
    best_gap = timedelta(days=COMEBACK_MIN_GAP_DAYS)
    best_split = None

    for uri, stat in track_stats.items():
        ts = sorted(stat["qualified_ts"])
        if len(ts) < COMEBACK_MIN_PLAYS_EACH_SIDE * 2:
            continue
        for i in range(1, len(ts)):
            gap = ts[i] - ts[i - 1]
            before, after = i, len(ts) - i
            if (
                gap > best_gap
                and before >= COMEBACK_MIN_PLAYS_EACH_SIDE
                and after >= COMEBACK_MIN_PLAYS_EACH_SIDE
            ):
                best_gap = gap
                best_uri = uri
                best_split = (ts[i - 1], ts[i])

    if best_uri is None:
        return None

    stat = track_stats[best_uri]
    return {
        "uri": best_uri,
        "name": stat["name"],
        "artist": stat["artist"],
        "gap_days": best_gap.days,
        "left_on": best_split[0].strftime("%Y-%m-%d"),
        "returned_on": best_split[1].strftime("%Y-%m-%d"),
        "qualified_plays": stat["qualified_plays"],
    }
