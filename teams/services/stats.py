

"""

    Kleine Statistik-/Format-Helfer, die auch in den Views gebraucht werden:
      - format_value(x, metric_format): Werte schön formatieren
      - percentile(sorted_vals, p)   : Perzentil mit linearer Interpolation
      - scale_hints(values, fmt)     : Achsen-Hinweise (min/max/suggestedMin/Max)


    Die Logik in `scale_hints` ist an die View-Implementierung angepasst


"""
from math import floor, ceil


def format_value(x, metric_format: str) -> str:
    """Formatiert Zahlen je nach gewünschtem Format.

    - "percent":  0.123 ->"12.3 %"
    - sonst:      12.345 -> "12.35"
    - None -> ""
    """
    if x is None:
        return ""
    if metric_format == "percent":
        return f"{x * 100:.1f} %"
    return f"{x:.2f}"


def percentile(sorted_vals, p: float):
    """p-Perzentil (0..1) mit linearer Interpolation auf sortierter Liste.

    Edge Cases:
      - n == 0 -> None
      - n == 1 -> der einzige Wert
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


def scale_hints(values, metric_format: str):
    """Leitet sinnvolle Achsen-Hinweise aus Daten ab

    Rückgabe:
      dict(min, max, suggestedMin, suggestedMax)

    Idee dahinter:
      - Prozent: Clamp auf [0,1], kleiner Puffer, Mindestspanne 0.20
      - Sonst  : 5.–95.% Quantil + 15% Puffer; Mindestspanne > 0
    """
    vals = [float(v) for v in values if v is not None]
    if not vals:
        return {"min": None, "max": None, "suggestedMin": None, "suggestedMax": None}

    vals.sort()
    vmin, vmax = vals[0], vals[-1]

    if metric_format == "percent":
        pad = 0.02
        # einfache Indizes (≈ 5% / 95%) – bei kleinen n vorsichtig
        lo_idx = max(0, int(0.05 * len(vals)))
        hi_idx = max(0, int(0.95 * len(vals)) - 1)
        smin = max(0.0, max(vals[0], vals[lo_idx]) - pad)
        smax = min(1.0, min(vals[-1], vals[hi_idx]) + pad)
        min_span = 0.20
        if smax - smin < min_span:
            mid = (smin + smax) / 2.0
            smin = max(0.0, mid - min_span / 2.0)
            smax = min(1.0, mid + min_span / 2.0)
        hmin, hmax = smin, smax
    else:
        # Bereich über 5.–95.% approximieren
        lo_idx = max(0, int(0.05 * len(vals)))
        hi_idx = max(0, int(0.95 * len(vals)) - 1)
        rng = max(1e-9, vals[hi_idx] - vals[lo_idx])
        pad = 0.15 * rng
        smin = vals[lo_idx] - pad
        smax = vals[hi_idx] + pad
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
