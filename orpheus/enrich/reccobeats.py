from __future__ import annotations

import logging
import time
from typing import Any

import requests

from orpheus.enrich.audio_import import spotify_id_from_track_uri

logger = logging.getLogger(__name__)


class ReccoBeatsClient:
    BASE_URL = "https://api.reccobeats.com/v1/audio-features"
    DEFAULT_RETRY_DELAY = 5.0

    def __init__(self, timeout: float = 20.0, max_retries: int = 3):
        self._timeout = timeout
        self._max_retries = max_retries

    def fetch_features(self, spotify_ids: list[str]) -> dict[str, dict | None]:
        ids = [spotify_id for spotify_id in spotify_ids if spotify_id]
        if not ids:
            return {}

        response = self._get(ids)
        if response is None:
            return {}

        results: dict[str, dict | None] = {spotify_id: None for spotify_id in ids}
        for item in _extract_items(response):
            spotify_id = spotify_id_from_track_uri(item.get("href"))
            if spotify_id is None:
                continue
            results[spotify_id] = _features_from_response(item)

        return results

    def _get(self, spotify_ids: list[str]) -> Any | None:
        try:
            attempts = 0
            while True:
                response = requests.get(
                    self.BASE_URL,
                    params={"ids": ",".join(spotify_ids)},
                    timeout=self._timeout,
                )
                if response.status_code != 429:
                    break

                attempts += 1
                if attempts > self._max_retries:
                    break

                retry_after = _retry_after_seconds(response.headers.get("Retry-After"))
                time.sleep(retry_after or self.DEFAULT_RETRY_DELAY)

            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("ReccoBeats fetch failed for %d tracks: %s", len(spotify_ids), e)
            return None


def _extract_items(payload: Any) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    if "href" in payload:
        return [payload]

    for key in ("audio_features", "features", "content", "items", "data"):
        items = payload.get(key)
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]

    return []


def _features_from_response(item: dict) -> dict:
    energy = _as_float(item.get("energy"))
    return {
        "valence": _as_float(item.get("valence")),
        "arousal": energy,
        "tempo": _as_float(item.get("tempo")),
        "key": _as_int(item.get("key")),
        "mode": _as_int(item.get("mode")),
        "energy": energy,
        "danceability": _as_float(item.get("danceability")),
        "acousticness": _as_float(item.get("acousticness")),
        "instrumentalness": _as_float(item.get("instrumentalness")),
        "loudness": _as_float(item.get("loudness")),
        "spectral_centroid": None,
        "spectral_complexity": None,
        "source": "reccobeats",
    }


def _retry_after_seconds(value: str | None) -> float:
    if value is None:
        return 0.0
    try:
        return max(0.0, float(value))
    except ValueError:
        return 0.0


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None
