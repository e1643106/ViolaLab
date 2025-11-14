from django import template

try:  # pragma: no cover - defensive fallback for template import time
    from players.labels import POSITION_LABELS as _POSITION_LABELS
except Exception:  # noqa: BLE001 - we must not break template loading
    _POSITION_LABELS: dict[str, str] = {}

POSITION_LABELS = _POSITION_LABELS

register = template.Library()


@register.filter
def attr(value, name):
    """Safely access an attribute on an object in templates."""
    if value is None:
        return None
    return getattr(value, name, None)


@register.filter
def position_label(code):
    """Map a short position code (e.g. ``CM``) to a friendly label."""

    if not code:
        return ""
    code_str = str(code)
    return POSITION_LABELS.get(code_str, code_str)


@register.filter
def dict_get(value, key):
    """Safely fetch *key* from a dict-like structure."""

    if value is None:
        return None
    try:
        return value.get(key)
    except AttributeError:
        return None
