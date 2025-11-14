from __future__ import annotations

import json
from collections import defaultdict
from typing import Iterable, Sequence

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render

from .data_access import (
    MatchRow,
    SeasonRow,
    fetch_competitions,
    fetch_match_rows,
    fetch_player_positions,
    fetch_players,
    fetch_positions,
    fetch_season_rows,
)
from .labels import (
    CATEGORY_LABELS,
    COLUMN_LABELS,
    MATCH_METRIC_CATEGORIES,
    PLAYER_INFO_FIELDS,
    POSITION_LABELS,
    SEASON_METRIC_CATEGORIES,
    metric_definition,
)

DEFAULT_SEASON_METRICS: list[str] = [
    "npg_90",
    "npxgxa_90",
    "shots_key_passes_90",
    "carries_90",
    "padj_pressures_90",
    "dribble_ratio",
]
DEFAULT_MATCH_METRICS: list[str] = ["np_xg", "goals", "assists", "xgchain"]

PLAYER_INFO_KEYS: list[str] = [key for key, _label in PLAYER_INFO_FIELDS]


def _metric_tuple(metric: str) -> tuple[str, str, str]:
    label, _legend, fmt = metric_definition(metric)
    fmt_key = "percent" if fmt == "percent" else "number"
    return metric, label, fmt_key


@login_required
def dashboard(request):
    """Zentrale Spieler-Ansicht: Filter + Vergleichsgrafiken."""

    competition_choices = fetch_competitions()
    selected_comp_key = request.GET.get("competition")
    valid_comp_keys = [c.key for c in competition_choices]
    if selected_comp_key not in valid_comp_keys:
        selected_comp_key = competition_choices[0].key if competition_choices else None

    selected_competition_id: int | None = None
    selected_season_id: int | None = None
    if selected_comp_key:
        selected_competition_id, selected_season_id = map(int, selected_comp_key.split(":"))

    available_positions = fetch_positions(selected_competition_id, selected_season_id)
    selected_position = request.GET.get("position") or ""
    if selected_position and selected_position not in available_positions:
        selected_position = ""

    players = fetch_players(
        selected_competition_id,
        selected_season_id,
        None,
    )
    position_lookup = fetch_player_positions(
        selected_competition_id,
        selected_season_id,
        [int(player["player_id"]) for player in players],
    )
    _annotate_player_positions(players, position_lookup)
    if selected_position:
        players = [
            player
            for player in players
            if _player_matches_position(player, selected_position)
        ]

    requested_players = request.GET.getlist("players")
    available_player_ids = [str(player["player_id"]) for player in players]
    if not requested_players:
        requested_players = available_player_ids[:2]
    selected_player_ids = [pid for pid in requested_players if pid in available_player_ids]

    season_metric_options = _metric_category_payload(SEASON_METRIC_CATEGORIES)
    match_metric_options = _metric_category_payload(MATCH_METRIC_CATEGORIES)

    requested_season_metrics = request.GET.getlist("season_metrics")
    requested_match_metrics = request.GET.getlist("match_metrics")
    season_metric_keys = _resolve_metric_selection(
        requested_season_metrics,
        SEASON_METRIC_CATEGORIES,
        DEFAULT_SEASON_METRICS,
    )
    match_metric_keys = _resolve_metric_selection(
        requested_match_metrics,
        MATCH_METRIC_CATEGORIES,
        DEFAULT_MATCH_METRICS,
    )
    season_metrics = [_metric_tuple(metric) for metric in season_metric_keys]
    match_metrics = [
        (metric, metric_definition(metric)[0]) for metric in match_metric_keys
    ]

    season_stats = _load_season_stats(
        selected_competition_id,
        selected_season_id,
        [int(pid) for pid in selected_player_ids],
        season_metric_keys,
    )
    match_stats = _load_match_stats(
        selected_competition_id,
        selected_season_id,
        [int(pid) for pid in selected_player_ids],
        match_metric_keys,
    )

    season_chart = _build_season_chart_payload(season_stats, season_metrics)
    match_chart = _build_match_chart_payload(match_stats, match_metrics)

    positions = [
        {
            "value": pos,
            "label": POSITION_LABELS.get(pos, pos),
        }
        for pos in available_positions
    ]
    selected_player_meta = _selected_player_meta(
        players,
        selected_player_ids,
        season_stats,
    )

    context = {
        "competition_choices": competition_choices,
        "players": players,
        "positions": positions,
        "selected_competition": selected_comp_key,
        "selected_position": selected_position,
        "selected_players": selected_player_ids,
        "season_stats": season_stats,
        "season_metrics": season_metrics,
        "match_metrics": match_metrics,
        "season_category_sections": _selected_metric_sections(
            season_metric_keys, SEASON_METRIC_CATEGORIES
        ),
        "match_category_sections": _selected_metric_sections(
            match_metric_keys, MATCH_METRIC_CATEGORIES
        ),
        "season_metric_options": season_metric_options,
        "match_metric_options": match_metric_options,
        "selected_season_metrics": season_metric_keys,
        "selected_match_metrics": match_metric_keys,
        "player_info_fields": PLAYER_INFO_FIELDS,
        "selected_player_meta": selected_player_meta,
        "season_chart_json": json.dumps(season_chart, cls=DjangoJSONEncoder),
        "match_chart_json": json.dumps(match_chart, cls=DjangoJSONEncoder),
    }
    return render(request, "players/dashboard.html", context)


