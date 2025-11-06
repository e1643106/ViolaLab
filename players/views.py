from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.shortcuts import render

from teams.models import Competition

from .models import PlayerMatchStat, PlayerSeasonStat


@dataclass(slots=True)
class CompetitionChoice:
    key: str
    label: str
    competition_id: int
    season_id: int


SEASON_METRICS: list[tuple[str, str, str]] = [
    ("npg_90", "NP Goals / 90", "number"),
    ("npxgxa_90", "NP xG+xA / 90", "number"),
    ("shots_key_passes_90", "Shots + Key Passes / 90", "number"),
    ("carries_90", "Carries / 90", "number"),
    ("padj_pressures_90", "Pressures (adj.) / 90", "number"),
    ("dribble_ratio", "Dribble Ratio", "percent"),
]

MATCH_METRICS: list[tuple[str, str]] = [
    ("np_xg", "NP xG"),
    ("goals", "Goals"),
    ("assists", "Assists"),
    ("xgchain", "xGChain"),
]


@login_required
def dashboard(request):
    """Zentrale Spieler-Ansicht: Filter + Vergleichsgrafiken."""

    competition_choices = _load_competition_choices()
    selected_comp_key = request.GET.get("competition")
    valid_comp_keys = [c.key for c in competition_choices]
    if selected_comp_key not in valid_comp_keys:
        selected_comp_key = competition_choices[0].key if competition_choices else None

    selected_competition_id: int | None = None
    selected_season_id: int | None = None
    if selected_comp_key:
        selected_competition_id, selected_season_id = map(int, selected_comp_key.split(":"))

    teams = _load_teams(selected_competition_id, selected_season_id)
    selected_team = request.GET.get("team")
    team_choices = [str(team["team_id"]) for team in teams if team["team_id"] is not None]
    if selected_team not in team_choices:
        selected_team = team_choices[0] if team_choices else None

    players = _load_players(selected_competition_id, selected_season_id, selected_team)
    requested_players = request.GET.getlist("players")
    available_player_ids = [str(player["player_id"]) for player in players]
    if not requested_players:
        requested_players = available_player_ids[:2]
    selected_player_ids = [pid for pid in requested_players if pid in available_player_ids]

    season_stats = _load_season_stats(
        selected_competition_id,
        selected_season_id,
        selected_team,
        [int(pid) for pid in selected_player_ids],
    )
    match_stats = _load_match_stats(
        selected_competition_id,
        selected_season_id,
        selected_team,
        [int(pid) for pid in selected_player_ids],
    )

    season_chart = _build_season_chart_payload(season_stats)
    match_chart = _build_match_chart_payload(match_stats)

    context = {
        "competition_choices": competition_choices,
        "teams": teams,
        "players": players,
        "selected_competition": selected_comp_key,
        "selected_team": selected_team,
        "selected_players": selected_player_ids,
        "season_stats": season_stats,
        "season_metrics": SEASON_METRICS,
        "match_metrics": MATCH_METRICS,
        "season_chart_json": json.dumps(season_chart, cls=DjangoJSONEncoder),
        "match_chart_json": json.dumps(match_chart, cls=DjangoJSONEncoder),
    }
    return render(request, "players/dashboard.html", context)


def _load_competition_choices() -> list[CompetitionChoice]:
    pairs = list(
        PlayerSeasonStat.objects.values_list("competition_id", "season_id").distinct()
    )
    if not pairs:
        return []

    comp_ids = {c_id for c_id, _ in pairs}
    season_ids = {s_id for _, s_id in pairs}
    competitions = Competition.objects.filter(
        competition_id__in=comp_ids,
        season_id__in=season_ids,
    )
    comp_map = {
        (c.competition_id, c.season_id): c for c in competitions
    }

    choices: list[CompetitionChoice] = []
    for comp_id, season_id in sorted(pairs, key=lambda pair: (pair[0], pair[1])):
        comp = comp_map.get((comp_id, season_id))
        label = (
            f"{comp.competition_name} – {comp.season_name}"
            if comp
            else f"Competition {comp_id} / Season {season_id}"
        )
        choices.append(
            CompetitionChoice(
                key=f"{comp_id}:{season_id}",
                label=label,
                competition_id=comp_id,
                season_id=season_id,
            )
        )
    return choices


