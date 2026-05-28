from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SpotifyConfig:
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8080/callback"


@dataclass
class SoundNetConfig:
    api_key: str = ""
    rate_limit_per_minute: int = 60


@dataclass
class GeniusConfig:
    access_token: str = ""


@dataclass
class WindowsConfig:
    state_half_life_days: float = 3.0
    trait_half_life_days: float = 90.0


@dataclass
class EngagementWeights:
    full_play: float = 1.0
    partial_play: float = 0.7
    early_skip: float = -0.5
    boundary_skip: float = -0.25
    repeat_session: float = 0.3
    shuffle_source: float = -0.1
    library_play: float = 0.1


@dataclass
class ClusteringConfig:
    dbscan_min_pts: int = 5
    gmm_components: int = 3


@dataclass
class DepthLabel:
    threshold: float
    label: str


@dataclass
class SafetyConfig:
    active: bool = False
    rumination_density_threshold: float = 0.7
    rumination_duration_hours: int = 48


@dataclass
class ModelsConfig:
    emotion_classifier: str = "facebook/bart-large-mnli"
    semantic_embedding: str = "sentence-transformers/all-mpnet-base-v2"


@dataclass
class PathsConfig:
    data_dir: str = "data"
    db_path: str = "data/cache/orpheus.db"
    reports_dir: str = "data/output/reports"


@dataclass
class OrpheusConfig:
    spotify: SpotifyConfig = field(default_factory=SpotifyConfig)
    soundnet: SoundNetConfig = field(default_factory=SoundNetConfig)
    genius: GeniusConfig = field(default_factory=GeniusConfig)
    windows: WindowsConfig = field(default_factory=WindowsConfig)
    engagement_weights: EngagementWeights = field(default_factory=EngagementWeights)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    depth_labels: list[DepthLabel] = field(default_factory=lambda: [
        DepthLabel(0.33, "surface"),
        DepthLabel(0.66, "engaged"),
        DepthLabel(1.0, "immersive"),
    ])
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    models: ModelsConfig = field(default_factory=ModelsConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)

    _project_root: Path = field(default_factory=lambda: Path.cwd(), repr=False)

    def resolve_path(self, rel: str) -> Path:
        return self._project_root / rel

    @property
    def db_path(self) -> Path:
        return self.resolve_path(self.paths.db_path)

    @property
    def reports_dir(self) -> Path:
        return self.resolve_path(self.paths.reports_dir)

    @property
    def data_dir(self) -> Path:
        return self.resolve_path(self.paths.data_dir)

    @property
    def model_version(self) -> str:
        return f"{self.models.emotion_classifier}+{self.models.semantic_embedding}"


def _build_dataclass(cls, data: dict[str, Any] | None):
    if data is None:
        return cls()
    known = {f.name for f in cls.__dataclass_fields__.values()}
    filtered = {k: v for k, v in data.items() if k in known}
    return cls(**filtered)


def load_config(config_path: Path | None = None, project_root: Path | None = None) -> OrpheusConfig:
    if project_root is None:
        project_root = Path.cwd()

    if config_path is None:
        config_path = project_root / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            "Copy config.yaml.template to config.yaml and fill in your API credentials."
        )

    with open(config_path) as f:
        raw = yaml.safe_load(f) or {}

    depth_labels_raw = raw.get("depth_labels")
    depth_labels = [
        DepthLabel(threshold=d["threshold"], label=d["label"])
        for d in depth_labels_raw
    ] if depth_labels_raw else None

    cfg = OrpheusConfig(
        spotify=_build_dataclass(SpotifyConfig, raw.get("spotify")),
        soundnet=_build_dataclass(SoundNetConfig, raw.get("soundnet")),
        genius=_build_dataclass(GeniusConfig, raw.get("genius")),
        windows=_build_dataclass(WindowsConfig, raw.get("windows")),
        engagement_weights=_build_dataclass(EngagementWeights, raw.get("engagement_weights")),
        clustering=_build_dataclass(ClusteringConfig, raw.get("clustering")),
        safety=_build_dataclass(SafetyConfig, raw.get("safety")),
        models=_build_dataclass(ModelsConfig, raw.get("models")),
        paths=_build_dataclass(PathsConfig, raw.get("paths")),
        _project_root=project_root,
    )
    if depth_labels is not None:
        cfg.depth_labels = depth_labels

    return cfg


def validate_config(config: OrpheusConfig) -> list[str]:
    errors = []

    if config.windows.state_half_life_days <= 0:
        errors.append("windows.state_half_life_days must be positive")
    if config.windows.trait_half_life_days <= 0:
        errors.append("windows.trait_half_life_days must be positive")
    if config.clustering.dbscan_min_pts < 2:
        errors.append("clustering.dbscan_min_pts must be >= 2")
    if config.clustering.gmm_components < 1:
        errors.append("clustering.gmm_components must be >= 1")

    prev_threshold = 0.0
    for dl in config.depth_labels:
        if dl.threshold <= prev_threshold:
            errors.append(f"depth_labels thresholds must be ascending (got {dl.threshold} after {prev_threshold})")
        prev_threshold = dl.threshold

    if config.safety.rumination_density_threshold <= 0 or config.safety.rumination_density_threshold > 1:
        errors.append("safety.rumination_density_threshold must be in (0, 1]")
    if config.safety.rumination_duration_hours <= 0:
        errors.append("safety.rumination_duration_hours must be positive")

    return errors
