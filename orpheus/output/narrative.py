"""Server-side narrative composition: the "letter about yourself" layer.

Composes a deterministic, template-based narrative object from the signals the
pipeline already computed — windows, shifts, trends, clusters, and the
temporal grounding layer. No model calls; the same report always yields the
same words. The frontend contract is ``{headline, key_insights, caveats}``
(see frontend/src/lib/reportParser.ts), plus ``listening_archetype`` for
future rendering.

The voice rules come from PRODUCT.md: observational not judgmental, honest
about uncertainty, never gamified. Every sentence must trace back to a number
in the report, and the caveats state what the numbers can't support.
"""

from __future__ import annotations

# Coverage ratio below which a window's mood mixture is treated as too thin
# to headline without qualification.
LOW_COVERAGE_THRESHOLD = 0.4
# Minimum plays in a window's evidence span before its mixture is used at all.
MIN_WINDOW_PLAYS = 20

EMOTION_PHRASES = {
    "joyful_activation": "joyful, energetic music",
    "triumphant_power": "triumphant, powerful music",
    "peacefulness": "calm, peaceful music",
    "tenderness": "tender, warm music",
    "nostalgia_longing": "nostalgic, longing music",
    "sadness_melancholy": "sad, melancholic music",
    "tension_anxiety": "tense, restless music",
    "anger_defiance": "defiant, angry music",
}

THEME_PHRASES = {
    "interpersonal_devotion": "love and devotion",
    "heartbreak_loss": "heartbreak and loss",
    "adversity_resilience": "adversity and resilience",
    "identity_autonomy": "identity and independence",
    "status_ambition": "status and ambition",
    "hedonism_escape": "pleasure and escape",
    "place_heritage": "place and roots",
    "existentialism_spirituality": "meaning and the big questions",
}

# Archetype naming: keyed by the dominant emotion of the dominant cluster
# (or of the trait window when clusters are unavailable). Names are
# observational, not aspirational.
ARCHETYPES = {
    "joyful_activation": (
        "the bright current",
        "listening organized around lift — high-energy, high-warmth tracks that carry momentum",
    ),
    "triumphant_power": (
        "the ascent",
        "listening that leans on power and victory — music for pushing through and proving",
    ),
    "peacefulness": (
        "the still water",
        "listening that settles — low-intensity, warm tracks chosen for calm",
    ),
    "tenderness": (
        "the close room",
        "listening built on warmth and intimacy — soft textures, near voices",
    ),
    "nostalgia_longing": (
        "the backward glance",
        "listening that keeps returning — memory, absence, and what was",
    ),
    "sadness_melancholy": (
        "the low tide",
        "listening that sits with heaviness rather than escaping it",
    ),
    "tension_anxiety": (
        "the live wire",
        "listening with an edge — restless, agitated, unresolved",
    ),
    "anger_defiance": (
        "the raised fist",
        "listening that resists — defiance, refusal, and fight",
    ),
}


def _top(mapping: dict[str, float], n: int = 2) -> list[str]:
    return [k for k, _ in sorted(mapping.items(), key=lambda x: -x[1])[:n]]


def _coverage_ok(window: dict) -> bool:
    cov = window.get("coverage") or {}
    return (cov.get("total_plays") or 0) >= MIN_WINDOW_PLAYS and (
        cov.get("ratio") or 0.0
    ) >= LOW_COVERAGE_THRESHOLD


def compose_narrative(
    state: dict,
    trait: dict,
    shifts: list[dict],
    trends: list[dict],
    clusters: list[dict],
    clusters_status: str,
    temporal: dict | None,
    as_of: dict | None = None,
) -> dict:
    """Build the narrative object. All inputs are the aggregation-layer dicts
    (pre-formatting), so emotion/theme maps are the raw normalized mixtures.
    """
    state_usable = _coverage_ok(state) and state.get("emotions")
    primary = state if state_usable else trait
    primary_name = "recent" if state_usable else "long-term"

    headline = _headline(primary, primary_name)
    archetype = _archetype(clusters, trait)
    key_insights = _insights(state, trait, state_usable, shifts, trends, temporal, archetype)
    caveats = _caveats(state, trait, state_usable, clusters_status, as_of)

    return {
        "headline": headline,
        "key_insights": key_insights,
        "listening_archetype": archetype,
        "caveats": caveats,
    }


def _headline(window: dict, window_name: str) -> str:
    emotions = _top(window.get("emotions") or {}, 2)
    themes = _top(window.get("themes") or {}, 1)
    if not emotions:
        return "Not enough scored listening yet to read a mood."

    mood = EMOTION_PHRASES.get(emotions[0], emotions[0])
    if len(emotions) > 1:
        second = EMOTION_PHRASES.get(emotions[1], emotions[1])
        mood = f"{mood}, shaded with {second.replace(' music', '')}"

    lead = (
        "Lately you've been drawn to"
        if window_name == "recent"
        else ("Over the long run you gravitate toward")
    )
    sentence = f"{lead} {mood}"
    if themes:
        sentence += f", circling themes of {THEME_PHRASES.get(themes[0], themes[0])}"
    return sentence + "."


