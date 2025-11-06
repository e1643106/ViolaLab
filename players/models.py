"""Players app models and compatibility exports."""

from django.db import models

<<<<<<< ours
=======
from .data_access import MatchRow, SeasonRow

>>>>>>> theirs

class Player(models.Model):
    """Abbild der bestehenden ``players``-Tabelle."""

    player_id = models.IntegerField(primary_key=True)
    birth_date = models.DateField(blank=True, null=True)
    player_name = models.CharField(max_length=255, blank=True, null=True)
    player_height_cm = models.FloatField(blank=True, null=True)
    player_weight_kg = models.FloatField(blank=True, null=True)
    created_at_utc = models.DateTimeField(blank=True, null=True)
    updated_at_utc = models.DateTimeField(blank=True, null=True)
    player_female = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "players"
        ordering = ("player_name",)

    def __str__(self) -> str:  # pragma: no cover - reine Convenience
        return self.player_name or f"Player {self.player_id}"
<<<<<<< ours
=======


# ----------------------------------------------------------------------------
# Compatibility aliases
# ----------------------------------------------------------------------------
#
# Earlier iterations of the players app exposed unmanaged Django models named
# ``PlayerSeasonStat`` and ``PlayerMatchStat``.  These relied on implicit
# ``id`` columns that do not exist in the underlying SQL Server views/tables
# and therefore triggered ``Invalid column name 'id'`` errors once queried.
#
# The refactored dashboard now consumes lightweight dataclass rows defined in
# ``players.data_access`` instead.  To keep imports from older code paths from
# breaking (e.g. ``from players.models import PlayerMatchStat``) we re-export
# those dataclasses here under the legacy names.  This keeps backwards
# compatibility without reintroducing the faulty ORM models.

PlayerSeasonStat = SeasonRow
PlayerMatchStat = MatchRow

__all__ = ["Player", "PlayerSeasonStat", "PlayerMatchStat"]
>>>>>>> theirs
