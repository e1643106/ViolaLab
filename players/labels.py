

from __future__ import annotations

import re

__all__ = [
    "norm_comp_key",
    "COMPETITION_LABELS",
    "SEASON_COLUMN_LABELS",
    "MATCH_COLUMN_LABELS",
    "COLUMN_LABELS",
    "SEASON_METRIC_CATEGORIES",
    "MATCH_METRIC_CATEGORIES",
    "CATEGORY_LABELS",
    "METRIC_NICHT",
    "PLAYER_INFO_FIELDS",
    "PLAYER_NICHT",
]


def norm_comp_key(value: str | None) -> str:

    if not value:
        return ""
    value = value.strip()
    value = re.sub(r"[\u2019\u2018`´']+", "'", value)
    value = re.sub(r"\s*'\s*", "'", value)
    value = re.sub(r"\s+", " ", value)
    return value.casefold()


COMPETITION_LABELS: dict[str, str] = {
    "Eredivisie": "Eredivisie, NLD 1",
    "Ligue 2": "Ligue 2, FR 2",
    "Ekstraklasa": "Ekstraklasa, POL 1",
    "La Liga 2": "La Liga 2, ESP 2",
    "Jupiler Pro League": "Jupiler Pro League, BEL 1",
    "Bundesliga": "Bundesliga, AUT 1",
    "Eerste Divisie": "Erste Divisie, NLD 2",
    "Allsvenskan": "Allsvenskan, SWE 1",
    "Czech Liga": "Czech Liga, CZE 1",
    "Superliga": "Superliga, DNK 1",
    "1. HNL": "1. HNL, HVR 1",
    "Super League": "Super League, CHE 1",
    "Eliteserien": "Eliteserien, NOR 1",
    "A-League": "A-League, AUS 1",
    "J1 League": "J1 League, JPN 1",
    "K League 1": "K League 1, KOR 1",
    "Super Liga": "Super Liga, SVK 1",
    "Championnat National": "Championnat National, FR 3",
    "Challenge League": "Challenge League, CHE 2",
    "PSL": "PSL, ZAF 1",
    "1. Division": "1. Division, DNK 2",
    "Segunda Liga": "Segunda Liga, PRT 2",
    "Challenger Pro League": "Challenger Pro League, BEL 2",
    "ligat ha'al": "Ligat Ha'Al, ISR 1",
    "2. Liga": "2. Liga, AUT 2",
    "1. SNL": "1. SNL, SVN 1",
}


