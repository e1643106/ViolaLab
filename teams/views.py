# teams/views.py
''' 
Beschreibung:

- Request-Parameter (Liga/Team/Kategorien/Metrik) entgegennehmen und validieren
- Daten aus der Datenbank (TeamEventData) aggregieren/aufbereiten
- Chart-Payload (Labels, Werte, Skalenhinweise, Quantile, Benchmarks) berechnen
- eine Matchday-Übersicht (Donut + Mini-Bars) für ein einzelnes Spiel erzeugen
- HTML-Ansicht (dashboard.html) rendern ODER JSON-Payload (AJAX) zurückgeben


Wichtige Endpunkte:
- league_dashboard(request): rendert das HTML-Template inkl. initialer Chart-Daten
- league_dashboard_data(request): liefert dieselben Daten als JSON (für dynamische Updates im Frontend)



- select_related("match") reduziert N+1-Queries, wenn auf match.* Felder zugegriffen wird.
- annotate(opponent_name=Case(...)) berechnet den Gegner direkt in der Query
- _BUNDESLIGA_BENCH_CACHE cached die CSV-Referenzwerte, um Dateizugriffe zu vermeiden

'''
# ------ Standardbibs ---------------------------------------------------------------
import json
import os, csv
from pathlib import Path
from datetime import datetime
from math import floor, ceil

# ------ Django Imports ---------------------------------------------------------------
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Case, When, F, CharField
from django.http import JsonResponse
from django.shortcuts import render

# ------ Projektspezifische Labels und Kategorien ---------------------------------------
from .labels import (
    COLUMN_LABELS,              # Mapping: metric Key -> (Name, Legende, Format)
    METRIC_CATEGORIES,          # Mapping: Kategorie -> [metric Key]
    METRIC_NICHT,               # Set/Mapping nicht anzuzeigender Metriken , werden aber geladen, falls irgendwann benötigt
    CATEGORY_LABELS,            # Mapping: Kategoriename -> schönere Anzeigename
    COMPETITION_LABELS          # Mapping: Ligabezeichnung -> Labels
)

# ------ Data-Models ---------------------------------------------------------------
from .models import TeamEventData


import re

# Regex für unterschiedliche Apostroph Varianten, ggf. mehrfach hintereinander, ("LIGAT HA’’AL" -> "LIGAT HA'AL")
_APOS_MULTI = re.compile(r"[\u2019\u2018`´']+")

def _norm_comp_key(s: str | None) -> str:
    ''' Normalisiert einen Wettbewerbs-/Ligabezeichner für robuste Vergleiche

    - Trimmt Whitespace
    - Vereinheitlicht verschiedenartige Apostrophe zu '\"
    - Entfernt überflüssige Leerzeichen um Apostrophe
    - Reduziert Mehrfach Leerzeichen
    - casefold() für Sprachunabhängige Klein-/Großschhreibung 
    
    '''
    if not s:
        return ""
    s = s.strip()
    s = _APOS_MULTI.sub("'", s)          # alle Varianten + Mehrfach-’ -> '
    s = re.sub(r"\s*'\s*", "'", s)       # Leerzeichen um Apostroph entfernen
    s = re.sub(r"\s+", " ", s)           # Mehrfachspaces
    return s.casefold()


# vorberechnete Map der normalisierten Competition-Keys -> Label
_COMP_LBL_NORM = { _norm_comp_key(k): v for k, v in COMPETITION_LABELS.items() }


def _comp_label(name: str | None) -> str | None:
    ''' Gibt ein konsistentes Label für einen Wettbewerbsnamen zurück:

    - Exakte treffer gegen COMPETION_LABELS
    - Fallback frü normalosierten Key (z. B. LIGAT HA''AL -> ligat ha'al)
    - Sonst Original zurückgeben

    '''
    if not name:
        return name
    # exakter Treffer (bestehende gemischte Keys)
    if name in COMPETITION_LABELS:
        return COMPETITION_LABELS[name]
    # normalisierter Fallback (z.B. LIGAT HA''AL -> ligat ha'al)
    return _COMP_LBL_NORM.get(_norm_comp_key(name), name)


# --- Defaults -----------------------------------------------------------------
DEFAULT_CATEGORIES = ["Core_ALLE", "Spieltag_Übersicht"]
MATCHDAY_KEY = "Spieltag_Übersicht"