def _archetype(clusters: list[dict], trait: dict) -> dict | None:
    dominant_emotion = None
    source = None

    if clusters:
        top_cluster = max(clusters, key=lambda c: c.get("share_of_listening", 0.0))
        dom = top_cluster.get("dominant_emotions") or []
        if dom:
            dominant_emotion = dom[0].get("category")
            source = "cluster"

    if dominant_emotion is None:
        emotions = _top(trait.get("emotions") or {}, 1)
        if not emotions:
            return None
        dominant_emotion = emotions[0]
        source = "trait_window"

    if dominant_emotion not in ARCHETYPES:
        return None
    name, description = ARCHETYPES[dominant_emotion]
    return {
        "name": name,
        "description": description,
        "dominant_emotion": dominant_emotion,
        "source": source,
    }


def _insights(
    state: dict,
    trait: dict,
    state_usable: bool,
    shifts: list[dict],
    trends: list[dict],
    temporal: dict | None,
    archetype: dict | None,
) -> list[str]:
    insights: list[str] = []

    # Beat 1 — mood: recent vs long-term.
    if state_usable and shifts:
        top_shift = shifts[0]
        insights.append(top_shift["narrative"])
    elif trait.get("emotions"):
        top_two = _top(trait["emotions"], 2)
        phrases = " and ".join(EMOTION_PHRASES.get(e, e) for e in top_two)
        insights.append(f"Your long-term signature centres on {phrases}.")

    # Beat 2 — themes.
    themes = _top(trait.get("themes") or {}, 2)
    if themes:
        phrases = " and ".join(THEME_PHRASES.get(t, t) for t in themes)
        insights.append(f"The themes you return to most are {phrases}.")

    # Beat 3 — grounding: hours, people, songs (full-coverage numbers).
    if temporal and temporal.get("grounding", {}).get("plays"):
        g = temporal["grounding"]
        insights.append(
            f"You spent about {g['hours']} hours here across {g['plays']} plays — "
            f"{g['distinct_tracks']} tracks by {g['distinct_artists']} artists."
        )
        moments = temporal.get("moments") or {}
        song = moments.get("song_of_season")
        if song and song.get("qualified_plays", 0) >= 3:
            insights.append(
                f"The song of this season: “{song['name']}” by {song['artist']} "
                f"({song['qualified_plays']} full listens)."
            )
        comeback = moments.get("comeback_track")
        if comeback:
            insights.append(
                f"You came back to “{comeback['name']}” by {comeback['artist']} "
                f"after {comeback['gap_days']} days away."
            )

    # Beat 4 — movement: strongest multi-week trend.
    if trends:
        insights.append(trends[0]["narrative"])

    # Beat 5 — archetype.
    if archetype:
        insights.append(
            f"If this listening had a name, it would be “{archetype['name']}” — "
            f"{archetype['description']}."
        )

    return insights


def _caveats(
    state: dict,
    trait: dict,
    state_usable: bool,
    clusters_status: str,
    as_of: dict | None,
) -> list[str]:
    caveats: list[str] = []

    if not state_usable:
        cov = state.get("coverage") or {}
        caveats.append(
            "The recent window is too thin to headline "
            f"({cov.get('scored_plays', 0)} of {cov.get('total_plays', 0)} recent plays scored); "
            "this reading leans on the long-term window instead."
        )
    else:
        cov = state.get("coverage") or {}
        if (cov.get("ratio") or 0) < 0.75:
            caveats.append(
                f"The recent mood is based on {cov.get('scored_plays', 0)} of "
                f"{cov.get('total_plays', 0)} recent plays — the unscored remainder could shift it."
            )

    trait_cov = trait.get("coverage") or {}
    if (trait_cov.get("ratio") or 0) < LOW_COVERAGE_THRESHOLD:
        caveats.append(
            f"Only {round((trait_cov.get('ratio') or 0) * 100)}% of long-term plays are scored; "
            "the long-term signature is a partial reading."
        )

    if clusters_status != "ok":
        caveats.append(
            "Listening clusters are unavailable — most tracks lack audio features, "
            "so no valence/energy clustering was possible."
        )

    if as_of and as_of.get("anchor") == "latest_play":
        caveats.append(
            f"Windows are anchored to your last recorded play ({as_of.get('as_of', '')[:10]}), "
            "not today — the export ends there."
        )

    caveats.append(
        "The energy axis is Spotify's energy feature, a proxy for arousal, not measured arousal."
    )
    caveats.append(
        "Sometimes a song is just a song — these are patterns in what you played, not a diagnosis."
    )
    return caveats
