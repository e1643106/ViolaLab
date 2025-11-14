"""Label- und Kategorie-Metadaten für die Players-App."""

from __future__ import annotations

from collections import OrderedDict


# ---------------------------------------------------------------------------
# Spaltenlabels / Formate
# ---------------------------------------------------------------------------

COLUMN_LABELS: dict[str, tuple[str, str | None, str]] = {
    "player_name": ("Spieler", None, "string"),
    "team_name": ("Team", None, "string"),
    "primary_position": ("Position", "Primäre Positionsgruppe", "string"),
    "secondary_position": ("Sek. Position", "Alternative Positionsgruppe", "string"),
    "npg_90": ("NP Goals / 90", "Nicht-Elfmeter-Tore pro 90 Minuten", "float"),
    "npxgxa_90": ("NP xG+xA / 90", "Nicht-Elfmeter xG + xA pro 90 Minuten", "float"),
    "shots_key_passes_90": (
        "Shots + Key Passes / 90",
        "Schüsse plus vorletzte Pässe pro 90 Minuten",
        "float",
    ),
    "carries_90": ("Carries / 90", "Ballführungen pro 90 Minuten", "float"),
    "padj_pressures_90": (
        "Pressures (adj.) / 90",
        "Positions-adjustierte Pressures pro 90 Minuten",
        "float",
    ),
    "dribble_ratio": (
        "Dribble Ratio",
        "Anteil erfolgreicher Dribblings (in %)",
        "percent",
    ),
    "np_xg": ("NP xG", "Nicht-Elfmeter Expected Goals pro Partie", "float"),
    "goals": ("Goals", "Tore in den ausgewählten Matches", "int"),
    "assists": ("Assists", "Assists in den ausgewählten Matches", "int"),
    "xgchain": (
        "xGChain",
        "xG-Beteiligung im Ballbesitz (OBV-ähnliche Kennzahl)",
        "float",
    ),
}


# ---------------------------------------------------------------------------
# Kategorien
# ---------------------------------------------------------------------------

CATEGORY_LABELS: dict[str, str] = {
    "scoring": "Torabschluss",
    "chance_creation": "Chance Creation",
    "progression": "Ballprogression",
    "pressing": "Defensivarbeit",
    "match_output": "Match-Output",
}

METRIC_CATEGORIES: dict[str, list[str]] = OrderedDict(
    {
        "scoring": ["npg_90", "np_xg", "goals"],
        "chance_creation": ["npxgxa_90", "shots_key_passes_90", "assists", "xgchain"],
        "progression": ["carries_90", "dribble_ratio"],
        "pressing": ["padj_pressures_90"],
        # "match_output" wiederholt bewusst die Match-spezifischen Kennzahlen
        "match_output": ["np_xg", "goals", "assists", "xgchain"],
    }
)

CATEGORY_GROUPS: list[tuple[str, list[str]]] = [
    ("Offensiv-Power", ["scoring", "chance_creation"]),
    ("Mit Ball", ["progression"]),
    ("Ohne Ball", ["pressing"]),
]


# ---------------------------------------------------------------------------
# Spieler-Info-Felder + Positionslabels
# ---------------------------------------------------------------------------

PLAYER_INFO_FIELDS: list[tuple[str, str]] = [
    ("team_name", "Team"),
    ("primary_position", "Primäre Position"),
    ("secondary_position", "Sekundäre Position"),
]

POSITION_LABELS: dict[str, str] = {
    "GK": "Torwart (GK)",
    "DF": "Verteidigung (DF)",
    "FB": "Außenverteidigung (FB)",
    "WB": "Wingback (WB)",
    "DM": "Defensives Mittelfeld (DM)",
    "CM": "Zentrales Mittelfeld (CM)",
    "AM": "Offensives Mittelfeld (AM)",
    "WM": "Flügel (WM)",
    "FW": "Angriff (FW)",
    "ST": "Stürmer (ST)",
}


def metric_definition(metric: str) -> tuple[str, str | None, str]:
    """Return label/legend/format triple for *metric*."""

    return COLUMN_LABELS.get(metric, (metric, None, "float"))


__all__ = [
    "COLUMN_LABELS",
    "CATEGORY_LABELS",
    "CATEGORY_GROUPS",
    "METRIC_CATEGORIES",
    "PLAYER_INFO_FIELDS",
    "POSITION_LABELS",
    "metric_definition",
]