# --- Bundesliga-Benchmark (CSV) ----------------------------------------------
# Cache für CSV-Referenzwerte, um wiederholte Datenzugriffe zu vermeiden
_BUNDESLIGA_BENCH_CACHE: dict[str, float] | None = None

def _load_bundesliga_benchmark() -> dict[str, float] | None:
    """
    Liest die CSV mit Referenzwerten tolerant ein und cached das Ergebnis:

    Unterstützt zwei Formate:
    long: Spalten [metric, value]
    wide: Header sind Metriken; die nächste Zeile enthält die Werte

    Pfadpriorität:
    - settings.BUNDESLIGA_BENCH_CSV
    - Umgebungsvariable BUNDESLIGA_BENCH_CSV
    - harter Fallback-Pfad (für loka arbeiten)
    """

    #greift auf die globale Cache-Variable zu. 
    #Funktion kann beim nächsten Aufruf die Cache zurückgeben und muss nicht die Datei erneut laden.
    global _BUNDESLIGA_BENCH_CACHE                  
    if _BUNDESLIGA_BENCH_CACHE is not None:
        return _BUNDESLIGA_BENCH_CACHE

    default_path = (
        getattr(settings, "BUNDESLIGA_BENCH_CSV", None)
        or os.environ.get("BUNDESLIGA_BENCH_CSV")
        or str(Path(settings.BASE_DIR) / "data" / "top6_overall_mean_last5_all_metrics_first22.csv")
    )
    # falls Pfad ungültig
    if not default_path or not os.path.exists(default_path):
        _BUNDESLIGA_BENCH_CACHE = {}
        return _BUNDESLIGA_BENCH_CACHE

    mapping: dict[str, float] = {}
    with open(default_path, newline="", encoding="utf-8") as fh:
        reader = list(csv.reader(fh))   # alles aufeinaml wird in den Speicher geladen, File ist aber nicht so kritisch
        if not reader:
            _BUNDESLIGA_BENCH_CACHE = {}
            return _BUNDESLIGA_BENCH_CACHE

        # white space trim
        header = [h.strip() for h in reader[0]]
        # long Format: ersten beiden Spalöten 'metric' und 'value' o.ä.
        if len(header) >= 2 and header[0].lower() in {"metric", "key"} and header[1].lower() in {"value", "mean", "avg"}:
            for row in reader[1:]:
                if len(row) < 2:
                    continue
                k = row[0].strip()
                try:
                    v = float(row[1])
                except Exception:
                    continue
                mapping[k] = v
        # wide Format: Header sind die Metriken, nächste Zeile die Werte
        else:
            if len(reader) >= 2:
                vals = reader[1]
                for k, cell in zip(header, vals):
                    k = (k or "").strip()
                    if not k:
                        continue
                    try:
                        mapping[k] = float(cell)
                    except Exception:
                        continue

    _BUNDESLIGA_BENCH_CACHE = mapping
    return _BUNDESLIGA_BENCH_CACHE

# --- kleine Utilities ---------------------------------------------------------
def _percentile(sorted_vals, p: float):
    """ Perzentil mit linearer Interpolation

        - Erwartet eine SORTIERTE Liste von Zahlen 
        - Gibt None bei leerer Liste.
    """

    n = len(sorted_vals)
    if n == 0:
        return None
    if n == 1:
        return float(sorted_vals[0])
    x = (n - 1) * p
    i, j = floor(x), ceil(x)
    if i == j:
        return float(sorted_vals[i])
    w = x - i
    return float(sorted_vals[i] * (1 - w) + sorted_vals[j] * w)

