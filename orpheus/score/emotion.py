from __future__ import annotations

import logging
import math
from typing import Any


logger = logging.getLogger(__name__)

EMOTION_CATEGORIES = [
    "joyful_activation",
    "triumphant_power",
    "peacefulness",
    "tenderness",
    "nostalgia_longing",
    "sadness_melancholy",
    "tension_anxiety",
    "anger_defiance",
]

EMOTION_LABELS = {
    "joyful_activation": "joy, celebration, happiness, delight",
    "triumphant_power": "triumph, power, strength, victory",
    "peacefulness": "peace, serenity, calm, tranquility",
    "tenderness": "tenderness, affection, warmth, gentleness",
    "nostalgia_longing": "nostalgia, longing, yearning, wistfulness",
    "sadness_melancholy": "sadness, melancholy, sorrow, grief",
    "tension_anxiety": "tension, anxiety, unease, dread",
    "anger_defiance": "anger, defiance, rage, rebellion",
}

# V/A anchor coordinates from T1 taxonomy.
#
# NB: the "arousal" axis here is not measured arousal. The enrichment source
# (ReccoBeats) supplies no arousal field, so audio_import falls back to Spotify
# `energy` for every track (see enrich/audio_import.py). Treat this plane as
# valence/energy; the UI labels the vertical axis "energy" accordingly.
_VA_ANCHORS = {
    "joyful_activation": (0.8, 0.6),
    "triumphant_power": (0.6, 0.8),
    "peacefulness": (0.8, -0.7),
    "tenderness": (0.7, -0.3),
    "nostalgia_longing": (0.2, -0.4),
    "sadness_melancholy": (-0.8, -0.6),
    "tension_anxiety": (-0.6, 0.5),
    "anger_defiance": (-0.7, 0.8),
}

_NEGATIVE_VALENCE = {"sadness_melancholy", "tension_anxiety", "anger_defiance"}
_HIGH_AROUSAL = {"triumphant_power", "anger_defiance", "joyful_activation"}


class EmotionScorer:
    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        self._model_name = model_name
        self._classifier = None

    def _load_model(self):
        if self._classifier is not None:
            return
        try:
            from transformers import pipeline
            self._classifier = pipeline(
                "zero-shot-classification",
                model=self._model_name,
                device=-1,
            )
            logger.info("Loaded emotion classifier: %s", self._model_name)
        except Exception as e:
            logger.warning("Failed to load BART model: %s. Using acoustic-only scoring.", e)
            self._classifier = None

    def score_track(
        self,
        audio_features: dict | None,
        lyrics: str | None,
    ) -> dict[str, Any]:
        acoustic_scores = self._score_acoustic(audio_features)
        lyrical_scores = self._score_lyrical(lyrics)

        if lyrical_scores is not None and acoustic_scores is not None:
            fused = self._fuse(acoustic_scores, lyrical_scores)
            confidence = 0.85
        elif acoustic_scores is not None:
            fused = acoustic_scores
            confidence = 0.5
        elif lyrical_scores is not None:
            fused = lyrical_scores
            confidence = 0.6
        else:
            fused = {cat: 1.0 / len(EMOTION_CATEGORIES) for cat in EMOTION_CATEGORIES}
            confidence = 0.1

        total = sum(fused.values())
        if total > 0:
            fused = {k: v / total for k, v in fused.items()}

        return {"emotion_scores": fused, "confidence": confidence}

    def _score_acoustic(self, audio_features: dict | None) -> dict | None:
        if audio_features is None:
            return None

        valence = audio_features.get("valence")
        arousal = audio_features.get("arousal")
        if valence is None or arousal is None:
            energy = audio_features.get("energy")
            if energy is not None and arousal is None:
                arousal = energy
            if valence is None or arousal is None:
                return None

        v_scaled = valence * 2 - 1  # [0,1] → [-1,1]
        a_scaled = arousal * 2 - 1

        scores = {}
        for cat, (v_anchor, a_anchor) in _VA_ANCHORS.items():
            dist = math.sqrt((v_scaled - v_anchor) ** 2 + (a_scaled - a_anchor) ** 2)
            scores[cat] = math.exp(-dist)

        return scores

    def _score_lyrical(self, lyrics: str | None) -> dict | None:
        if not lyrics or len(lyrics.strip()) < 20:
            return None

        self._load_model()
        if self._classifier is None:
            return None

        candidate_labels = list(EMOTION_LABELS.values())
        try:
            result = self._classifier(
                lyrics[:1024],
                candidate_labels,
                multi_label=True,
            )
        except Exception as e:
            logger.warning("BART classification failed: %s", e)
            return None

        label_to_cat = {}
        for cat, label in EMOTION_LABELS.items():
            label_to_cat[label] = cat

        scores = {}
        for label, score in zip(result["labels"], result["scores"]):
            cat = label_to_cat.get(label)
            if cat:
                scores[cat] = score

        return scores

    def _fuse(self, acoustic: dict, lyrical: dict) -> dict:
        fused = {}
        for cat in EMOTION_CATEGORIES:
            a_score = acoustic.get(cat, 0.0)
            l_score = lyrical.get(cat, 0.0)

            if cat in _NEGATIVE_VALENCE:
                w_lyric, w_acoustic = 0.7, 0.3
            elif cat in _HIGH_AROUSAL:
                w_lyric, w_acoustic = 0.4, 0.6
            else:
                w_lyric, w_acoustic = 0.5, 0.5

            fused[cat] = w_lyric * l_score + w_acoustic * a_score

        return fused
