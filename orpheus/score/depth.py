from __future__ import annotations

import math
import re

from orpheus.config import DepthLabel


def score_depth(
    audio_features: dict | None,
    lyrics: str | None,
    theme_scores: dict | None = None,
    depth_labels: list[DepthLabel] | None = None,
) -> tuple[float, str]:
    signals = []

    acoustic_complexity = _acoustic_complexity(audio_features)
    if acoustic_complexity is not None:
        signals.append(acoustic_complexity)

    lexical_density = _lexical_density(lyrics)
    if lexical_density is not None:
        signals.append(lexical_density)

    topic_depth = _topic_depth(theme_scores)
    if topic_depth is not None:
        signals.append(topic_depth)

    if not signals:
        score = 0.5
    else:
        score = sum(signals) / len(signals)

    score = max(0.0, min(1.0, score))

    if depth_labels is None:
        depth_labels = [
            DepthLabel(0.33, "surface"),
            DepthLabel(0.66, "engaged"),
            DepthLabel(1.0, "immersive"),
        ]

    label = depth_labels[-1].label
    for dl in depth_labels:
        if score <= dl.threshold:
            label = dl.label
            break

    return score, label


def _acoustic_complexity(audio_features: dict | None) -> float | None:
    if audio_features is None:
        return None

    signals = []

    sc = audio_features.get("spectral_complexity")
    if sc is not None:
        signals.append(min(sc, 1.0))

    tempo = audio_features.get("tempo")
    if tempo is not None:
        deviation = abs(tempo - 120) / 120
        signals.append(min(deviation, 1.0))

    loudness = audio_features.get("loudness")
    if loudness is not None:
        dynamic_range = min(abs(loudness + 5) / 20, 1.0)
        signals.append(dynamic_range)

    acousticness = audio_features.get("acousticness")
    if acousticness is not None:
        signals.append(acousticness * 0.5)

    if not signals:
        return None

    return sum(signals) / len(signals)


_TTR_SEGMENT = 100


def _lexical_density(lyrics: str | None) -> float | None:
    if not lyrics or len(lyrics.strip()) < 20:
        return None

    words = re.findall(r"\b[a-zA-Z]+\b", lyrics.lower())
    if len(words) < 10:
        return None

    total = len(words)

    # Plain type/token ratio is length-biased: a short lyric mechanically scores
    # as more "dense" because fewer tokens means fewer chances to repeat. Use a
    # mean-segmental TTR (average TTR over fixed-size word segments) so density
    # is comparable across a 40-word chorus and a 400-word rap verse.
    base_density = _mean_segmental_ttr(words, _TTR_SEGMENT)

    avg_syllables = sum(_count_syllables(w) for w in words) / total
    syllable_weight = min(avg_syllables / 3.0, 1.0)

    return min(base_density * (0.7 + 0.3 * syllable_weight), 1.0)


def _mean_segmental_ttr(words: list[str], segment: int) -> float:
    if len(words) <= segment:
        return len(set(words)) / len(words)
    ratios = []
    for i in range(0, len(words) - segment + 1, segment):
        chunk = words[i : i + segment]
        ratios.append(len(set(chunk)) / len(chunk))
    # Ignore a trailing partial segment to keep every ratio over the same token
    # count; if the text was shorter than one segment we already returned above.
    return sum(ratios) / len(ratios)


def _count_syllables(word: str) -> int:
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def _topic_depth(theme_scores: dict | None) -> float | None:
    if not theme_scores:
        return None

    values = list(theme_scores.values())
    total = sum(values)
    if total <= 0:
        return None

    probs = [v / total for v in values]
    entropy = -sum(p * math.log(p + 1e-10) for p in probs)
    max_entropy = math.log(len(probs))

    if max_entropy <= 0:
        return None

    return entropy / max_entropy