def _scale_hints(values, metric_format: str):
    """ Erzeugt sinnvolle Min/Max-Grenzen für Chart-Skalen

        - Für Prozentwerte: feste Begrenzung [0, 1] ---- ist noch ein Fehler versteckt
        - Für numerische Werte: 5.–95.% + 15% Padding (Ausreiser)
        - Falls alle Werte identisch sind, wird um +/- 10% gepuffert, damit man etwas sieht
    """
    vals = [float(v) for v in values if v is not None]
    if not vals:
        return {"min": None, "max": None, "suggestedMin": None, "suggestedMax": None}

    vals.sort()
    vmin, vmax = vals[0], vals[-1]
    q05 = _percentile(vals, 0.05) or vmin
    q95 = _percentile(vals, 0.95) or vmax

    if metric_format == "percent":
        pad = 0.02
        smin = max(0.0, q05 - pad)
        smax = min(1.0, q95 + pad)
        # Mindestspanne, damit der Plot nicht zu flach ist
        min_span = 0.20
        if smax - smin < min_span:
            mid = (smin + smax) / 2.0
            smin = max(0.0, mid - min_span / 2.0)
            smax = min(1.0, mid + min_span / 2.0)
        hmin, hmax = smin, smax
    else:
        rng = max(1e-9, q95 - q05)
        pad = 0.15 * rng
        smin = q05 - pad
        smax = q95 + pad
        if smin == smax:
            base = abs(smax) or 1.0
            smin = smax - 0.1 * base
            smax = smax + 0.1 * base
        hmin, hmax = smin, smax

    return {
        "min": float(hmin),
        "max": float(hmax),
        "suggestedMin": float(smin),
        "suggestedMax": float(smax),
    }

# --- Matchday Payload ---------------------------------------------------------
def _build_matchday_overview(qs, selected_team: str, params):
    """
    Baut die Kachel-Übersicht für EIN Spiel (Donut + Mini-Bars) für das ausgewählte Team.

    Erwartet: `qs` ist bereits nach Liga gefiltert (competition_name).
    Auswahl des Spieltags:
    - Wenn ?md=<match_id> im Querystring vorhanden: dieses Spiel
    - Sonst: das jüngste Spiel.
    """
    team_qs = (
        qs.filter(team_name=selected_team)
        .order_by("match_date", "match_id")
        .select_related("match")
        .annotate(
            # Gegnername in Abhängigkeit von Heim/Auswärts
            opponent_name=Case(
                When(team_name=F("match__home_team_name"), then=F("match__away_team_name")),
                default=F("match__home_team_name"),
                output_field=CharField(),
            )
        )
    )
    # Holen nur die Felder, die wir für die Kacheln wollen, jederzeit änderbar
    rows = list(
        team_qs.values(
            "match_id", "match_date", "opponent_name",
            "goals", "opponent_goals",
            "possession", "opponent_possession",
            "successful_passes", "opponent_successful_passes",
            "op_xg", "sp_xg", "opponent_op_xg", "opponent_sp_xg",
            "deep_progressions", "opponent_deep_progressions",
            "deep_completions", "opponent_deep_completions",
            "op_shots", "sp_shots", "opponent_op_shots", "opponent_sp_shots",
            "pressure_regain_rate", "opponent_pressure_regain_rate",
            "obv", "opponent_obv",
            "match__home_team_name", "match__away_team_name"
        )
    )
    if not rows:
        return {
            "overview_mode": "matchday",
            "matchdays": [],
            "selected_match_id": None,
            "tiles": [],
            "fixture": None,
            "error": "Keine Spiele für dieses Team gefunden.",
        }

    # # Liste aller Spieltage (Label für Dropdown/Select)
    md_list = []
    for i, r in enumerate(rows, start=1):
        d = r.get("match_date")
        try:
            d_str = d.strftime("%d.%m.%Y")
        except Exception:
            d_str = str(d) if d else ""
        home_team = r["match__home_team_name"]
        ha = "H" if (home_team == selected_team) else "A"      # Heim/Auswärts-Kürzel
        md_list.append({"id": str(r["match_id"]), "label": f"MD{i:02d} – {ha} – {r.get('opponent_name') or '?'} – {d_str}"})

    # Ausgewähltes Spiel bestimmen
    md_param = params.get("md")
    idx = None
    if md_param:
        for j, r in enumerate(rows):
            if str(r["match_id"]) == str(md_param):
                idx = j
                break
    if idx is None:
        idx = len(rows) - 1 # Default, jüngstes Spiel

    row = rows[idx]

    # Header-Infos (Datum, Heim/Auswärts, Tore, xG), kann man noch schöner machen
    try:
        date_pretty = row["match_date"].strftime("%d.%m.%Y") if row.get("match_date") else ""
    except Exception:
        date_pretty = str(row.get("match_date") or "")
    home_team = row["match__home_team_name"]
    home_away = "H" if (home_team == selected_team) else "A"

    # Tore und xG gesamt (open play + set pieces)
    goals = int(row.get("goals") or 0)
    opp_goals = int(row.get("opponent_goals") or 0)
    xg_team = float(row.get("op_xg") or 0.0) + float(row.get("sp_xg") or 0.0)
    xg_opp  = float(row.get("opponent_op_xg") or 0.0) + float(row.get("opponent_sp_xg") or 0.0)

    # Schüsse gesamt (open play + set pieces)
    shots_team = int(row.get("op_shots") or 0) + int(row.get("sp_shots") or 0)
    shots_opp  = int(row.get("opponent_op_shots") or 0) + int(row.get("opponent_sp_shots") or 0)

    def pct(x):
        try:
            return float(x)
        except Exception:
            return None
    # Kacheln für die Matchday-Ansicht (Typ, Key, Label, Format, Team-/Gegnerwert)
    tiles = [
        {"type":"pie","key":"possession","label":"Ballbesitz","format":"percent","team":pct(row.get("possession")),"opp":pct(row.get("opponent_possession"))},
        {"type":"bars","key":"successful_passes","label":"Erfolgreiche Pässe","format":"int","team":int(row.get("successful_passes") or 0),"opp":int(row.get("opponent_successful_passes") or 0)},
        {"type":"bars","key":"xg_total","label":"xG gesamt","format":"float","team":round(xg_team,6),"opp":round(xg_opp,6)},
        {"type":"bars","key":"deep_progressions","label":"Deep Progressions","format":"int","team":int(row.get("deep_progressions") or 0),"opp":int(row.get("opponent_deep_progressions") or 0)},
        {"type":"bars","key":"deep_completions","label":"Deep Completions","format":"int","team":int(row.get("deep_completions") or 0),"opp":int(row.get("opponent_deep_completions") or 0)},
        {"type":"bars","key":"shots_all","label":"Schüsse (alle)","format":"int","team":shots_team,"opp":shots_opp},
        {"type":"bars","key":"pressure_regain_rate","label":"Pressure-Erfolgsquote","format":"percent","team":pct(row.get("pressure_regain_rate")),"opp":pct(row.get("opponent_pressure_regain_rate"))},
        {"type":"bars","key":"obv","label":"OBV gesamt","format":"float","team":float(row.get("obv") or 0.0),"opp":float(row.get("opponent_obv") or 0.0)},
    ]

    return {
        "overview_mode": "matchday",
        "matchdays": md_list,
        "selected_match_id": str(row["match_id"]),
        "fixture": {"date": date_pretty, "home_away": home_away, "opponent": row.get("opponent_name") or "?", "goals": goals, "opp_goals": opp_goals, "xg": round(xg_team,6), "opp_xg": round(xg_opp,6)},
        "tiles": tiles,
        "error": None,
    }



