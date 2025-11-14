"""Raw SQL helpers for the players dashboard."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from typing import Sequence

from django.db import DatabaseError, connection
@dataclass(slots=True)
class CompetitionRecord:
    key: str
    label: str
    competition_id: int
    season_id: int
@dataclass(slots=True)
class SeasonRow:
    player_id: int
    player_name: str
    team_name: str | None
    primary_position: str | None
    secondary_position: str | None
    metrics: dict[str, float | None]
    def __getattr__(self, item: str):  # pragma: no cover - convenience for templates
        if item in self.metrics:
            return self.metrics[item]
        raise AttributeError(item)
@dataclass(slots=True)
class MatchRow:
    match_id: int
    match_date: date | None
    player_id: int
    player_name: str
    metrics: dict[str, float | None]
    def __getattr__(self, item: str):  # pragma: no cover - convenience for templates
        if item in self.metrics:
            return self.metrics[item]
        raise AttributeError(item)


PLAYER_SEASON_TABLE = "player_season_data"


@lru_cache(maxsize=None)
def _table_columns(table_name: str) -> set[str]:
    sql = """
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE UPPER(TABLE_NAME) = UPPER(%s)
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, [table_name])
            return {row[0].lower() for row in cursor.fetchall()}
    except DatabaseError:
        return set()


def _has_psd_column(column: str) -> bool:
    return column.lower() in _table_columns(PLAYER_SEASON_TABLE)


def _position_select_columns(alias: str = "psd") -> list[str]:
    columns: list[str] = []
    if _has_psd_column("primary_position"):
        columns.append(f"{alias}.primary_position")
    else:
        columns.append("NULL AS primary_position")
    if _has_psd_column("secondary_position"):
        columns.append(f"{alias}.secondary_position")
    else:
        columns.append("NULL AS secondary_position")
    return columns


def _position_expression(alias: str = "psd") -> str | None:
    expressions: list[str] = []
    if _has_psd_column("primary_position"):
        expressions.append(f"NULLIF(LTRIM(RTRIM({alias}.primary_position)), '')")
    if _has_psd_column("secondary_position"):
        expressions.append(f"NULLIF(LTRIM(RTRIM({alias}.secondary_position)), '')")
    if not expressions:
        return None
    if len(expressions) == 1:
        return expressions[0]
    return f"COALESCE({', '.join(expressions)})"
def fetch_competitions() -> list[CompetitionRecord]:
    rows = _fetch_dicts(
        """
        SELECT DISTINCT
            psd.competition_id,
            psd.season_id,
            c.competition_name,
            c.season_name
        FROM player_season_data AS psd
        LEFT JOIN competitions AS c
          ON c.competition_id = psd.competition_id
         AND c.season_id = psd.season_id
        ORDER BY psd.competition_id, psd.season_id
        """,
    )
    competitions: list[CompetitionRecord] = []
    for row in rows:
        competition_id = int(row["competition_id"])
        season_id = int(row["season_id"])
        comp_name = row.get("competition_name")
        season_name = row.get("season_name")
        if comp_name and season_name:
            label = f"{comp_name} – {season_name}"
        elif comp_name:
            label = comp_name
        else:
            label = f"Competition {competition_id} / Season {season_id}"
        competitions.append(
            CompetitionRecord(
                key=f"{competition_id}:{season_id}",
                label=label,
                competition_id=competition_id,
                season_id=season_id,
            )
        )
    return competitions

def fetch_teams(competition_id: int | None, season_id: int | None) -> list[dict[str, object]]:
    """Historic helper – kept for backwards compatibility."""

    if competition_id is None or season_id is None:
        return []
    return _fetch_dicts(
        """
        SELECT DISTINCT
            psd.team_id,
            psd.team_name
        FROM player_season_data AS psd
        WHERE psd.competition_id = %s
          AND psd.season_id = %s
          AND psd.team_id IS NOT NULL
        ORDER BY psd.team_name
        """,
        [competition_id, season_id],
    )
def fetch_players(
    competition_id: int | None,
    season_id: int | None,
    position: str | None = None,
) -> list[dict[str, object]]:
    if competition_id is None or season_id is None:
        return []
    params: list[object] = [competition_id, season_id]
    position_filter = ""
    if position:
        clauses: list[str] = []
        if _has_psd_column("primary_position"):
            clauses.append("psd.primary_position = %s")
        if _has_psd_column("secondary_position"):
            clauses.append("psd.secondary_position = %s")
        if clauses:
            position_filter = f"""
          AND (
                {' OR '.join(clauses)}
          )
        """
            params.extend([position] * len(clauses))
    position_select_sql = ",\n            ".join(_position_select_columns())
    rows = _fetch_dicts(
        f"""
        SELECT DISTINCT
            psd.player_id,
            COALESCE(pl.player_name, CONCAT('Player ', psd.player_id)) AS player_name,
            psd.team_id,
            psd.team_name,
            {position_select_sql}
        FROM player_season_data AS psd
        LEFT JOIN players AS pl
          ON pl.player_id = psd.player_id
        WHERE psd.competition_id = %s
          AND psd.season_id = %s
          {position_filter}
        ORDER BY player_name, psd.player_id
        """,
        params,
    )
    return rows


