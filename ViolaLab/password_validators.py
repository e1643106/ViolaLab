# ViolaLab/password_validators.py
import re  # RegEx
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _ 


# Klasse für Validator -- Custom-Passwort-Validator erwartet Methoden mit Namen validate und get_help_text
class UppercaseValidator:
    """
    Erfordert mindestens einen Großbuchstaben A–Z (nur ASCII, keine Umlaute)
    """

    # Klassenattribut pattern: eine kompilierte RegEx
    # re.compile(...) verschiebt die Compile-"Kosten" an den Modulimport (performant)
    # Raw String r"..." heißt: Backslashes werden nicht als Escape in Python behandelt, sondern direkt an den RegEx-Parser übergeben
    # [A-Z] matcht einen ASCII-Großbuchstaben von A bis Z (keine Umlaute!)
    pattern = re.compile(r"[A-Z]")  # ---> RegEx-Objekt, das überprüft wird

    # Methode, die Django aufruft, um das Passwort zu prüfen
    # password ist str, user optional, Rückgabe None: bei Erfolg wird nichts zurückgegeben, bei Fehler Exception
    def validate(self, password: str, user=None) -> None:
        if not self.pattern.search(password):   # self.pattern.search(...) sucht IRGENDWO im String nach einem Treffer, None wenn kein Match
                                               # not... prüft: wurde KEIN Großbuchstabe gefunden?
            raise ValidationError(
                _("Das Passwort muss mindestens einen Großbuchstaben enthalten."),
                code="password_no_upper",
            )

    def get_help_text(self) -> str:   # erzeugt Hilfstext (z. B. unter dem Passwortfeld)
        return _("Muss mindestens einen Großbuchstaben enthalten.")


# analog zu Uppercase 
class LowercaseValidator:
    """
    Erfordert mindestens einen Kleinbuchstaben a–z (nur ASCII, keine Umlaute)
    """
    pattern = re.compile(r"[a-z]")

    def validate(self, password: str, user=None) -> None:
        if not self.pattern.search(password):
            raise ValidationError(
                _("Das Passwort muss mindestens einen Kleinbuchstaben enthalten."),
                code="password_no_lower",
            )

    def get_help_text(self) -> str:
        return _("Muss mindestens einen Kleinbuchstaben enthalten.")


# Validator für Ziffern
class NumberValidator:
    """
    Erfordert mindestens eine Ziffer 0–9
    """
    pattern = re.compile(r"[0-9]")  # matcht nur ASCII-Ziffern von 0 bis 9

    def validate(self, password: str, user=None) -> None:
        if not self.pattern.search(password):
            raise ValidationError(
                _("Das Passwort muss mindestens eine Zahl enthalten."),
                code="password_no_number",
            )

    def get_help_text(self) -> str:
        return _("Muss mindestens eine Zahl enthalten.")


# Validator für Sonderzeichen
class SpecialCharacterValidator:
    """
    Erfordert mindestens ein Sonderzeichen (kein Buchstabe, keine Ziffer, kein Unterstrich, KEIN Leerzeichen)
    """

    # [^...] = Negativklasse, also matcht alles, was NICHT in der Menge enthalten ist
    # \w = "Word Characters" (Buchstaben, Ziffern, Unterstrich)
    # \s = Whitespace (Leerzeichen, Tab, Zeilenumbruch, ...)
    # [^\w\s] matcht also: Zeichen, die weder \w noch \s sind -> echte Sonderzeichen wie !?@#$%&*
    pattern = re.compile(r"[^\w\s]")

    def validate(self, password: str, user=None) -> None:
        if not self.pattern.search(password):
            raise ValidationError(
                _("Das Passwort muss mindestens ein Sonderzeichen enthalten."),
                code="password_no_special",
            )

    def get_help_text(self) -> str:
        return _("Muss mindestens ein Sonderzeichen enthalten (z. B. !?@#$%&*, kein Leerzeichen).")
