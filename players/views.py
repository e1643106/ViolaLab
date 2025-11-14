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
    fetch_players,
    fetch_positions,
    fetch_season_rows,
)
<<<<<<< ours
from .dashboard_labels import (
=======
from .labels import (
>>>>>>> theirs
    CATEGORY_GROUPS,
    CATEGORY_LABELS,
    COLUMN_LABELS,
    METRIC_CATEGORIES,
    PLAYER_INFO_FIELDS,
    POSITION_LABELS,
    metric_definition,
)

SEASON_METRIC_KEYS: list[str] = [
    "npg_90",
    "npxgxa_90",
    "shots_key_passes_90",
    "carries_90",
    "padj_pressures_90",
    "dribble_ratio",
]
MATCH_METRIC_KEYS: list[str] = ["np_xg", "goals", "assists", "xgchain"]


def _metric_tuple(metric: str) -> tuple[str, str, str]:
    label, _legend, fmt = metric_definition(metric)
    fmt_key = "percent" if fmt == "percent" else "number"
    return metric, label, fmt_key


SEASON_METRICS: list[tuple[str, str, str]] = [_metric_tuple(metric) for metric in SEASON_METRIC_KEYS]
MATCH_METRICS: list[tuple[str, str]] = [
    (metric, metric_definition(metric)[0]) for metric in MATCH_METRIC_KEYS
]


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
        selected_position or None,
    )

    requested_players = request.GET.getlist("players")
    available_player_ids = [str(player["player_id"]) for player in players]
    if not requested_players:
        requested_players = available_player_ids[:2]
    selected_player_ids = [pid for pid in requested_players if pid in available_player_ids]

    season_stats = _load_season_stats(
        selected_competition_id,
        selected_season_id,
        [int(pid) for pid in selected_player_ids],
    )
    match_stats = _load_match_stats(
        selected_competition_id,
        selected_season_id,
        [int(pid) for pid in selected_player_ids],
    )

    season_chart = _build_season_chart_payload(season_stats)
    match_chart = _build_match_chart_payload(match_stats)

    positions = [
        {
            "value": pos,
            "label": POSITION_LABELS.get(pos, pos),
        }
        for pos in available_positions
    ]
    selected_player_meta = _selected_player_meta(players, selected_player_ids)

    context = {
        "competition_choices": competition_choices,
        "players": players,
        "positions": positions,
        "selected_competition": selected_comp_key,
        "selected_position": selected_position,
        "selected_players": selected_player_ids,
        "season_stats": season_stats,
        "season_metrics": SEASON_METRICS,
        "match_metrics": MATCH_METRICS,
        "season_category_groups": _build_category_groups(SEASON_METRIC_KEYS),
        "match_category_groups": _build_category_groups(MATCH_METRIC_KEYS),
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
):
    if (
        competition_id is None
        or season_id is None
        or not player_ids
    ):
        return []

    season_metrics = [metric for metric, _, _ in SEASON_METRICS]
    rows = fetch_season_rows(
        competition_id=int(competition_id),
        season_id=int(season_id),
        player_ids=list(player_ids),
        metrics=season_metrics,
    )

    for row in rows:
        row.metrics = {metric: row.metrics.get(metric) for metric in season_metrics}
    return rows


def _load_match_stats(
    competition_id: int | None,
    season_id: int | None,
    player_ids: Iterable[int],
):
    if (
        competition_id is None
        or season_id is None
        or not player_ids
    ):
        return []

    match_metrics = [metric for metric, _ in MATCH_METRICS]
    rows = fetch_match_rows(
        competition_id=int(competition_id),
        season_id=int(season_id),
        player_ids=list(player_ids),
        metrics=match_metrics,
    )
    for row in rows:
        row.metrics = {metric: row.metrics.get(metric) for metric in match_metrics}
    return rows


def _build_season_chart_payload(season_stats: Sequence[SeasonRow]):
    labels = [label for _, label, _ in SEASON_METRICS]
    formats = [fmt for _, _, fmt in SEASON_METRICS]
    datasets = []
    for stat in season_stats:
        datasets.append(
            {
                "label": stat.player_name or f"Player {stat.player_id}",
                "data": [
                    _chart_value(getattr(stat, metric))
                    for metric, _, _ in SEASON_METRICS
                ],
            }
        )
    return {"labels": labels, "datasets": datasets, "formats": formats}


def _build_match_chart_payload(match_stats: Sequence[MatchRow]):
    if not match_stats:
        return {"labels": [], "metrics": {}, "players": []}

    dates = sorted({stat.match_date for stat in match_stats if stat.match_date})
    labels = [date.strftime("%Y-%m-%d") for date in dates]
    metric_values: dict[str, dict[int, dict[str, float | None]]] = {
        metric: defaultdict(dict) for metric, _ in MATCH_METRICS
    }
    player_names: dict[int, str] = {}

    for stat in match_stats:
        date = stat.match_date
        if not date or date not in dates:
            continue
        player_names[stat.player_id] = stat.player_name or f"Player {stat.player_id}"
        for metric, _ in MATCH_METRICS:
            metric_values[metric][stat.player_id][date.strftime("%Y-%m-%d")] = _chart_value(
                getattr(stat, metric)
            )

    metric_payload = {}
    for metric, label in MATCH_METRICS:
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


def _build_category_groups(metric_keys: Sequence[str]):
    metric_set = set(metric_keys)
    groups: list[dict[str, object]] = []

    seen_categories: set[str] = set()
    for group_label, categories in CATEGORY_GROUPS:
        group_categories = []
        for category in categories:
            seen_categories.add(category)
            metrics = [
                {
                    "key": metric,
                    "label": COLUMN_LABELS.get(metric, (metric, None, "float"))[0],
                    "legend": COLUMN_LABELS.get(metric, (metric, None, "float"))[1],
                }
                for metric in METRIC_CATEGORIES.get(category, [])
                if metric in metric_set
            ]
            if metrics:
                group_categories.append(
                    {
                        "key": category,
                        "label": CATEGORY_LABELS.get(category, category),
                        "metrics": metrics,
                    }
                )
        if group_categories:
            groups.append({"label": group_label, "categories": group_categories})

    extra_categories = [
        category for category in METRIC_CATEGORIES.keys() if category not in seen_categories
    ]
    for category in extra_categories:
        metrics = [
            {
                "key": metric,
                "label": COLUMN_LABELS.get(metric, (metric, None, "float"))[0],
                "legend": COLUMN_LABELS.get(metric, (metric, None, "float"))[1],
            }
            for metric in METRIC_CATEGORIES.get(category, [])
            if metric in metric_set
        ]
        if metrics:
            groups.append(
                {
                    "label": CATEGORY_LABELS.get(category, category),
                    "categories": [
                        {
                            "key": category,
                            "label": CATEGORY_LABELS.get(category, category),
                            "metrics": metrics,
                        }
                    ],
                }
            )

    return groups


def _selected_player_meta(players: list[dict[str, object]], selected_ids: Sequence[str]):
    lookup = {str(player.get("player_id")): player for player in players}
    meta = []
    for player_id in selected_ids:
        player = lookup.get(player_id)
        if not player:
            continue
        primary = _format_position(player.get("primary_position"))
        secondary = _format_position(player.get("secondary_position"))
        meta.append(
            {
                "player_name": player.get("player_name"),
                "team_name": player.get("team_name"),
                "primary_position": primary,
                "secondary_position": secondary,
            }
        )
    return meta


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