def fetch_positions(
    competition_id: int | None, season_id: int | None
) -> list[str]:
    if competition_id is None or season_id is None:
        return []
    position_expr = _position_expression()
    if not position_expr:
        return []
    rows = _fetch_dicts(
        f"""
        SELECT DISTINCT
            {position_expr} AS position
        FROM player_season_data AS psd
        WHERE psd.competition_id = %s
          AND psd.season_id = %s
        ORDER BY position
        """,
        [competition_id, season_id],
    )
    return [str(row["position"]) for row in rows if row.get("position")]
def fetch_season_rows(
    competition_id: int,
    season_id: int,
    player_ids: Sequence[int],
    metrics: Sequence[str],
    team_id: int | None = None,
) -> list[SeasonRow]:
    placeholders = ", ".join(["%s"] * len(player_ids))
    where_clauses = [
        "psd.competition_id = %s",
        "psd.season_id = %s",
        f"psd.player_id IN ({placeholders})",
    ]
    params: list[object] = [competition_id, season_id]
    if team_id is not None:
        where_clauses.insert(2, "psd.team_id = %s")
        params.append(team_id)
    params.extend(player_ids)
    select_fields = [
        "psd.player_id",
        "COALESCE(pl.player_name, CONCAT('Player ', psd.player_id)) AS player_name",
        "psd.team_name",
        *_position_select_columns(),
        *[f"psd.{metric} AS {metric}" for metric in metrics],
    ]
    select_clause = ",\n            ".join(select_fields)
    rows = _fetch_dicts(
        f"""
        SELECT
            {select_clause}
        FROM player_season_data AS psd
        LEFT JOIN players AS pl
          ON pl.player_id = psd.player_id
        WHERE {' AND '.join(where_clauses)}
        ORDER BY player_name, psd.player_id
        """,
        params,
    )
    results: list[SeasonRow] = []
    for row in rows:
        metrics_map = {metric: row.get(metric) for metric in metrics}
        results.append(
            SeasonRow(
                player_id=int(row["player_id"]),
                player_name=str(row.get("player_name") or f"Player {row['player_id']}"),
                team_name=row.get("team_name"),
                primary_position=row.get("primary_position"),
                secondary_position=row.get("secondary_position"),
                metrics=metrics_map,
            )
        )
    return results
def fetch_match_rows(
    competition_id: int,
    season_id: int,
    player_ids: Sequence[int],
    metrics: Sequence[str],
    team_id: int | None = None,
) -> list[MatchRow]:
    placeholders = ", ".join(["%s"] * len(player_ids))
    metric_sql = ",\n            ".join(f"pmd.{metric} AS {metric}" for metric in metrics)
    team_filter = ""
    params: list[object] = [competition_id, season_id]
    if team_id is not None:
        team_filter = " AND pmd.team_id = %s"
        params.append(team_id)
    params.extend(player_ids)
    rows = _fetch_dicts(
        f"""
        SELECT
            pmd.match_id,
            COALESCE(m.match_date, pmd.match_date) AS match_date,
            pmd.player_id,
            COALESCE(pl.player_name, CONCAT('Player ', pmd.player_id)) AS player_name,
            {metric_sql}
        FROM player_match_data AS pmd
        INNER JOIN matches AS m
          ON m.match_id = pmd.match_id
        LEFT JOIN players AS pl
          ON pl.player_id = pmd.player_id
        WHERE m.competition_id = %s
          AND m.season_id = %s
          AND pmd.player_id IN ({placeholders})
          {team_filter}
        ORDER BY m.match_date, pmd.match_id, pmd.player_id
        """,
        params,
    )
    results: list[MatchRow] = []
    for row in rows:
        metrics_map = {metric: row.get(metric) for metric in metrics}
        results.append(
            MatchRow(
                match_id=int(row["match_id"]),
                match_date=row.get("match_date"),
                player_id=int(row["player_id"]),
                player_name=str(row.get("player_name") or f"Player {row['player_id']}"),
                metrics=metrics_map,
            )
        )
    return results
def _fetch_dicts(sql: str, params: Sequence[object] | None = None) -> list[dict[str, object]]:
    """Execute *sql* and return dicts with lowercase keys."""
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        columns = [column[0].lower() for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]