# --- Haupt-Payload (Charts + optional Matchday) -------------------------------
def _compute_payload(params):
    """
    Zentraler Orchestrator: liest Request-Parameter und erzeugt die Payload
    für Charts, Listen (Metriken, Teams) und optional die Matchday-Übersicht.


    Erwartete Parameter (GET):
    - league: Wettbewerbs-/Liga-Name
    - team: Teamname (oder "Alle" für Ligavergleich)
    - categories: Liste von Kategorien (z. B. Core_ALLE, Spieltag_Übersicht, ...)
    - metric: ausgewählter metrischer Key
    - md: (optional) match_id für die Matchday-Ansicht
    """
    # --- verfügbare Ligen laden ---
    competitions = list(
        TeamEventData.objects.values_list("competition_name", flat=True)
        .distinct().order_by("competition_name")
    )
    selected = params.get("league") or (competitions[0] if competitions else None)

    # Basis-QuerySet ggf. nach Liga filtern
    qs = TeamEventData.objects.all()
    if selected:
        qs = qs.filter(competition_name=selected)

    # Teams der Liga (für Auswahl-UI)
    teams_in_league = list(qs.values_list("team_name", flat=True).distinct().order_by("team_name"))

    # Team-Auswahl validieren
    selected_team = params.get("team") or "Alle"
    if selected_team != "Alle" and selected_team not in teams_in_league:
        selected_team = "Alle"

    # Kategorien aus Request (Mehrfachauswahl)
    selected_categories = params.getlist("categories") if hasattr(params, "getlist") else params.get("categories", [])
    if not selected_categories:
        selected_categories = DEFAULT_CATEGORIES[:]

    # Matchday wird aktiv, sobald MATCHDAY_KEY ausgewählt ist (zusätzlich zum Chart-Teil)
    want_matchday = MATCHDAY_KEY in selected_categories

    # Für die Metriken MATCHDAY_KEY herausfiltern (Matchday erzeugt keine Metrikliste)
    metric_categories = [c for c in selected_categories if c != MATCHDAY_KEY]
    if not metric_categories:
        metric_categories = ["Core_ALLE"]

    # gültige Metriken aus Kategorien aufbauen (Reihenfolge bewahren, Duplikate entfernen)
    valid_metrics = set(COLUMN_LABELS.keys()) - set(METRIC_NICHT.keys())
    category_metrics = []
    for cat in metric_categories:
        category_metrics += METRIC_CATEGORIES.get(cat, [])
    seen = set()
    category_metrics = [m for m in category_metrics if not (m in seen or seen.add(m))]

    # Dropdown-Optionen: (key, schöner Name)
    metrics_options = [(name, COLUMN_LABELS[name][0]) for name in category_metrics if name in valid_metrics]
    metrics_options.sort(key=lambda kv: kv[1].lower())
    metric_keys = [m for m, _ in metrics_options]

    # gewählte Metrik prüfen/festlegen
    metric = params.get("metric")
    if not metric or metric not in metric_keys:
        metric = metric_keys[0] if metric_keys else None

    # Initialisierung Chart-Metadaten
    pretty_metric = None
    legend = None
    metric_format = None
    chart_data = None
    league_mean = None
    team_mean = None
    quantiles = None
    error = None

    # --- Chart-Payload berchenen ---
    if not metric:
        error = "Keine gültige Metrik in ausgewählten Kategorien verfügbar."
    else:
        # schöner Name, Legende, Format ("float" | "int" | "percent") holen
        pretty_metric, legend, metric_format = COLUMN_LABELS.get(metric, (metric, None, "float"))
        if not selected:
            error = "Keine Liga ausgewählt."
        else:
            if selected_team == "Alle":
                # Ligenvergleich: Teamdurchschnitt der Metrik
                team_avgs_qs = qs.values("team_name").annotate(val=Avg(metric)).order_by("-val")
                items = [(r["team_name"], r["val"]) for r in team_avgs_qs if r["val"] is not None]
                if items:
                    labels = [t for t, _ in items]
                    values = [round(float(v), 6) for _, v in items]

                    # Kennzahlen für Skalen & Quantile (auf Basis der Werte im Ligenvergleich)
                    vals = sorted(values)
                    league_mean = sum(vals) / len(vals) if vals else None
                    quantiles = {
                        "p10": _percentile(vals, 0.10),
                        "p25": _percentile(vals, 0.25),
                        "p75": _percentile(vals, 0.75),
                        "p90": _percentile(vals, 0.90),
                    }
                    chart_data = {
                        "labels": labels,
                        "datasets": [{"type": "bar", "label": f"{pretty_metric} – Teammittel", "data": values}],
                    }
                else:
                    error = "Keine Daten für Plot gefunden."
            else:
                # Zeitreihe für EIN Team: Werte je Spieltag
                league_mean = qs.aggregate(val=Avg(metric))["val"]

                team_qs = (
                    qs.filter(team_name=selected_team)
                    .order_by("match_date")
                    .select_related("match")
                    .annotate(
                        opponent_name=Case(
                            When(team_name=F("match__home_team_name"), then=F("match__away_team_name")),
                            default=F("match__home_team_name"),
                            output_field=CharField(),
                        )
                    )
                )

                extra_fields = []
                include_opponent_pressures = metric == "opponent_pressure_regains"
                if include_opponent_pressures:
                    extra_fields.append("opponent_pressures")

                value_rows = list(
                    team_qs.values("match_date", "opponent_name", metric, *extra_fields)
                )

                labels, values = [], []
                overlay_values = [] if include_opponent_pressures else None
                for row in value_rows:
                    opp = row.get("opponent_name") or "?"
                    d = row.get("match_date")
                    try:
                        date_pretty = d.strftime("%d.%m.%Y") if isinstance(d, datetime) else (d or "")
                    except Exception:
                        date_pretty = str(d) if d is not None else ""
                    labels.append(f"{opp} – {date_pretty}")
                    val = row.get(metric)
                    values.append(None if val is None else round(float(val), 6))
                    if overlay_values is not None:
                        opp_val = row.get("opponent_pressures")
                        overlay_values.append(
                            None if opp_val is None else round(float(opp_val), 6)
                        )

                # Null-Werte entfernen (sowohl aus Labels als auch Werten)
                clean = [
                    (lab, v, None if overlay_values is None else overlay_values[i])
                    for i, (lab, v) in enumerate(zip(labels, values))
                    if v is not None
                ]
                labels = [lab for lab, _, _ in clean]
                values = [v for _, v, _ in clean]
                if overlay_values is not None:
                    overlay_values = [ov for _, _, ov in clean]

                if labels:
                    team_mean = (sum(values) / len(values)) if values else None
                    datasets = [
                        {
                            "type": "bar",
                            "label": f"{pretty_metric} – {selected_team}",
                            "data": values,
                        }
                    ]
                    if overlay_values is not None and any(v is not None for v in overlay_values):
                        overlay_label = COLUMN_LABELS.get("opponent_pressures", ("Pressures Gegner",))[0]
                        datasets.append(
                            {
                                "type": "bar",
                                "label": f"{overlay_label}",
                                "data": overlay_values,
                            }
                        )

                    chart_data = {"labels": labels, "datasets": datasets}
                else:
                    error = "Keine Daten für diese Mannschaft / Metrik gefunden."

                # Quantile über ALLE Spiele der Liga (nicht nur das Team)
                vals = [float(v) for v in qs.values_list(metric, flat=True) if v is not None]
                if vals:
                    vals.sort()
                    quantiles = {
                        "p10": _percentile(vals, 0.10),
                        "p25": _percentile(vals, 0.25),
                        "p75": _percentile(vals, 0.75),
                        "p90": _percentile(vals, 0.90),
                    }
    # Skalenhinweise für das Frontend (Chart.js) berechnen
    scale_hints = None
    if chart_data and chart_data.get("datasets"):
        values = []
        for ds in chart_data["datasets"]:
            values.extend([v for v in ds.get("data", []) if v is not None])
        scale_hints = _scale_hints(values, metric_format or "float")

    # CSV-Referenz (nur für Bundesliga AUT sichtbar)
    bench = None
    if selected == "Bundesliga" and metric:
        bench_map = _load_bundesliga_benchmark() or {}
        if metric in bench_map:
            bench = {"label": "CSV-Referenz", "value": float(bench_map[metric])}

    # --- Basis-Payload (Charts + Metrikliste) ---
    payload = {
        "selected": selected,
        "selected_team": selected_team,
        "selected_categories": selected_categories,
        "metrics_options": [{"key": k, "label": lbl} for k, lbl in metrics_options],
        "metric": metric,
        "pretty_metric": pretty_metric,
        "legend": legend,
        "metric_format": metric_format,
        "chart_data": chart_data,
        "league_mean": float(league_mean) if league_mean is not None else None,
        "team_mean": float(team_mean) if team_mean is not None else None,
        "scale_hints": scale_hints,
        "quantiles": {k: float(v) for k, v in (quantiles or {}).items()},
        "error": error,
        "teams": teams_in_league,
        "bench": bench,
    }
    # zusätzlich: hübsches Label für die ausgewählte Liga
    payload["selected_label"] = _comp_label(selected)

    # --- Matchday-Felder anfügen (nur wenn gewünscht & Team != "Alle") ---
    if want_matchday and selected and selected_team != "Alle":
        md_payload = _build_matchday_overview(qs, selected_team, params)
        # Chart-Teil NICHT überschreiben – nur Matchday-Felder ergänzen
        payload.update({
            "overview_mode": md_payload.get("overview_mode"),
            "matchdays": md_payload.get("matchdays"),
            "selected_match_id": md_payload.get("selected_match_id"),
            "fixture": md_payload.get("fixture"),
            "tiles": md_payload.get("tiles"),
            "md_error": md_payload.get("error"),  # eigener Fehlertext für Matchday
        })

    return payload


