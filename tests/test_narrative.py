"""Tests for the server-side narrative composer."""

from __future__ import annotations

from orpheus.output.narrative import compose_narrative

_STATE_GOOD = {
    "emotions": {"nostalgia_longing": 0.3, "tension_anxiety": 0.25, "peacefulness": 0.1},
    "themes": {"heartbreak_loss": 0.3, "adversity_resilience": 0.2},
    "coverage": {"scored_plays": 80, "total_plays": 100, "ratio": 0.8},
}

_STATE_THIN = {
    "emotions": {"joyful_activation": 0.5},
    "themes": {"hedonism_escape": 0.4},
    "coverage": {"scored_plays": 3, "total_plays": 40, "ratio": 0.075},
}

_TRAIT = {
    "emotions": {"nostalgia_longing": 0.25, "anger_defiance": 0.2, "sadness_melancholy": 0.15},
    "themes": {"heartbreak_loss": 0.25, "status_ambition": 0.2},
    "coverage": {"scored_plays": 1500, "total_plays": 5800, "ratio": 0.26},
}

_SHIFTS = [
    {
        "category": "heartbreak_loss",
        "axis": "theme",
        "direction": "elevated",
        "delta": 0.06,
        "narrative": "Heartbreak and loss are more present lately.",
    },
]

_TRENDS = [
    {
        "category": "existentialism_spirituality",
        "axis": "theme",
        "direction": "rising",
        "magnitude": "notable",
        "narrative": "Existential themes are rising over recent weeks.",
    },
]

_CLUSTERS = [
    {
        "share_of_listening": 0.6,
        "dominant_emotions": [{"category": "nostalgia_longing", "weight": 0.4}],
        "dominant_themes": [{"category": "heartbreak_loss", "weight": 0.3}],
    },
]

_TEMPORAL = {
    "grounding": {
        "hours": 120.5,
        "plays": 3000,
        "qualified_plays": 2500,
        "distinct_tracks": 900,
        "distinct_artists": 250,
        "days_with_listening": 80,
    },
    "moments": {
        "song_of_season": {
            "name": "Song A",
            "artist": "Artist A",
            "qualified_plays": 25,
            "hours": 1.5,
            "uri": "spotify:track:x",
        },
        "comeback_track": {
            "name": "Song B",
            "artist": "Artist B",
            "gap_days": 45,
            "left_on": "2026-01-01",
            "returned_on": "2026-02-15",
            "qualified_plays": 8,
            "uri": "spotify:track:y",
        },
        "biggest_day": {
            "date": "2026-03-01",
            "hours": 4.2,
            "plays": 60,
            "top_track": {"name": "Song C", "artist": "Artist C", "uri": "spotify:track:z"},
        },
        "top_artist": {"artist": "Artist A", "hours": 20.0},
    },
}


def _compose(
    state=_STATE_GOOD, clusters=_CLUSTERS, clusters_status="ok", temporal=_TEMPORAL, as_of=None
):
    return compose_narrative(
        state=state,
        trait=_TRAIT,
        shifts=_SHIFTS,
        trends=_TRENDS,
        clusters=clusters,
        clusters_status=clusters_status,
        temporal=temporal,
        as_of=as_of,
    )


def test_narrative_shape():
    n = _compose()
    assert set(n) == {"headline", "key_insights", "listening_archetype", "caveats"}
    assert isinstance(n["headline"], str) and n["headline"]
    assert all(isinstance(i, str) for i in n["key_insights"])
    assert all(isinstance(c, str) for c in n["caveats"])


def test_headline_uses_state_when_coverage_good():
    n = _compose()
    assert n["headline"].startswith("Lately")
    assert "nostalgic" in n["headline"]


def test_falls_back_to_trait_when_state_thin():
    n = _compose(state=_STATE_THIN)
    assert n["headline"].startswith("Over the long run")
    # And the caveats explain why.
    assert any("too thin" in c for c in n["caveats"])


def test_archetype_from_dominant_cluster():
    n = _compose()
    arch = n["listening_archetype"]
    assert arch["source"] == "cluster"
    assert arch["dominant_emotion"] == "nostalgia_longing"
    assert arch["name"] == "the backward glance"


def test_archetype_falls_back_to_trait_without_clusters():
    n = _compose(clusters=[])
    assert n["listening_archetype"]["source"] == "trait_window"


def test_insights_include_grounding_and_moments():
    n = _compose()
    joined = " ".join(n["key_insights"])
    assert "120.5 hours" in joined
    assert "Song A" in joined  # song of the season
    assert "Song B" in joined  # comeback track


def test_caveats_flag_clusters_and_stale_anchor():
    n = _compose(
        clusters_status="insufficient_audio_data",
        as_of={"as_of": "2026-05-22T23:22:05+00:00", "anchor": "latest_play"},
    )
    joined = " ".join(n["caveats"])
    assert "clusters are unavailable" in joined
    assert "last recorded play" in joined
    assert "2026-05-22" in joined


def test_low_trait_coverage_caveat_always_present():
    n = _compose()
    assert any("26%" in c for c in n["caveats"])