SEASON_COLUMN_LABELS: dict[str, tuple[str, str | None, str]] = {
    "competition_id": ("Wettbewerbs-ID", "Eindeutige Kennung des Wettbewerbs", "int"),
    "season_id": ("Saison-ID", "Eindeutige Kennung der Saison", "int"),
    "player_id": ("Spieler-ID", "Eindeutige Kennung des Spielers", "int"),
    "team_id": ("Team-ID", "Eindeutige Kennung des Teams", "int"),
    "team_name": ("Team", None, "string"),
    "npga_90": (
        "NP-Gegentore /90",
        "Non-Penalty-Gegentore pro 90 Minuten",
        "float",
    ),
    "padj_tackles_90": (
        "Tacklings (adj.) /90",
        "An Intensität angepasste Tacklings pro 90 Minuten",
        "float",
    ),
    "padj_tackles_and_interceptions_90": (
        "Tackles+Interceptions (adj.) /90",
        "An Intensität angepasste Tackles & Interceptions pro 90 Minuten",
        "float",
    ),
    "blocks_per_shot": (
        "Blocks pro Schuss",
        "Geblockte Schüsse im Verhältnis zu zugelassenen Schüssen",
        "float",
    ),
    "backward_pass_proportion": (
        "Rückpass-Anteil",
        "Anteil der Rückpässe an allen Pässen",
        "percent",
    ),
    "sideways_pass_proportion": (
        "Querpässe-Anteil",
        "Anteil der Querpässe an allen Pässen",
        "percent",
    ),
    "op_f3_forward_pass_proportion": (
        "Off. Drittel Vorwärtspässe (%)",
        "Anteil vorwärts gespielter Pässe im offensiven Drittel",
        "percent",
    ),
    "op_f3_backward_pass_proportion": (
        "Off. Drittel Rückpässe (%)",
        "Anteil rückwärts gespielter Pässe im offensiven Drittel",
        "percent",
    ),
    "op_f3_sideways_pass_proportion": (
        "Off. Drittel Querpässe (%)",
        "Anteil quer gespielter Pässe im offensiven Drittel",
        "percent",
    ),
    "shot_on_target_ratio": (
        "Schussgenauigkeit",
        "Anteil der Schüsse aufs Tor",
        "percent",
    ),
    "conversion_ratio": (
        "Torquote",
        "Anteil der Schüsse, die zu Toren werden",
        "percent",
    ),
    "npg_90": (
        "Tore oE /90",
        "Non-Penalty-Tore pro 90 Minuten",
        "float",
    ),
    "padj_clearances_90": (
        "Klärungen (adj.) /90",
        "An Intensität angepasste Klärungsaktionen pro 90 Minuten",
        "float",
    ),
    "xgchain_90": (
        "xGChain /90",
        "xGChain-Beiträge pro 90 Minuten",
        "float",
    ),
    "op_xgbuildup_90": (
        "xGBuildup Gegner /90",
        "xGBuildup des Gegners pro 90 Minuten",
        "float",
    ),
    "shots_faced_90": (
        "Schüsse gegen /90",
        "Zugelassene Schüsse pro 90 Minuten",
        "float",
    ),
    "np_xg_faced_90": (
        "NP xG gegen /90",
        "Non-Penalty xG gegen pro 90 Minuten",
        "float",
    ),
    "np_psxg_faced_90": (
        "NP PSxG gegen /90",
        "Post-Shot xG gegen ohne Elfmeter pro 90 Minuten",
        "float",
    ),
    "xs_ratio": (
        "xS-Quote",
        "Verhältnis von gehaltenen zu erwarteten Abschlüssen",
        "float",
    ),
    "left_foot_ratio": (
        "Linker-Fuß-Anteil",
        "Anteil der Aktionen mit dem linken Fuß",
        "percent",
    ),
    "pressured_passing_ratio": (
        "Passquote unter Druck",
        "Anteil erfolgreicher Pässe unter Gegnerdruck",
        "percent",
    ),
    "passes_pressed_ratio": (
        "Angespielte unter Druck",
        "Anteil der Pässe zu Mitspielern unter Druck",
        "percent",
    ),
    "s_pass_length": (
        "Passlänge kurz",
        "Durchschnittliche Länge kurzer Pässe",
        "float",
    ),
    "p_pass_length": (
        "Passlänge mittellang",
        "Durchschnittliche Länge mittlerer Pässe",
        "float",
    ),
    "ps_pass_length": (
        "Passlänge lang",
        "Durchschnittliche Länge langer Pässe",
        "float",
    ),
    "ot_shots_faced_90": (
        "Schüsse aufs Tor gegen /90",
        "Schüsse aufs Tor des Gegners pro 90 Minuten",
        "float",
    ),
    "ot_shots_faced_ratio": (
        "Quote Schüsse aufs Tor",
        "Anteil der gegnerischen Schüsse, die aufs Tor gehen",
        "percent",
    ),
    "np_optimal_gk_dlength": (
        "Optimale GK-Distanz",
        "Empfohlene Distanz des Torwarts zur Linie",
        "float",
    ),
    "pass_into_pressure_ratio": (
        "Pässe in Druckzonen",
        "Anteil der Pässe in gegnerischen Druck",
        "percent",
    ),
    "pass_into_danger_ratio": (
        "Pässe in Gefahrzonen",
        "Anteil der Pässe in gefährliche Zonen",
        "percent",
    ),
    "appearances": (
        "Einsätze",
        "Anzahl der Spiele mit Einsatz",
        "int",
    ),
    "positive_outcome_90": (
        "Positive Aktionen /90",
        "Positive Ereignisse pro 90 Minuten",
        "float",
    ),
    "sp_assists_90": (
        "Standards-Vorlagen /90",
        "Assists aus Standards pro 90 Minuten",
        "float",
    ),
    "sp_key_passes_90": (
        "Standards-Key-Pässe /90",
        "Key Pässe aus Standards pro 90 Minuten",
        "float",
    ),
    "npxgxa_90": (
        "NP xG+xA /90",
        "Non-Penalty xG plus xA pro 90 Minuten",
        "float",
    ),
    "shots_key_passes_90": (
        "Schüsse+Key Pässe /90",
        "Summe aus Schüssen und Key Pässen pro 90 Minuten",
        "float",
    ),
    "dribble_ratio": (
        "Dribbel-Erfolgsquote",
        "Anteil erfolgreicher Dribblings",
        "percent",
    ),
    "pass_length_ratio": (
        "Passlängen-Mix",
        "Verteilung kurzer vs. langer Pässe",
        "percent",
    ),
    "pressured_pass_length_ratio": (
        "Passlängen-Mix (unter Druck)",
        "Verteilung der Passlängen unter Druck",
        "percent",
    ),
    "pressured_change_in_pass_length": (
        "Passlänge Δ unter Druck",
        "Veränderung der Passlänge unter Gegnerdruck",
        "float",
    ),
    "carries_90": (
        "Carries /90",
        "Ballführungen pro 90 Minuten",
        "float",
    ),
    "carry_ratio": (
        "Carry-Anteil",
        "Anteil von Läufen mit Ball",
        "percent",
    ),
    "carry_length": (
        "Carry-Länge",
        "Durchschnittliche Laufdistanz mit Ball",
        "float",
    ),
    "yellow_cards_90": (
        "Gelbe Karten /90",
        "Gelbe Karten pro 90 Minuten",
        "float",
    ),
    "second_yellow_cards_90": (
        "Gelb-Rot /90",
        "Gelb-Rote Karten pro 90 Minuten",
        "float",
    ),
    "red_cards_90": (
        "Rote Karten /90",
        "Rote Karten pro 90 Minuten",
        "float",
    ),
    "errors_90": (
        "Fehler /90",
        "Fehler, die zu Chancen führen, pro 90 Minuten",
        "float",
    ),
    "padj_pressures_90": (
        "Pressures (adj.) /90",
        "An Intensität angepasste Pressures pro 90 Minuten",
        "float",
    ),
    "defensive_action_regains_90": (
        "Ballgewinne nach Defensivaktionen /90",
        "Ballgewinne innerhalb von 5 Sekunden nach Defensivaktionen pro 90",
        "float",
    ),
    "counterpressure_regains_90": (
        "Ballgewinne nach Gegenpressing /90",
        "Gegenpressing-Balleroberungen pro 90 Minuten",
        "float",
    ),
    "starting_appearances": (
        "Startelf-Einsätze",
        "Anzahl der Spiele in der Startelf",
        "int",
    ),
    "average_x_pressure": (
        "Ø Position Pressures",
        "Durchschnittliche Spielfeldposition eigener Pressures",
        "float",
    ),
    "fhalf_pressures_90": (
        "Pressures vordere Hälfte /90",
        "Pressures in der gegnerischen Hälfte pro 90 Minuten",
        "float",
    ),
    "fhalf_counterpressures_90": (
        "Gegenpressing vordere Hälfte /90",
        "Gegenpressing-Aktionen in der gegnerischen Hälfte pro 90",
        "float",
    ),
    "fhalf_pressures_ratio": (
        "Pressures vordere Hälfte (%)",
        "Anteil der Pressures in der gegnerischen Hälfte",
        "percent",
    ),
    "average_x_defensive_action": (
        "Ø Position Defensivaktionen",
        "Durchschnittliche Spielfeldposition defensiver Aktionen",
        "float",
    ),
    "average_x_pass": (
        "Ø Pass-Position",
        "Durchschnittliche Spielfeldposition eigener Pässe",
        "float",
    ),
    "90s_played": (
        "Absolvierte 90er",
        "Anzahl gespielter 90-Minuten-Einheiten",

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



MATCH_COLUMN_LABELS: dict[str, tuple[str, str | None, str]] = {
    "match_id": ("Match-ID", "Eindeutige Kennung des Spiels", "int"),
    "player_id": ("Spieler-ID", "Eindeutige Kennung des Spielers", "int"),
    "team_id": ("Team-ID", "Eindeutige Kennung des Teams", "int"),
    "team_name": ("Team", None, "string"),
    "match_date": ("Spieltermin", None, "date"),
    "minutes": ("Spielminuten", "Einsatzzeit im Spiel", "int"),
    "np_xg_per_shot": (
        "NP xG pro Schuss",
        "Non-Penalty Expected Goals pro Abschluss",
        "float",
    ),
    "np_xg": ("NP xG", "Non-Penalty Expected Goals", "float"),
    "np_shots": ("Schüsse oE", "Abschlüsse ohne Elfmeter", "int"),
    "goals": ("Tore", None, "int"),
    "np_goals": ("Tore oE", "Tore ohne Elfmeter", "int"),
    "xa": ("xA", "Expected Assists", "float"),
    "key_passes": ("Key Pässe", "Vorlagen zu Abschlüssen", "int"),
    "op_key_passes": (
        "Key Pässe Gegner",
        "Vom Gegner gespielte Key Pässe",
        "int",
    ),
    "assists": ("Vorlagen", None, "int"),
    "through_balls": (
        "Steilpässe",
        "Durchgesteckte Bälle hinter die Abwehr",
        "int",
    ),
    "passes_into_box": (
        "Pässe in den Strafraum",
        "Erfolgreiche Zuspiele in den Strafraum",
        "int",
    ),
    "op_passes_into_box": (
        "Pässe in den Strafraum Gegner",
        "Erfolgreiche Strafraumpässe des Gegners",
        "int",
    ),
    "touches_inside_box": (
        "Ballkontakte Strafraum",
        "Kontakte im gegnerischen Strafraum",
        "int",
    ),
    "tackles": ("Tacklings", "Versuchte Tacklings", "int"),
    "interceptions": ("Interceptions", "Abgefangene Zuspiele", "int"),
    "possession": (
        "Ballbesitz",
        "Anteil am Spiel in Prozent",
        "percent",
    ),
    "dribbled_past": (
        "Ausgedribbelte Male",
        "Anzahl der Male, in denen der Gegenspieler vorbeikam",
        "int",
    ),
    "dribbles_faced": (
        "Dribblings gegen",
        "Versuchte Dribblings des Gegners",
        "int",
    ),
    "dribbles": ("Dribblings", "Eigene Dribbling-Versuche", "int"),
    "challenge_ratio": (
        "Erfolgsquote Zweikampf",
        "Anteil gewonnener direkten Zweikämpfe",
        "percent",
    ),
    "dispossessions": (
        "Ballverluste",
        "Verluste bei Ballführungen",
        "int",
    ),
    "long_balls": (
        "Lange Bälle",
        "Versuchte lange Pässe",
        "int",
    ),
    "successful_long_balls": (
        "Lange Bälle erfolgreich",
        "Angekommene lange Pässe",
        "int",
    ),
    "long_ball_ratio": (
        "Quote lange Bälle",
        "Anteil erfolgreicher langer Bälle",
        "percent",
    ),
    "shots_blocked": (
        "Geblockte Schüsse",
        "Vom Spieler geblockte gegnerische Abschlüsse",
        "int",
    ),
    "clearances": ("Klärungen", None, "int"),
    "aerials": ("Luftzweikämpfe", "Versuchte Kopfballduelle", "int"),
    "successful_aerials": (
        "Luftzweikämpfe gewonnen",
        "Gewonnene Kopfballduelle",
        "int",
    ),
    "aerial_ratio": (
        "Luftzweikampfquote",
        "Anteil gewonnener Luftduelle",
        "percent",
    ),
    "passes": ("Pässe", "Versuchte Pässe", "int"),
    "successful_passes": (
        "Pässe erfolgreich",
        "Angekommene Pässe",
        "int",
    ),
    "passing_ratio": (
        "Passquote",
        "Anteil erfolgreicher Pässe",
        "percent",
    ),
    "op_passes": (
        "Pässe Gegner",
        "Vom Gegner gespielte Pässe",
        "int",
    ),
    "backward_passes": (
        "Rückpässe",
        "Nach hinten gespielte Pässe",
        "int",
    ),
    "sideways_passes": (
        "Querpässe",
        "Seitlich gespielte Pässe",
        "int",
    ),
    "op_f3_passes": (
        "Pässe offensives Drittel",
        "Alle Pässe im offensiven Drittel",
        "int",
    ),
    "op_f3_forward_passes": (
        "Vorwärtspässe offensives Drittel",
        "Vorwärts gespielte Bälle im offensiven Drittel",
        "int",
    ),
    "op_f3_backward_passes": (
        "Rückpässe offensives Drittel",
        "Zurück gespielte Bälle im offensiven Drittel",
        "int",
    ),
    "op_f3_sideways_passes": (
        "Querpässe offensives Drittel",
        "Seitliche Bälle im offensiven Drittel",
        "int",
    ),
    "np_shots_on_target": (
        "Schüsse aufs Tor oE",
        "Schüsse aufs Tor ohne Elfmeter",
        "int",
    ),
    "crosses": ("Flanken", None, "int"),
    "successful_crosses": (
        "Flanken erfolgreich",
        "Angekommene Flanken",
        "int",
    ),
    "crossing_ratio": (
        "Flankenquote",
        "Anteil erfolgreicher Flanken",
        "percent",
    ),
    "penalties_won": (
        "Gewonnene Elfmeter",
        "Erzielte Strafstoßsituationen",
        "int",
    ),
    "passes_inside_box": (
        "Pässe im Strafraum",
        "Erfolgreiche Pässe innerhalb des Strafraums",
        "int",
    ),
    "op_xa": ("xA Gegner", "Expected Assists des Gegners", "float"),
    "op_assists": (
        "Vorlagen Gegner",
        "Vom Gegner erzielte Assists",
        "int",
    ),
    "pressured_long_balls": (
        "Lange Bälle unter Druck",
        "Versuchte lange Bälle unter Gegnerdruck",
        "int",
    ),
    "aggressive_actions": (
        "Aggressive Aktionen",
        "Pressures, Tackles oder Fouls direkt nach gegnerischer Ballannahme",
        "int",
    ),
    "turnovers": (
        "Turnover",
        "Ballverluste ohne Druck",
        "int",
    ),
    "crosses_into_box": (
        "Flanken in den Strafraum",
        "Flanken, die im Strafraum enden",
        "int",
    ),
    "sp_xa": (
        "xA Standards",
        "Expected Assists aus Standardsituationen",
        "float",
    ),
    "op_shots": (
        "Schüsse Gegner",
        "Alle gegnerischen Abschlüsse",
        "int",
    ),
    "touches": ("Ballkontakte", None, "int"),
    "pressure_regains": (
        "Pressing-Gewinne",
        "Ballgewinne innerhalb 5s nach eigenem Pressing",
        "int",
    ),
    "box_cross_ratio": (
        "Flanken-Anteil",
        "Anteil der Pässe in den Strafraum, die Flanken sind",
        "percent",
    ),
    "deep_progressions": (
        "Deep Progressions",
        "Aktive Fortschritte ins letzte Drittel",
        "int",
    ),
    "shot_touch_ratio": (
        "Shot-Touch-Ratio",
        "Anteil der Ballkontakte, die zu Schüssen führen",
        "percent",
    ),
    "fouls_won": ("Gezogene Fouls", None, "int"),
    "xgchain": ("xGChain", None, "float"),
    "op_xgchain": ("xGChain Gegner", None, "float"),
    "xgbuildup": ("xGBuildup", None, "float"),
    "op_xgbuildup": ("xGBuildup Gegner", None, "float"),
    "xgchain_per_possession": (
        "xGChain pro Ballbesitz",
        "xGChain-Beiträge pro eigenem Ballbesitz",
        "float",
    ),
    "op_xgchain_per_possession": (
        "xGChain Gegner/Besitz",
        "xGChain des Gegners pro Ballbesitz",
        "float",
    ),
    "xgbuildup_per_possession": (
        "xGBuildup pro Ballbesitz",
        "xGBuildup pro eigenem Ballbesitz",
        "float",
    ),
    "op_xgbuildup_per_possession": (
        "xGBuildup Gegner/Besitz",
        "xGBuildup des Gegners pro Ballbesitz",
        "float",
    ),
    "pressures": (
        "Pressures",
        "Anläufe auf den ballführenden Gegner",
        "int",
    ),
    "pressure_duration_total": (
        "Pressingdauer gesamt",
        "Gesamtdauer eigener Pressures",
        "float",
    ),
    "pressure_duration_avg": (
        "Pressingdauer Ø",
        "Durchschnittliche Dauer einer Pressure-Aktion",
        "float",
    ),
    "pressured_action_fails": (
        "Fehlschläge unter Druck",
        "Aktionen unter Druck, die misslangen",
        "int",
    ),
    "counterpressures": (
        "Gegenpressing",
        "Pressures innerhalb 5s nach Ballverlust",
        "int",
    ),
    "counterpressure_duration_total": (
        "Gegenpressingdauer gesamt",
        "Gesamtdauer aller Gegenpressing-Aktionen",
        "float",
    ),
    "counterpressure_duration_avg": (
        "Gegenpressingdauer Ø",
        "Durchschnittliche Dauer der Gegenpressing-Aktionen",
        "float",
    ),
    "counterpressured_action_fails": (
        "Fehlschläge Gegenpressing",
        "Fehlerhafte Aktionen während des Gegenpressings",
        "int",
    ),
    "obv": (
        "OBV Gesamt",
        "On-Ball Value sämtlicher Aktionen",
        "float",
    ),
    "obv_pass": (
        "OBV Pässe",
        "On-Ball Value aus Pässen",
        "float",
    ),
    "obv_shot": (
        "OBV Schüsse",
        "On-Ball Value aus Abschlüssen",
        "float",
    ),
    "obv_defensive_action": (
        "OBV Defensivaktionen",
        "On-Ball Value aus Defensivaktionen",
        "float",
    ),
    "obv_dribble_carry": (
        "OBV Dribblings",
        "On-Ball Value aus Dribblings und Carries",
        "float",
    ),
    "obv_gk": (
        "OBV Torwart",
        "On-Ball Value aus Torwartaktionen",
        "float",
    ),
    "deep_completions": (
        "Deep Completions",
        "Erfolgreiche Zuspiele nahe des Tores",
        "int",
    ),
    "ball_recoveries": (
        "Ballgewinne",
        "Lose Bälle kontrolliert aufgenommen",
        "int",
    ),
    "np_psxg": (
        "NP PSxG",
        "Post-Shot xG ohne Elfmeter",
        "float",
    ),
    "penalties_faced": (
        "Elfmeter gegen",
        "Anzahl gegnerischer Strafstöße",
        "int",
    ),
    "penalties_conceded": (
        "Verursachte Elfmeter",
        "Strafstöße, die verursacht wurden",
        "int",
    ),
    "fhalf_ball_recoveries": (
        "Ballgewinne vordere Hälfte",
        "Ballgewinne in der gegnerischen Spielfeldhälfte",
        "int",
    ),
    "defensive_actions": (
        "Defensivaktionen",
        "Tackles, Interceptions, Blocks etc.",
        "int",
    ),
    "ccaa": (
        "CCAA",
        "Combined Counter Attacking Actions",
        "int",
    ),
    "claim_success": (
        "Fangquote",
        "Erfolgsquote bei Fangaktionen des Torwarts",
        "percent",
    ),
    "da_aggressive_distance": (
        "Aggressive Distanz",
        "Durchschnittliche Distanz aggressiver Aktionen vom eigenen Tor",
        "float",
    ),
    "goals_conceded": (
        "Gegentore",
        "Anzahl kassierter Treffer",
        "int",
    ),
    "gsaa": (
        "GSAA",
        "Goals Saved Above Average",
        "float",
    ),
    "gk_positioning_error": (
        "Torwart-Positionsfehler",
        "Bewertete Positionsfehler des Torwarts",
        "float",
    ),
    "positive_outcome_score": (
        "Positive Aktionen",
        "Gesamtbewertung positiver Aktionen",
        "float",
    ),
    "npot_psxg_faced": (
        "NPOT PSxG gegen",
        "Post-Shot xG aus dem Spiel gegen",
        "float",
    ),
    "save_ratio": (
        "Paradenquote",
        "Anteil gehaltener Schüsse aufs Tor",
        "percent",
    ),
    "gsaa_ratio": (
        "GSAA Ratio",
        "Goals Saved Above Average relativ",
        "percent",
    ),
    "npot_shots_faced": (
        "Schüsse aus dem Spiel gegen",
        "Schüsse aufs Tor aus dem Spiel",
        "int",
    ),
    "unpressured_long_balls": (
        "Lange Bälle ohne Druck",
        "Versuchte lange Bälle ohne gegnerischen Druck",
        "int",
    ),
}


COLUMN_LABELS: dict[str, tuple[str, str | None, str]] = {
    **SEASON_COLUMN_LABELS,
    **MATCH_COLUMN_LABELS,
}


SEASON_METRIC_CATEGORIES: dict[str, list[str]] = {
    "overview": [
        "appearances",
        "starting_appearances",
        "90s_played",
        "positive_outcome_90",
    ],
    "shooting": [
        "npg_90",
        "shots_key_passes_90",
        "shot_on_target_ratio",
        "conversion_ratio",
        "npxgxa_90",
    ],
    "passing": [
        "backward_pass_proportion",
        "sideways_pass_proportion",
        "op_f3_forward_pass_proportion",
        "op_f3_backward_pass_proportion",
        "op_f3_sideways_pass_proportion",
        "pressured_passing_ratio",
        "passes_pressed_ratio",
        "pass_into_pressure_ratio",
        "pass_into_danger_ratio",
        "pass_length_ratio",
        "pressured_pass_length_ratio",
        "pressured_change_in_pass_length",
        "s_pass_length",
        "p_pass_length",
        "ps_pass_length",
        "average_x_pass",
    ],
    "possession": [
        "carries_90",
        "carry_ratio",
        "carry_length",
        "left_foot_ratio",
    ],
    "defending": [
        "padj_tackles_90",
        "padj_tackles_and_interceptions_90",
        "padj_clearances_90",
        "padj_pressures_90",
        "defensive_action_regains_90",
        "counterpressure_regains_90",
        "fhalf_pressures_90",
        "fhalf_counterpressures_90",
        "fhalf_pressures_ratio",
        "average_x_defensive_action",
        "average_x_pressure",
        "blocks_per_shot",
    ],
    "goalkeeping": [
        "npga_90",
        "shots_faced_90",
        "np_xg_faced_90",
        "np_psxg_faced_90",
        "ot_shots_faced_90",
        "ot_shots_faced_ratio",
        "np_optimal_gk_dlength",
        "xs_ratio",
    ],
    "set_pieces": [
        "sp_assists_90",
        "sp_key_passes_90",
    ],
    "discipline": [
        "yellow_cards_90",
        "second_yellow_cards_90",
        "red_cards_90",
        "errors_90",
    ],
}


MATCH_METRIC_CATEGORIES: dict[str, list[str]] = {
    "overview": [
        "minutes",
        "positive_outcome_score",
        "possession",
    ],
    "shooting": [
        "np_shots",
        "np_shots_on_target",
        "np_xg",
        "np_xg_per_shot",
        "np_goals",
        "goals",
        "np_psxg",
        "shot_touch_ratio",
    ],
    "chance_creation": [
        "xa",
        "sp_xa",
        "assists",
        "key_passes",
        "through_balls",
        "passes_into_box",
        "crosses",
        "successful_crosses",
        "crossing_ratio",
        "crosses_into_box",
        "passes_inside_box",
        "touches_inside_box",
        "deep_completions",
        "xgchain",
        "xgbuildup",
        "xgchain_per_possession",
        "xgbuildup_per_possession",
        "deep_progressions",
        "shot_touch_ratio",
    ],
    "possession": [
        "touches",
        "passes",
        "successful_passes",
        "passing_ratio",
        "backward_passes",
        "sideways_passes",
        "long_balls",
        "successful_long_balls",
        "long_ball_ratio",
        "pressured_long_balls",
        "unpressured_long_balls",
        "turnovers",
        "dispossessions",
    ],
    "defending": [
        "tackles",
        "interceptions",
        "clearances",
        "shots_blocked",
        "aggressive_actions",
        "pressures",
        "pressure_regains",
        "pressure_duration_total",
        "pressure_duration_avg",
        "pressured_action_fails",
        "counterpressures",
        "counterpressure_duration_total",
        "counterpressure_duration_avg",
        "counterpressured_action_fails",
        "ball_recoveries",
        "defensive_actions",
        "fhalf_ball_recoveries",
        "ccaa",
    ],
    "duels": [
        "dribbled_past",
        "dribbles_faced",
        "dribbles",
        "challenge_ratio",
        "aerials",
        "successful_aerials",
        "aerial_ratio",
        "fouls_won",
    ],
    "set_pieces": [
        "penalties_won",
        "penalties_faced",
        "penalties_conceded",
        "box_cross_ratio",
    ],
    "goalkeeping": [
        "op_shots",
        "goals_conceded",
        "save_ratio",
        "gsaa",
        "gsaa_ratio",
        "npot_shots_faced",
        "npot_psxg_faced",
        "penalties_faced",
        "claim_success",
        "da_aggressive_distance",
        "gk_positioning_error",
    ],
    "obv": [
        "obv",
        "obv_pass",
        "obv_shot",
        "obv_defensive_action",
        "obv_dribble_carry",
        "obv_gk",
    ],
    "opponent": [
        "op_key_passes",
        "op_passes_into_box",
        "op_passes",
        "op_f3_passes",
        "op_f3_forward_passes",
        "op_f3_backward_passes",
        "op_f3_sideways_passes",
        "op_xa",
        "op_assists",
        "op_shots",
        "op_xgchain",
        "op_xgbuildup",
        "op_xgchain_per_possession",
        "op_xgbuildup_per_possession",
    ],
    "discipline": [
        "turnovers",
        "pressured_action_fails",
        "counterpressured_action_fails",
    ],
}


CATEGORY_LABELS: dict[str, str] = {
    "overview": "Überblick",
    "shooting": "Torabschluss",
    "passing": "Passspiel",
    "possession": "Ballbesitz",
    "defending": "Defensive Aktionen",
    "goalkeeping": "Torhüter",
    "set_pieces": "Standards",
    "discipline": "Disziplin",
    "chance_creation": "Chancen kreieren",
    "duels": "Zweikämpfe",
    "obv": "On-Ball Value",
    "opponent": "Gegner",
}


METRIC_NICHT: dict[str, tuple[str | None, str | None, str | None]] = {
    "competition_id": ("Wettbewerbs-ID", "Eindeutige Kennung des Wettbewerbs", "int"),
    "season_id": ("Saison-ID", "Eindeutige Kennung der Saison", "int"),
    "player_id": ("Spieler-ID", "Eindeutige Kennung des Spielers", "int"),
    "team_id": ("Team-ID", "Eindeutige Kennung des Teams", "int"),
    "team_name": ("Team", None, "string"),
    "match_id": ("Match-ID", "Eindeutige Kennung des Spiels", "int"),
    "match_date": ("Spieltermin", None, "date"),
}


PLAYER_INFO_FIELDS: list[str] = [
    "team_name",
    "appearances",
    "starting_appearances",
    "90s_played",
    "npg_90",
    "npxgxa_90",
]


PLAYER_NICHT: dict[str, tuple[str, str | None, str]] = {
    "match_id": ("Match-ID", "Eindeutige Kennung des Spiels", "int"),
    "match_date": ("Spieltermin", None, "date"),
    "team_id": ("Team-ID", None, "int"),
    "team_name": ("Team", None, "string"),
}
