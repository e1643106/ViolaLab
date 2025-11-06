"""

    CSV-Referenzwerte (Bundesliga-Benchmark) einmalig laden und im
    Modul-Cache halten. Unterstützt zwei CSV-Formate:

    long  : Spalten [metric, value] (auch [key, value|mean|avg])
    wide  : Header sind Metriken, nächste Zeile enthält die Werte

Pfad-Prio:
    1) settings.BUNDESLIGA_BENCH_CSV
    2) Umgebungsvariable BUNDESLIGA_BENCH_CSV


Caching:
    _CACHE ist ein Modul-weiter Speicher. Beim ersten Aufruf wird gelesen,
    danach werden Folgeaufrufe aus dem Cache gefüllt
"""
from __future__ import annotations
import csv, os
from django.conf import settings

# Modul-weiter Cache (None = noch nicht geladen)
_CACHE: dict[str, float] | None = None

def load_bundesliga_benchmark() -> dict[str, float]:
    """Liest die CSV tolerant ein und liefert ein Mapping {metric -> float}.

    Rückgabe:
        dict[str, float]: leeres Dict, falls kein Pfad/keine Datei, sonst Key→Wert.
    """
    global _CACHE
    if _CACHE is not None:
        # Bereits geladen -> direkt zurückgeben
        return _CACHE

    # 1) settings  2) Umgebungsvariable
    path = (
        getattr(settings, "BUNDESLIGA_BENCH_CSV", None)
        or os.environ.get("BUNDESLIGA_BENCH_CSV")
    )

    # Nichts konfiguriert oder Datei existiert nicht -> leerer Cache
    if not path or not os.path.exists(path):
        _CACHE = {}
        return _CACHE

    mapping: dict[str, float] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
        if not rows:
            _CACHE = {}
            return _CACHE

        header = [h.strip() for h in rows[0]]

        # long-Format: erste beiden Spalten heißen sinngemäß metric/key, value/mean/avg
        if (
            len(header) >= 2
            and header[0].lower() in {"metric", "key"}
            and header[1].lower() in {"value", "mean", "avg"}
        ):
            for r in rows[1:]:
                if len(r) < 2:
                    continue
                try:
                    mapping[r[0].strip()] = float(r[1])
                except Exception:
                    # nicht-parsbare Zellen still überspringen
                    pass
        #  wide-Format: Header = Metriken, Zeile 2 = Werte
        elif len(rows) >= 2:
            for k, cell in zip(header, rows[1]):
                k = (k or "").strip()
                if not k:
                    continue
                try:
                    mapping[k] = float(cell)
                except Exception:
                    pass

    _CACHE = mapping
    return _CACHE

