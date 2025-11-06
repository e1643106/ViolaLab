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


class PlayerSeasonStat(models.Model):
    """Saisondaten eines Spielers (Aggregationen pro Saison/Wettbewerb)."""

    competition_id = models.IntegerField()
    season_id = models.IntegerField()
    player = models.ForeignKey(
        Player,
        models.DO_NOTHING,
        db_column="player_id",
        related_name="season_stats",
    )
    team_id = models.IntegerField(blank=True, null=True)
    team_name = models.CharField(max_length=255, blank=True, null=True)

    npga_90 = models.FloatField(blank=True, null=True)
    padj_tackles_90 = models.FloatField(blank=True, null=True)
    padj_tackles_and_interceptions_90 = models.FloatField(blank=True, null=True)
    blocks_per_shot = models.FloatField(blank=True, null=True)
    backward_pass_proportion = models.FloatField(blank=True, null=True)
    sideways_pass_proportion = models.FloatField(blank=True, null=True)
    op_f3_forward_pass_proportion = models.FloatField(blank=True, null=True)
    op_f3_backward_pass_proportion = models.FloatField(blank=True, null=True)
    op_f3_sideways_pass_proportion = models.FloatField(blank=True, null=True)
    shot_on_target_ratio = models.FloatField(blank=True, null=True)
    conversion_ratio = models.FloatField(blank=True, null=True)
    npg_90 = models.FloatField(blank=True, null=True)
    padj_clearances_90 = models.FloatField(blank=True, null=True)
    xgchain_90 = models.FloatField(blank=True, null=True)
    op_xgbuildup_90 = models.FloatField(blank=True, null=True)
    shots_faced_90 = models.FloatField(blank=True, null=True)
    np_xg_faced_90 = models.FloatField(blank=True, null=True)
    np_psxg_faced_90 = models.FloatField(blank=True, null=True)
    xs_ratio = models.FloatField(blank=True, null=True)
    left_foot_ratio = models.FloatField(blank=True, null=True)
    pressured_passing_ratio = models.FloatField(blank=True, null=True)
    passes_pressed_ratio = models.FloatField(blank=True, null=True)
    s_pass_length = models.FloatField(blank=True, null=True)
    p_pass_length = models.FloatField(blank=True, null=True)
    ps_pass_length = models.FloatField(blank=True, null=True)
    ot_shots_faced_90 = models.FloatField(blank=True, null=True)
    ot_shots_faced_ratio = models.FloatField(blank=True, null=True)
    np_optimal_gk_dlength = models.FloatField(blank=True, null=True)
    pass_into_pressure_ratio = models.FloatField(blank=True, null=True)
    pass_into_danger_ratio = models.FloatField(blank=True, null=True)
    appearances = models.IntegerField(blank=True, null=True)
    positive_outcome_90 = models.FloatField(blank=True, null=True)
    sp_assists_90 = models.FloatField(blank=True, null=True)
    sp_key_passes_90 = models.FloatField(blank=True, null=True)
    npxgxa_90 = models.FloatField(blank=True, null=True)
    shots_key_passes_90 = models.FloatField(blank=True, null=True)
    dribble_ratio = models.FloatField(blank=True, null=True)
    pass_length_ratio = models.FloatField(blank=True, null=True)
    pressured_pass_length_ratio = models.FloatField(blank=True, null=True)
    pressured_change_in_pass_length = models.FloatField(blank=True, null=True)
    carries_90 = models.FloatField(blank=True, null=True)
    carry_ratio = models.FloatField(blank=True, null=True)
    carry_length = models.FloatField(blank=True, null=True)
    yellow_cards_90 = models.FloatField(blank=True, null=True)
    second_yellow_cards_90 = models.FloatField(blank=True, null=True)
    red_cards_90 = models.FloatField(blank=True, null=True)
    errors_90 = models.FloatField(blank=True, null=True)
    padj_pressures_90 = models.FloatField(blank=True, null=True)
    defensive_action_regains_90 = models.FloatField(blank=True, null=True)
    counterpressure_regains_90 = models.FloatField(blank=True, null=True)
    starting_appearances = models.IntegerField(blank=True, null=True)
    average_x_pressure = models.FloatField(blank=True, null=True)
    fhalf_pressures_90 = models.FloatField(blank=True, null=True)
    fhalf_counterpressures_90 = models.FloatField(blank=True, null=True)
    fhalf_pressures_ratio = models.FloatField(blank=True, null=True)
    average_x_defensive_action = models.FloatField(blank=True, null=True)
    average_x_pass = models.FloatField(blank=True, null=True)
    ninety_s_played = models.FloatField(db_column="90s_played", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "player_season_data"
        unique_together = ("competition_id", "season_id", "player", "team_id")

    @property
    def ninety_minutes(self):  # pragma: no cover - simple Alias für Templates
        return self.ninety_s_played


class PlayerMatchStat(models.Model):
    """Einzelspiel-Daten eines Spielers."""

    match = models.ForeignKey(
        "teams.Match",
        models.DO_NOTHING,
        db_column="match_id",
        to_field="match_id",
        related_name="player_stats",
        blank=True,
        null=True,
    )
    player = models.ForeignKey(
        Player,
        models.DO_NOTHING,
        db_column="player_id",
        related_name="match_stats",
    )
    team_id = models.IntegerField(blank=True, null=True)
    team_name = models.CharField(max_length=255, blank=True, null=True)
    match_date = models.DateField(blank=True, null=True)
    minutes = models.FloatField(blank=True, null=True)
    np_xg_per_shot = models.FloatField(blank=True, null=True)
    np_xg = models.FloatField(blank=True, null=True)
    np_shots = models.FloatField(blank=True, null=True)
    goals = models.FloatField(blank=True, null=True)
    np_goals = models.FloatField(blank=True, null=True)
    xa = models.FloatField(blank=True, null=True)
    key_passes = models.FloatField(blank=True, null=True)
    assists = models.FloatField(blank=True, null=True)
    passes_into_box = models.FloatField(blank=True, null=True)
    touches_inside_box = models.FloatField(blank=True, null=True)
    tackles = models.FloatField(blank=True, null=True)
    interceptions = models.FloatField(blank=True, null=True)
    dribbles = models.FloatField(blank=True, null=True)
    challenge_ratio = models.FloatField(blank=True, null=True)
    long_balls = models.FloatField(blank=True, null=True)
    successful_long_balls = models.FloatField(blank=True, null=True)
    clearances = models.FloatField(blank=True, null=True)
    aerials = models.FloatField(blank=True, null=True)
    successful_aerials = models.FloatField(blank=True, null=True)
    passes = models.FloatField(blank=True, null=True)
    successful_passes = models.FloatField(blank=True, null=True)
    passing_ratio = models.FloatField(blank=True, null=True)
    crosses = models.FloatField(blank=True, null=True)
    successful_crosses = models.FloatField(blank=True, null=True)
    penalties_won = models.FloatField(blank=True, null=True)
    pressures = models.FloatField(blank=True, null=True)
    pressure_regains = models.FloatField(blank=True, null=True)
    deep_progressions = models.FloatField(blank=True, null=True)
    fouls_won = models.FloatField(blank=True, null=True)
    xgchain = models.FloatField(blank=True, null=True)
    xgbuildup = models.FloatField(blank=True, null=True)
    obv = models.FloatField(blank=True, null=True)
    obv_pass = models.FloatField(blank=True, null=True)
    obv_shot = models.FloatField(blank=True, null=True)
    obv_defensive_action = models.FloatField(blank=True, null=True)
    obv_dribble_carry = models.FloatField(blank=True, null=True)
    goals_conceded = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "player_match_data"
        ordering = ("match_date", "match_id", "player_id")

    def __str__(self) -> str:  # pragma: no cover - Anzeigehilfe
        base = self.player.player_name if self.player_id and hasattr(self, "player") else str(self.player_id)
        date = self.match.match_date if self.match_id and self.match else self.match_date
        return f"{base} – {date}"