def _load_season_stats(
    competition_id: int | None,
    season_id: int | None,
    player_ids: Iterable[int],
    metrics: Sequence[str],
):
    if (
        competition_id is None
        or season_id is None
        or not player_ids
        or not metrics
    ):
        return []

    metric_list = list(metrics)
    info_metrics = [key for key in PLAYER_INFO_KEYS if key not in metric_list]
    query_metrics = metric_list + info_metrics
    player_ids_list = list(player_ids)
    rows = fetch_season_rows(
        competition_id=int(competition_id),
        season_id=int(season_id),
        player_ids=player_ids_list,
        metrics=query_metrics,
    )

    positions = fetch_player_positions(
        competition_id,
        season_id,
        player_ids_list,
    )
    for row in rows:
        row.metrics = {metric: row.metrics.get(metric) for metric in query_metrics}
        lookup = positions.get(row.player_id)
        if lookup:
            row.primary_position = lookup.get("primary_position") or row.primary_position
            row.secondary_position = lookup.get("secondary_position") or row.secondary_position
    return rows


def _load_match_stats(
    competition_id: int | None,
    season_id: int | None,
    player_ids: Iterable[int],
    metrics: Sequence[str],
):
    if (
        competition_id is None
        or season_id is None
        or not player_ids
        or not metrics
    ):
        return []

    metric_list = list(metrics)
    rows = fetch_match_rows(
        competition_id=int(competition_id),
        season_id=int(season_id),
        player_ids=list(player_ids),
        metrics=metric_list,
    )
    for row in rows:
        row.metrics = {metric: row.metrics.get(metric) for metric in metric_list}
    return rows


def _build_season_chart_payload(
    season_stats: Sequence[SeasonRow],
    season_metrics: Sequence[tuple[str, str, str]],
):
    labels = [label for _, label, _ in season_metrics]
    formats = [fmt for _, _, fmt in season_metrics]
    datasets = []
    for stat in season_stats:
        datasets.append(
            {
                "label": stat.player_name or f"Player {stat.player_id}",
                "data": [
                    _chart_value(getattr(stat, metric))
                    for metric, _, _ in season_metrics
                ],
            }
        )
    return {"labels": labels, "datasets": datasets, "formats": formats}


def _build_match_chart_payload(
    match_stats: Sequence[MatchRow],
    match_metrics: Sequence[tuple[str, str]],
):
    if not match_stats:
        return {"labels": [], "metrics": {}, "players": []}

    dates = sorted({stat.match_date for stat in match_stats if stat.match_date})
    labels = [date.strftime("%Y-%m-%d") for date in dates]
    metric_values: dict[str, dict[int, dict[str, float | None]]] = {
        metric: defaultdict(dict) for metric, _ in match_metrics
    }
    player_names: dict[int, str] = {}

    for stat in match_stats:
        date = stat.match_date
        if not date or date not in dates:
            continue
        player_names[stat.player_id] = stat.player_name or f"Player {stat.player_id}"
        for metric, _ in match_metrics:
            metric_values[metric][stat.player_id][date.strftime("%Y-%m-%d")] = _chart_value(
                getattr(stat, metric)
            )

    metric_payload = {}
    for metric, label in match_metrics:
        datasets = []
        for player_id in sorted(player_names, key=lambda pid: player_names[pid]):
            player_name = player_names[player_id]
            player_data = metric_values[metric].get(player_id, {})
            datasets.append(
                {
                    "label": player_name,
                    "data": [player_data.get(date_label) for date_label in labels],
                }
            )
        metric_payload[metric] = {"label": label, "datasets": datasets}
    return {"labels": labels, "metrics": metric_payload, "players": list(player_names.values())}


