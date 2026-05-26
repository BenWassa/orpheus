from __future__ import annotations

from orpheus.config import OrpheusConfig


def check_rumination(state: dict, config: OrpheusConfig) -> list[dict]:
    if not config.safety.active:
        return []

    emotions = state.get("emotions", {})
    avg_depth = state.get("avg_depth", 0.0)

    negative_valence_sum = (
        emotions.get("sadness_melancholy", 0.0)
        + emotions.get("tension_anxiety", 0.0)
        + emotions.get("anger_defiance", 0.0)
    )

    if negative_valence_sum > config.safety.rumination_density_threshold and avg_depth > 0.7:
        return [{
            "type": "potential_rumination",
            "detail": (
                "Recent listening clusters densely around negative-valence, high-depth content. "
                "This is an observation, not a diagnosis."
            ),
        }]

    return []
