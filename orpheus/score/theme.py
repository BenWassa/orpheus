from __future__ import annotations

import logging
from collections import Counter
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

THEME_CATEGORIES = [
    "interpersonal_devotion",
    "heartbreak_loss",
    "adversity_resilience",
    "identity_autonomy",
    "status_ambition",
    "hedonism_escape",
    "place_heritage",
    "existentialism_spirituality",
]

THEME_DESCRIPTIONS = {
    "interpersonal_devotion": "romantic love, devotion, familial bonds, friendship, attachment, loyalty, togetherness",
    "heartbreak_loss": "heartbreak, loss, betrayal, unrequited love, grief, separation, abandonment",
    "adversity_resilience": "adversity, mental health, resilience, survival, depression, trauma, endurance, overcoming struggle",
    "identity_autonomy": "identity, autonomy, self-actualization, anti-conformity, rebellion, authenticity, individuality",
    "status_ambition": "status, ambition, wealth, fame, material success, competitive dominance, hustle",
    "hedonism_escape": "hedonism, party, substance use, escapism, sensory pleasure, nightlife, release",
    "place_heritage": "place, heritage, nostalgia for home, geographic identity, family roots, travel, cultural grounding",
    "existentialism_spirituality": "existentialism, mortality, spirituality, faith, meaning of life, transience, cosmic purpose",
}

_ACOUSTIC_THEME_HEURISTIC = {
    "existentialism_spirituality": {"low_valence": True, "low_energy": True},
    "hedonism_escape": {"high_valence": True, "high_energy": True},
    "adversity_resilience": {"low_valence": True, "high_energy": True},
    "interpersonal_devotion": {"high_valence": True, "low_energy": True},
}


class ThemeScorer:
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        self._model_name = model_name
        self._model = None
        self._ref_embeddings: dict[str, Any] = {}

    def _load_model(self):
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
            self._precompute_references()
            logger.info("Loaded theme scorer: %s", self._model_name)
        except Exception as e:
            logger.warning("Failed to load MPNet model: %s. Theme scoring disabled.", e)
            self._model = None

    def _precompute_references(self):
        descriptions = [THEME_DESCRIPTIONS[cat] for cat in THEME_CATEGORIES]
        embeddings = self._model.encode(descriptions, normalize_embeddings=True)
        for cat, emb in zip(THEME_CATEGORIES, embeddings):
            self._ref_embeddings[cat] = emb

    def score_track(
        self,
        lyrics: str | None,
        artist_prior: dict | None = None,
        audio_features: dict | None = None,
    ) -> dict[str, Any]:
        lyrical_scores = self._score_lyrical(lyrics)

        if lyrical_scores is not None:
            scores = lyrical_scores
            confidence = 0.75
        elif audio_features is not None:
            scores = self._acoustic_heuristic(audio_features)
            confidence = 0.3
        else:
            scores = {cat: 1.0 / len(THEME_CATEGORIES) for cat in THEME_CATEGORIES}
            confidence = 0.1

        if artist_prior:
            scores = self._apply_prior(scores, artist_prior)
            confidence = min(confidence + 0.1, 1.0)

        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}

        return {"theme_scores": scores, "confidence": confidence}

    def _score_lyrical(self, lyrics: str | None) -> dict | None:
        if not lyrics or len(lyrics.strip()) < 20:
            return None

        self._load_model()
        if self._model is None:
            return None

        filtered = self._svsm_filter(lyrics)
        if len(filtered.strip()) < 20:
            return None

        try:
            text_emb = self._model.encode([filtered[:2048]], normalize_embeddings=True)[0]
        except Exception as e:
            logger.warning("MPNet encoding failed: %s", e)
            return None

        scores = {}
        for cat, ref_emb in self._ref_embeddings.items():
            similarity = float(np.dot(text_emb, ref_emb))
            scores[cat] = max(0.0, similarity)

        return scores

    def _svsm_filter(self, lyrics: str) -> str:
        lines = lyrics.strip().splitlines()
        line_counts = Counter(line.strip().lower() for line in lines)
        filtered = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if len(stripped.split()) < 3:
                continue
            if line_counts[stripped.lower()] >= 3:
                continue
            filtered.append(stripped)
        return "\n".join(filtered)

    def _acoustic_heuristic(self, audio_features: dict) -> dict:
        valence = audio_features.get("valence") or 0.5
        energy = audio_features.get("energy") or 0.5

        scores = {cat: 0.1 for cat in THEME_CATEGORIES}

        if valence < 0.3 and energy < 0.3:
            scores["existentialism_spirituality"] += 0.3
        if valence > 0.7 and energy > 0.7:
            scores["hedonism_escape"] += 0.3
        if valence < 0.3 and energy > 0.7:
            # Low valence + high energy reads as struggle/defiance. Bump the
            # matching *theme* categories only — anger/defiance is an emotion
            # category and must not be written into theme scores.
            scores["adversity_resilience"] += 0.2
            scores["identity_autonomy"] += 0.1
        if valence > 0.6 and energy < 0.4:
            scores["interpersonal_devotion"] += 0.2
            scores["place_heritage"] += 0.1

        return scores

    def _apply_prior(self, scores: dict, prior: dict) -> dict:
        result = {}
        for cat in THEME_CATEGORIES:
            likelihood = scores.get(cat, 0.0)
            prior_val = prior.get(cat, 1.0 / len(THEME_CATEGORIES))
            result[cat] = likelihood * prior_val
        return result
