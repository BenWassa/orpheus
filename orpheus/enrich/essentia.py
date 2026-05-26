from __future__ import annotations

from pathlib import Path


def extract_features(audio_path: Path) -> dict | None:
    raise NotImplementedError(
        "Essentia local extraction requires audio files. "
        "Most Spotify-only users will not have local audio. "
        "Use SoundNet API or Anna's Archive cache instead."
    )
