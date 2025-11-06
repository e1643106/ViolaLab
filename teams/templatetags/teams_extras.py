"""

    Stellt benutzerdefinierte Django-Template-Filter bereit.
    Aktuell enthalten: `get_item` – zum sicheren Nachschlagen eines Wertes
    in einem Dictionary per Schlüssel direkt im Template.

Einsatz im Template:
    {% load teams_extras %}
    {{ row|get_item:"spaltenname" }}

    Django-Templates erlauben keinen direkten Ausdruck wie `row[header]`
    Mit einem Filter kann man aber per Schlüssel auf Dict-Werte zugreifen.

Rückgabe:
    - Ist `d` ein Dictionary, wird `d.get(key, "")` zurückgegeben.
    - Andernfalls wird ein leerer String zurückgegeben (keine Exception im Template).
"""

from django import template

# Library-Instanz registrieren – hier werden unsere Filter/Tags angemeldet
register = template.Library()


@register.filter
def get_item(d, key):
    """Template-Filter für Dict-Zugriff per Schlüssel:

    Bsp:
        {{ my_row|get_item:"team_name" }}
        {{ stats|get_item:dynamic_key_var }}

    Args:
        d:   Erwartet ein `dict`-ähnliches Objekt 
        key: Schlüssel (String), der im Dict nachgeschlagen werden soll

    Returns:
        Wert zu `key` oder "" (leerer String), falls nicht vorhanden
        bzw. `d` kein Dict ist. Das vermeidet Template-Fehler.
    """
    # erlaubt {{ dict|get_item:"spaltenname" }} im template
    if isinstance(d, dict):
        return d.get(key, "")
    return ""