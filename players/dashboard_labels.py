"""Compatibility shim that re-exports the canonical label metadata."""

from __future__ import annotations

from .labels import (
    CATEGORY_GROUPS,
    CATEGORY_LABELS,
    COLUMN_LABELS,
    MATCH_METRIC_CATEGORIES,
    METRIC_CATEGORIES,
    PLAYER_INFO_FIELDS,
    POSITION_LABELS,
    SEASON_METRIC_CATEGORIES,
    metric_definition,
)

__all__ = [
    "CATEGORY_GROUPS",
    "CATEGORY_LABELS",
    "COLUMN_LABELS",
    "MATCH_METRIC_CATEGORIES",
    "METRIC_CATEGORIES",
    "PLAYER_INFO_FIELDS",
    "POSITION_LABELS",
    "SEASON_METRIC_CATEGORIES",
    "metric_definition",
]
