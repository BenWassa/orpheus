-- Migration 001: Initial schema
-- This is the baseline migration. The full schema is applied via schema.sql;
-- this file exists so the migration runner records version 1 as applied.

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);
