-- Orpheus v2 database schema
-- Source: C3_data_pipeline_spec.md §2

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plays (
    id INTEGER PRIMARY KEY,
    ts TEXT NOT NULL,
    ms_played INTEGER NOT NULL,
    track_uri TEXT,
    track_name TEXT,
    artist_name TEXT,
    album_name TEXT,
    reason_start TEXT,
    reason_end TEXT,
    shuffle BOOLEAN,
    skipped BOOLEAN,
    source TEXT,
    ingested_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_plays_ts ON plays(ts);
CREATE INDEX IF NOT EXISTS idx_plays_track ON plays(track_uri);

CREATE TABLE IF NOT EXISTS tracks (
    track_uri TEXT PRIMARY KEY,
    isrc TEXT,
    mbid TEXT,
    track_name TEXT,
    primary_artist TEXT,
    featured_artists TEXT,
    album_name TEXT,
    release_date TEXT,
    popularity INTEGER,
    duration_ms INTEGER,
    is_instrumental BOOLEAN,
    enriched_at TEXT
);

CREATE TABLE IF NOT EXISTS audio_features (
    track_uri TEXT PRIMARY KEY,
    source TEXT,
    valence REAL,
    arousal REAL,
    tempo REAL,
    key INTEGER,
    mode INTEGER,
    energy REAL,
    danceability REAL,
    acousticness REAL,
    instrumentalness REAL,
    loudness REAL,
    spectral_centroid REAL,
    spectral_complexity REAL,
    fetched_at TEXT,
    FOREIGN KEY(track_uri) REFERENCES tracks(track_uri)
);

CREATE TABLE IF NOT EXISTS lyrics (
    track_uri TEXT PRIMARY KEY,
    raw_text TEXT,
    cleaned_text TEXT,
    annotations TEXT,
    has_lyrics BOOLEAN,
    fetched_at TEXT,
    FOREIGN KEY(track_uri) REFERENCES tracks(track_uri)
);

CREATE TABLE IF NOT EXISTS track_scores (
    track_uri TEXT,
    model_version TEXT,
    emotion_scores TEXT,
    theme_scores TEXT,
    depth_score REAL,
    depth_label TEXT,
    confidence TEXT,
    scored_at TEXT,
    PRIMARY KEY(track_uri, model_version),
    FOREIGN KEY(track_uri) REFERENCES tracks(track_uri)
);

CREATE TABLE IF NOT EXISTS artists (
    artist_name TEXT PRIMARY KEY,
    spotify_id TEXT,
    mbid TEXT,
    genres TEXT,
    canonical_themes TEXT,
    play_count INTEGER,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT,
    finished_at TEXT,
    config_snapshot TEXT,
    model_versions TEXT,
    play_count_processed INTEGER,
    track_count_processed INTEGER,
    output_path TEXT,
    output_hash TEXT
);