def _metric_category_payload(metric_categories: dict[str, Sequence[str]]):
    payload: list[dict[str, object]] = []
    for category, metrics in metric_categories.items():
        payload.append(
            {
                "key": category,
                "label": CATEGORY_LABELS.get(category, category),
                "metrics": [
                    {
                        "key": metric,
                        "label": COLUMN_LABELS.get(metric, (metric, None, "float"))[0],
                        "legend": COLUMN_LABELS.get(metric, (metric, None, "float"))[1],
                    }
                    for metric in metrics
                ],
            }
        )
    return payload


def _selected_metric_sections(
    metric_keys: Sequence[str], metric_categories: dict[str, Sequence[str]]
):
    metric_set = set(metric_keys)
    sections: list[dict[str, object]] = []
    for category, metrics in metric_categories.items():
        visible_metrics = [
            {
                "key": metric,
                "label": COLUMN_LABELS.get(metric, (metric, None, "float"))[0],
                "legend": COLUMN_LABELS.get(metric, (metric, None, "float"))[1],
            }
            for metric in metrics
            if metric in metric_set
        ]
        if visible_metrics:
            sections.append(
                {
                    "key": category,
                    "label": CATEGORY_LABELS.get(category, category),
                    "metrics": visible_metrics,
                }
            )
    return sections


def _resolve_metric_selection(
    requested: Sequence[str],
    metric_categories: dict[str, Sequence[str]],
    default: Sequence[str],
) -> list[str]:
    allowed = _all_metric_keys(metric_categories)
    valid = [metric for metric in requested if metric in allowed]
    if not valid:
        fallback = [metric for metric in default if metric in allowed]
        valid = fallback or allowed[:6]
    return valid


def _all_metric_keys(metric_categories: dict[str, Sequence[str]]) -> list[str]:
    keys: list[str] = []
    for metrics in metric_categories.values():
        keys.extend(metrics)
    return keys


def _annotate_player_positions(
    players: list[dict[str, object]],
    lookup: dict[int, dict[str, str | None]],
):
    if not lookup:
        return
    for player in players:
        player_id = player.get("player_id")
        try:
            player_id_int = int(player_id)
        except (TypeError, ValueError):
            continue
        positions = lookup.get(player_id_int)
        if not positions:
            continue
        player["primary_position"] = positions.get("primary_position")
        player["secondary_position"] = positions.get("secondary_position")


def _player_matches_position(player: dict[str, object], position: str) -> bool:
    if not position:
        return True
    position_upper = position.upper()
    primary = (player.get("primary_position") or "").upper()
    secondary = (player.get("secondary_position") or "").upper()
    return position_upper in {primary, secondary}


def _selected_player_meta(
    players: list[dict[str, object]],
    selected_ids: Sequence[str],
    season_rows: Sequence[SeasonRow],
):
    season_lookup = {str(row.player_id): row for row in season_rows}
    fallback_lookup = {str(player.get("player_id")): player for player in players}
    meta: list[dict[str, object | None]] = []
    for player_id in selected_ids:
        season_row = season_lookup.get(player_id)
        fallback = fallback_lookup.get(player_id, {})
        if not season_row and not fallback:
            continue
        player_name = (
            season_row.player_name
            if season_row
            else fallback.get("player_name")
        )
        primary = _format_position(
            _player_info_value(season_row, fallback, "primary_position")
        )
        secondary = _format_position(
            _player_info_value(season_row, fallback, "secondary_position")
        )
        info: dict[str, object | None] = {
            "player_name": player_name,
            "primary_position": primary,
            "secondary_position": secondary,
        }
        for key in PLAYER_INFO_KEYS:
            info[key] = _player_info_value(season_row, fallback, key)
        meta.append(info)
    return meta


def _player_info_value(
    season_row: SeasonRow | None,
    fallback: dict[str, object],
    key: str,
):
    if season_row:
        if hasattr(season_row, key):
            return getattr(season_row, key)
        if key in season_row.metrics:
            return season_row.metrics.get(key)
    return fallback.get(key)


def _format_position(code: object | None) -> str | None:
    if not code:
        return None
    code_str = str(code)
    return POSITION_LABELS.get(code_str, code_str)


def _chart_value(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