# --- Views --------------------------------------------------------------------
@login_required
def league_dashboard(request):
    """Rendert das Dashboard-HTML (templates/teams/dashboard.html).

    Erstellt dazu die initiale Payload (Chartdaten und Metadaten) und baut
    die Kontext-Variablen für das Template, inkl. gruppierter Kategorien
    und (value,label)-Paaren für das Liga-Select.
    """
    payload = _compute_payload(request.GET)

    # Gruppierung der Kategorien für die UI (Accordion/Checkbox-Gruppen)
    category_groups = [
        ("Allgemein", ["Core_ALLE", MATCHDAY_KEY]),
        ("Offensive", ["Offensiv_Allgemein", "Offensive_Spiel", "Offensive_F3", "Chancen"]),
        ("Defensive", ["Def_Allgemein", "Def_Spielaufbau_Gegner", "Boxverteidigung"]),
        ("Umschalten", ["transition"]),
        ("Standards – Freistöße", [
            "Standards_Allgemein",
            "Standards_Freistöße_Off_Allgemein",
            "Standards_Freistöße_Off_Direkt",
            "standards_freistöße_def_allgemein",
            "standards_freistöße_def_direkt",
        ]),
        ("Standards – Ecken", ["Ecken_Off", "ecken_def"]),
        ("Standards – Einwürfe", ["standards_einwürfe_off", "standards_einwürfe_def"]),
        ("Torwart", ["GK_Off", "GK_def"]),
    ]
    # (Gruppe, [(KategorieKey, Anzeigmamne)])
    grouped_categories = [
        (group, [(cat, CATEGORY_LABELS.get(cat, cat)) for cat in cats]) for group, cats in category_groups
    ]

    # Ligen und Teams erneut für die Selects laden (könnte man aus payload nehmen.... 
    # hier wird es direkt aus dem Modell ermittelt, ist aber logisch äquivalent, muss man nicht ändern)
    competitions = list(
        TeamEventData.objects.values_list("competition_name", flat=True)
        .distinct().order_by("competition_name")
    )
    qs = TeamEventData.objects.all()
    if payload["selected"]:
        qs = qs.filter(competition_name=payload["selected"])
    teams_in_league = list(qs.values_list("team_name", flat=True).distinct().order_by("team_name"))
    
    # Paare (value, label) fürs Liga-Select (value = Raw-Name, label = harmonisiert)
    competitions = list(
        TeamEventData.objects.values_list("competition_name", flat=True)
        .distinct().order_by("competition_name")
    )

    competitions_view = [(c, _comp_label(c)) for c in competitions]


    # Kontext fürs Template
    context = {
        "competitions_view": competitions_view, 
        "competitions": competitions,
        "teams": ["Alle"] + teams_in_league,
        "grouped_categories": grouped_categories,
        "selected": payload["selected"],
        "selected_label": _comp_label(payload["selected"]),
        "selected_team": payload["selected_team"],
        "selected_categories": payload["selected_categories"],
        "metrics_options": [(m["key"], m["label"]) for m in payload["metrics_options"]],
        "metric": payload["metric"],
        "pretty_metric": payload["pretty_metric"],
        "legend": payload["legend"],
        "metric_format": payload["metric_format"],
        # Chart-Daten und Meta als JSON-String fürs Frontend (Chart.js)
        "chart_data_json": json.dumps(payload["chart_data"]) if payload["chart_data"] else "null",
        "chart_meta_json": json.dumps({
            "league_mean": payload["league_mean"],
            "team_mean": payload["team_mean"],
            "scale_hints": payload["scale_hints"],
            "metric_format": payload["metric_format"],
            "quantiles": payload.get("quantiles"),
            "bench": payload.get("bench"),
        }),
        "error": payload["error"],
    }
    return render(request, "teams/dashboard.html", context)

@login_required
def league_dashboard_data(request):
    """Gibt die vollständige Payload als JSON zurück (für AJAX/Fetch im Frontend)
    """
    payload = _compute_payload(request.GET)
    return JsonResponse(payload)
