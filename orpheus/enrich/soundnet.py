from __future__ import annotations

import logging
import time

import requests

logger = logging.getLogger(__name__)

_MAX_RETRIES = 5
_BACKOFF_BASE = 1

_HOST = "track-analysis.p.rapidapi.com"
_BASE_URL = f"https://{_HOST}/pktx/spotify"


class SoundNetClient:
    def __init__(self, api_key: str, rate_limit_per_minute: int = 60):
        self._api_key = api_key
        self._min_interval = 60.0 / rate_limit_per_minute
        self._last_request_time = 0.0
        self._session = requests.Session()

    def fetch_audio_features(self, track_uri: str) -> dict | None:
        spotify_id = track_uri.split(":")[-1] if ":" in track_uri else track_uri

        self._rate_limit()

        for attempt in range(_MAX_RETRIES):
            try:
                resp = self._session.get(
                    f"{_BASE_URL}/{spotify_id}",
                    headers={
                        "Content-Type": "application/json",
                        "X-RapidAPI-Key": self._api_key,
                        "X-RapidAPI-Host": _HOST,
                    },
                    timeout=30,
                )

                if resp.status_code == 200:
                    data = resp.json()
                    return self._normalize(data)
                elif resp.status_code == 404:
                    logger.debug("Track not found in Track Analysis API: %s", spotify_id)
                    return None
                elif resp.status_code in (429, 503):
                    wait = _BACKOFF_BASE * (2 ** attempt)
                    logger.warning("Track Analysis API %d, retrying in %ds (attempt %d/%d)",
                                   resp.status_code, wait, attempt + 1, _MAX_RETRIES)
                    time.sleep(wait)
                else:
                    logger.warning("Track Analysis API returned %d for %s", resp.status_code, spotify_id)
                    return None

            except requests.RequestException as e:
                wait = _BACKOFF_BASE * (2 ** attempt)
                logger.warning("Track Analysis API request error: %s, retrying in %ds", e, wait)
                time.sleep(wait)

        logger.error("Track Analysis API exhausted retries for %s", spotify_id)
        return None

    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def _normalize(self, data: dict) -> dict:
        # API returns 0-100 integer scales; normalise to 0.0-1.0 floats.
        # "happiness" is their valence equivalent; no arousal field — use energy as proxy.
        def _pct(val) -> float | None:
            return val / 100.0 if val is not None else None

        def _loudness(val) -> float | None:
            # Returned as string e.g. "-5 dB"; strip unit and convert.
            if val is None:
                return None
            try:
                return float(str(val).replace("dB", "").strip())
            except ValueError:
                return None

        energy = _pct(data.get("energy"))
        return {
            "valence": _pct(data.get("happiness")),
            "arousal": energy,  # best available proxy for arousal
            "tempo": data.get("tempo"),
            "key": data.get("key"),
            "mode": data.get("mode"),
            "energy": energy,
            "danceability": _pct(data.get("danceability")),
            "acousticness": _pct(data.get("acousticness")),
            "instrumentalness": _pct(data.get("instrumentalness")),
            "loudness": _loudness(data.get("loudness")),
            "spectral_centroid": None,
            "spectral_complexity": None,
            "source": "soundnet",
        }