def _load_teams(competition_id: int | None, season_id: int | None):
    if competition_id is None or season_id is None:
        return []
    qs = (
        PlayerSeasonStat.objects.filter(
            competition_id=competition_id,
            season_id=season_id,
        )
        .values("team_id", "team_name")
        .distinct()
        .order_by("team_name")
    )
    return list(qs)


def _load_players(
    competition_id: int | None,
    season_id: int | None,
    team_id: str | None,
):
    if competition_id is None or season_id is None or team_id is None:
        return []
    qs = (
        PlayerSeasonStat.objects.filter(
            competition_id=competition_id,
            season_id=season_id,
            team_id=int(team_id),
        )
        .select_related("player")
        .values(
            "player_id",
            "player__player_name",
        )
        .order_by("player__player_name")
    )
    return [
        {
            "player_id": row["player_id"],
            "player_name": row["player__player_name"] or f"Player {row['player_id']}",
        }
        for row in qs
    ]


def _load_season_stats(
    competition_id: int | None,
    season_id: int | None,
    team_id: str | None,
    player_ids: Iterable[int],
):
    if competition_id is None or season_id is None or team_id is None or not player_ids:
        return []
    qs = (
        PlayerSeasonStat.objects.select_related("player")
        .filter(
            competition_id=competition_id,
            season_id=season_id,
            team_id=int(team_id),
            player_id__in=list(player_ids),
        )
        .order_by("player__player_name")
    )
    return list(qs)


def _load_match_stats(
    competition_id: int | None,
    season_id: int | None,
    team_id: str | None,
    player_ids: Iterable[int],
):
    if competition_id is None or season_id is None or team_id is None or not player_ids:
        return []
    filters = Q(player_id__in=list(player_ids)) & Q(team_id=int(team_id))
    qs = (
        PlayerMatchStat.objects.select_related("player", "match", "match__competition")
        .filter(filters)
        .filter(
            match__competition__competition_id=competition_id,
            match__competition__season_id=season_id,
        )
        .order_by("match__match_date", "match_id")
    )
    return list(qs)


def _build_season_chart_payload(season_stats: list[PlayerSeasonStat]):
    labels = [label for _, label, _ in SEASON_METRICS]
    formats = [fmt for _, _, fmt in SEASON_METRICS]
    datasets = []
    for stat in season_stats:
        datasets.append(
            {
                "label": stat.player.player_name or f"Player {stat.player_id}",
                "data": [
                    _chart_value(getattr(stat, metric))
                    for metric, _, _ in SEASON_METRICS
                ],
            }
        )
    return {"labels": labels, "datasets": datasets, "formats": formats}


def _build_match_chart_payload(match_stats: list[PlayerMatchStat]):
    if not match_stats:
        return {"labels": [], "metrics": {}, "players": []}

    dates = sorted(
        {
            stat.match.match_date if stat.match and stat.match.match_date else stat.match_date
            for stat in match_stats
            if (stat.match and stat.match.match_date) or stat.match_date
        }
    )
    labels = [date.strftime("%Y-%m-%d") for date in dates]

    metric_values: dict[str, dict[int, dict[str, float | None]]] = {
        metric: defaultdict(dict) for metric, _ in MATCH_METRICS
    }
    player_names: dict[int, str] = {}

    for stat in match_stats:
        date = stat.match.match_date if stat.match and stat.match.match_date else stat.match_date
        if date not in dates:
            continue
        player_names[stat.player_id] = stat.player.player_name or f"Player {stat.player_id}"
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


def _chart_value(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
