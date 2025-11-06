from django.db import models


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
