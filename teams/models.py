# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

from django.db import models

class Competition(models.Model):
    id = models.AutoField(primary_key=True)  # künstlicher PK für saubere ForeignKeys
    competition_id = models.IntegerField()
    season_id = models.IntegerField()
    country_name = models.CharField(max_length=255, blank=True, null=True)
    competition_name = models.CharField(max_length=255, blank=True, null=True)
    season_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'competitions'
        unique_together = ('competition_id', 'season_id')  # sinnvoll, aber kein PK

    def __str__(self):
        return f"{self.competition_name} {self.season_name}"


class Match(models.Model):
    match_id = models.IntegerField(primary_key=True)
    match_date = models.DateField(blank=True, null=True)
    match_week = models.IntegerField(blank=True, null=True)

    home_team_name = models.CharField(max_length=255, blank=True, null=True)
    away_team_name = models.CharField(max_length=255, blank=True, null=True)
    home_team_id = models.IntegerField(blank=True, null=True)
    away_team_id = models.IntegerField(blank=True, null=True)

    has_event_data = models.IntegerField(blank=True, null=True)

    # FK zur Competition-Tabelle über künstliche ID
    competition = models.ForeignKey(
        Competition,
        models.DO_NOTHING,
        to_field='id',
        blank=True,
        null=True,
        related_name='matches'
    )

    season_name = models.CharField(max_length=255, blank=True, null=True)

    is_processed = models.BooleanField(blank=True, null=True)
    number_360_collected = models.BooleanField(db_column='360_collected', blank=True, null=True)
    number_360_is_processed = models.BooleanField(db_column='360_is_processed', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'matches'

    def __str__(self):
        return f"{self.match_date} – {self.home_team_name} vs {self.away_team_name}"



class PlayerBirthdate(models.Model):
    player_id = models.IntegerField(primary_key=True)
    birth_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'player_birthdates'


class TeamEventData(models.Model):
    #
    match = models.ForeignKey(
        Match,  # statt 'Matches'
        models.DO_NOTHING,
        db_column='match_id',
        to_field='match_id',
        related_name='team_event_data',
        blank=True,
        null=True
    )



    team_id = models.IntegerField(blank=True, null=True)
    team_name = models.CharField(max_length=255, db_collation='Latin1_General_CI_AS')
    opposition_id = models.IntegerField(blank=True, null=True)
    opposition_name = models.CharField(max_length=255, db_collation='Latin1_General_CI_AS', blank=True, null=True)
    competition_id = models.IntegerField(blank=True, null=True)
    competition_name = models.CharField(max_length=255, db_collation='Latin1_General_CI_AS', blank=True, null=True)
    season_id = models.IntegerField(blank=True, null=True)
    season_name = models.CharField(max_length=255, db_collation='Latin1_General_CI_AS', blank=True, null=True)
    gd = models.IntegerField(blank=True, null=True)
    xgd = models.FloatField(blank=True, null=True)
    np_shots = models.IntegerField(blank=True, null=True)
    op_shots = models.IntegerField(blank=True, null=True)
    op_shots_outside_box = models.IntegerField(blank=True, null=True)
    sp_shots = models.IntegerField(blank=True, null=True)
    np_xg = models.FloatField(blank=True, null=True)
    op_xg = models.FloatField(blank=True, null=True)
    sp_xg = models.FloatField(blank=True, null=True)
    np_xg_per_shot = models.FloatField(blank=True, null=True)
    np_shot_distance = models.FloatField(blank=True, null=True)
    op_shot_distance = models.FloatField(blank=True, null=True)
    sp_shot_distance = models.FloatField(blank=True, null=True)
    possessions = models.IntegerField(blank=True, null=True)
    possession = models.FloatField(blank=True, null=True)
    directness = models.FloatField(blank=True, null=True)
    pace_towards_goal = models.FloatField(blank=True, null=True)
    gk_pass_distance = models.FloatField(blank=True, null=True)
    gk_long_pass_ratio = models.FloatField(blank=True, null=True)
    box_cross_ratio = models.FloatField(blank=True, null=True)
    passes_inside_box = models.IntegerField(blank=True, null=True)
    ppda = models.FloatField(blank=True, null=True)
    defensive_distance_ppda = models.FloatField(blank=True, null=True)
    opp_passing_ratio = models.FloatField(blank=True, null=True)
    opp_final_third_pass_ratio = models.FloatField(blank=True, null=True)
    opponent_np_shots = models.IntegerField(blank=True, null=True)
    opponent_op_shots = models.IntegerField(blank=True, null=True)
    opponent_op_shots_outside_box = models.IntegerField(blank=True, null=True)
    opponent_sp_shots = models.IntegerField(blank=True, null=True)
    opponent_np_xg = models.FloatField(blank=True, null=True)
    opponent_op_xg = models.FloatField(blank=True, null=True)
    opponent_sp_xg = models.FloatField(blank=True, null=True)
    opponent_np_xg_per_shot = models.FloatField(blank=True, null=True)
    opponent_np_shot_distance = models.FloatField(blank=True, null=True)
    opponent_op_shot_distance = models.FloatField(blank=True, null=True)
    opponent_sp_shot_distance = models.FloatField(blank=True, null=True)
    opponent_passes_inside_box = models.IntegerField(blank=True, null=True)
    corners = models.IntegerField(blank=True, null=True)
    corner_xg = models.FloatField(blank=True, null=True)
    xg_per_corner = models.FloatField(blank=True, null=True)
    free_kicks = models.IntegerField(blank=True, null=True)
    free_kick_xg = models.FloatField(blank=True, null=True)
    xg_per_free_kick = models.FloatField(blank=True, null=True)
    direct_free_kicks = models.IntegerField(blank=True, null=True)
    direct_free_kick_xg = models.FloatField(blank=True, null=True)
    xg_per_direct_free_kick = models.FloatField(blank=True, null=True)
    throw_ins = models.IntegerField(blank=True, null=True)
    throw_in_xg = models.FloatField(blank=True, null=True)
    xg_per_throw_in = models.FloatField(blank=True, null=True)
    ball_in_play_time = models.FloatField(blank=True, null=True)
    counter_attacking_shots = models.IntegerField(blank=True, null=True)
    high_press_shots = models.IntegerField(blank=True, null=True)
    shots_in_clear = models.IntegerField(blank=True, null=True)
    opponent_counter_attacking_shots = models.IntegerField(blank=True, null=True)
    opponent_shots_in_clear = models.IntegerField(blank=True, null=True)
    aggressive_actions = models.IntegerField(blank=True, null=True)
    aggression = models.FloatField(blank=True, null=True)
    goals = models.IntegerField(blank=True, null=True)
    own_goals = models.IntegerField(blank=True, null=True)
    penalty_goals = models.IntegerField(blank=True, null=True)
    opponent_goals = models.IntegerField(blank=True, null=True)
    opponent_own_goals = models.IntegerField(blank=True, null=True)
    opponent_penalty_goals = models.IntegerField(blank=True, null=True)
    shots_from_corners = models.IntegerField(blank=True, null=True)
    goals_from_corners = models.IntegerField(blank=True, null=True)
    shots_from_free_kicks = models.IntegerField(blank=True, null=True)
    goals_from_free_kicks = models.IntegerField(blank=True, null=True)
    direct_free_kick_goals = models.IntegerField(blank=True, null=True)
    shots_from_direct_free_kicks = models.IntegerField(blank=True, null=True)
    shots_from_throw_ins = models.IntegerField(blank=True, null=True)
    goals_from_throw_ins = models.IntegerField(blank=True, null=True)
    opponent_direct_free_kick_goals = models.IntegerField(blank=True, null=True)
    opponent_shots_from_direct_free_kicks = models.IntegerField(blank=True, null=True)
    opponent_corners = models.IntegerField(blank=True, null=True)
    opponent_corner_xg = models.FloatField(blank=True, null=True)
    opponent_shots_from_corners = models.IntegerField(blank=True, null=True)
    opponent_goals_from_corners = models.IntegerField(blank=True, null=True)
    opponent_free_kicks = models.IntegerField(blank=True, null=True)
    opponent_free_kick_xg = models.FloatField(blank=True, null=True)
    opponent_shots_from_free_kicks = models.IntegerField(blank=True, null=True)
    opponent_goals_from_free_kicks = models.IntegerField(blank=True, null=True)
    opponent_direct_free_kicks = models.IntegerField(blank=True, null=True)
    opponent_direct_free_kick_xg = models.FloatField(blank=True, null=True)
    opponent_throw_ins = models.IntegerField(blank=True, null=True)
    opponent_throw_in_xg = models.FloatField(blank=True, null=True)
    opponent_shots_from_throw_ins = models.IntegerField(blank=True, null=True)
    opponent_goals_from_throw_ins = models.IntegerField(blank=True, null=True)
    corner_shot_ratio = models.FloatField(blank=True, null=True)
    corner_goal_ratio = models.FloatField(blank=True, null=True)
    free_kick_shot_ratio = models.FloatField(blank=True, null=True)
    free_kick_goal_ratio = models.FloatField(blank=True, null=True)
    direct_free_kick_goal_ratio = models.FloatField(blank=True, null=True)
    throw_in_shot_ratio = models.FloatField(blank=True, null=True)
    throw_in_goal_ratio = models.FloatField(blank=True, null=True)
    opponent_xg_per_corner = models.FloatField(blank=True, null=True)
    opponent_corner_shot_ratio = models.FloatField(blank=True, null=True)
    opponent_corner_goal_ratio = models.FloatField(blank=True, null=True)
    opponent_xg_per_free_kick = models.FloatField(blank=True, null=True)
    opponent_free_kick_shot_ratio = models.FloatField(blank=True, null=True)
    opponent_free_kick_goal_ratio = models.FloatField(blank=True, null=True)
    opponent_xg_per_direct_free_kick = models.FloatField(blank=True, null=True)
    opponent_direct_free_kick_goal_ratio = models.FloatField(blank=True, null=True)
    opponent_xg_per_throw_in = models.FloatField(blank=True, null=True)
    opponent_throw_in_shot_ratio = models.FloatField(blank=True, null=True)
    opponent_throw_in_goal_ratio = models.FloatField(blank=True, null=True)
    direct_free_kick_shot_ratio = models.FloatField(blank=True, null=True)
    opponent_direct_free_kick_shot_ratio = models.FloatField(blank=True, null=True)
    sp = models.IntegerField(blank=True, null=True)
    xg_per_sp = models.FloatField(blank=True, null=True)
    sp_shot_ratio = models.FloatField(blank=True, null=True)
    sp_goals = models.IntegerField(blank=True, null=True)
    sp_goal_ratio = models.FloatField(blank=True, null=True)
    opponent_sp = models.IntegerField(blank=True, null=True)
    opponent_xg_per_sp = models.FloatField(blank=True, null=True)
    opponent_sp_shot_ratio = models.FloatField(blank=True, null=True)
    opponent_sp_goals = models.IntegerField(blank=True, null=True)
    opponent_sp_goal_ratio = models.FloatField(blank=True, null=True)
    penalties_won = models.IntegerField(blank=True, null=True)
    opponent_penalties = models.IntegerField(blank=True, null=True)
    completed_dribbles = models.IntegerField(blank=True, null=True)
    failed_dribbles = models.IntegerField(blank=True, null=True)
    total_dribbles = models.IntegerField(blank=True, null=True)
    dribble_ratio = models.FloatField(blank=True, null=True)
    opponent_completed_dribbles = models.IntegerField(blank=True, null=True)
    opponent_failed_dribbles = models.IntegerField(blank=True, null=True)
    opponent_total_dribbles = models.IntegerField(blank=True, null=True)
    opposition_dribble_ratio = models.FloatField(blank=True, null=True)
    opponent_high_press_shots = models.IntegerField(blank=True, null=True)
    np_xgd = models.FloatField(blank=True, null=True)
    passing_ratio = models.FloatField(blank=True, null=True)
    pressures = models.IntegerField(blank=True, null=True)
    counterpressures = models.IntegerField(blank=True, null=True)
    pressure_regains = models.IntegerField(blank=True, null=True)
    counterpressure_regains = models.IntegerField(blank=True, null=True)
    defensive_action_regains = models.IntegerField(blank=True, null=True)
    yellow_cards = models.IntegerField(blank=True, null=True)
    second_yellow_cards = models.IntegerField(blank=True, null=True)
    red_cards = models.IntegerField(blank=True, null=True)
    fhalf_pressures = models.IntegerField(blank=True, null=True)
    fhalf_counterpressures = models.IntegerField(blank=True, null=True)
    fhalf_pressures_ratio = models.FloatField(blank=True, null=True)
    fhalf_counterpressures_ratio = models.FloatField(blank=True, null=True)
    crosses_into_box = models.IntegerField(blank=True, null=True)
    successful_crosses_into_box = models.IntegerField(blank=True, null=True)
    successful_box_cross_ratio = models.FloatField(blank=True, null=True)
    deep_progressions = models.IntegerField(blank=True, null=True)
    opponent_deep_progressions = models.IntegerField(blank=True, null=True)
    obv = models.FloatField(blank=True, null=True)
    obv_pass = models.FloatField(blank=True, null=True)
    obv_shot = models.FloatField(blank=True, null=True)
    obv_defensive_action = models.FloatField(blank=True, null=True)
    obv_dribble_carry = models.FloatField(blank=True, null=True)
    obv_gk = models.FloatField(blank=True, null=True)
    opponent_obv = models.FloatField(blank=True, null=True)
    opponent_obv_pass = models.FloatField(blank=True, null=True)
    obv_shot_nconceded = models.FloatField(blank=True, null=True)
    opponent_obv_defensive_action = models.FloatField(blank=True, null=True)
    opponent_obv_dribble_carry = models.FloatField(blank=True, null=True)
    opponent_obv_gk = models.FloatField(blank=True, null=True)
    passes = models.IntegerField(blank=True, null=True)
    successful_passes = models.IntegerField(blank=True, null=True)
    opponent_passes = models.IntegerField(blank=True, null=True)
    opponent_successful_passes = models.IntegerField(blank=True, null=True)
    op_passes = models.IntegerField(blank=True, null=True)
    opponent_op_passes = models.IntegerField(blank=True, null=True)
    result = models.CharField(max_length=255, db_collation='Latin1_General_CI_AS', blank=True, null=True)
    match_date = models.CharField(max_length=255, db_collation='Latin1_General_CI_AS', blank=True, null=True)
    avg_weighted_age = models.FloatField(blank=True, null=True)
    average_defensive_x = models.FloatField(blank=True, null=True)
    counter_attacks = models.FloatField(blank=True, null=True)
    deep_completions = models.FloatField(blank=True, null=True)
    deep_completions_with_shot = models.FloatField(blank=True, null=True)
    deep_completions_after_crosses = models.FloatField(blank=True, null=True)
    deep_completions_after_cutbacks = models.FloatField(blank=True, null=True)
    deep_completions_after_counters = models.FloatField(blank=True, null=True)
    deep_completion_rate = models.FloatField(blank=True, null=True)
    deep_completion_shot_rate = models.FloatField(blank=True, null=True)
    pressure_regain_rate = models.FloatField(blank=True, null=True)
    counterpressure_regain_rate = models.FloatField(blank=True, null=True)
    opponent_possessions = models.IntegerField(blank=True, null=True)
    opponent_possession = models.FloatField(blank=True, null=True)
    opponent_directness = models.FloatField(blank=True, null=True)
    opponent_pace_towards_goal = models.FloatField(blank=True, null=True)
    opponent_gk_pass_distance = models.FloatField(blank=True, null=True)
    opponent_gk_long_pass_ratio = models.FloatField(blank=True, null=True)
    opponent_ppda = models.FloatField(blank=True, null=True)
    opponent_defensive_distance_ppda = models.FloatField(blank=True, null=True)
    opponent_opp_passing_ratio = models.FloatField(blank=True, null=True)
    opponent_deep_completions = models.FloatField(blank=True, null=True)
    opponent_opp_final_third_pass_ratio = models.FloatField(blank=True, null=True)
    opponent_ball_in_play_time = models.FloatField(blank=True, null=True)
    opponent_aggression = models.FloatField(blank=True, null=True)
    opponent_np_xgd = models.FloatField(blank=True, null=True)
    opponent_passing_ratio = models.FloatField(blank=True, null=True)
    opponent_pressures = models.IntegerField(blank=True, null=True)
    opponent_counterpressures = models.IntegerField(blank=True, null=True)
    opponent_pressure_regains = models.IntegerField(blank=True, null=True)
    opponent_counterpressure_regains = models.IntegerField(blank=True, null=True)
    opponent_defensive_action_regains = models.IntegerField(blank=True, null=True)
    opponent_yellow_cards = models.IntegerField(blank=True, null=True)
    opponent_second_yellow_cards = models.IntegerField(blank=True, null=True)
    opponent_red_cards = models.IntegerField(blank=True, null=True)
    opponent_fhalf_pressures = models.IntegerField(blank=True, null=True)
    opponent_fhalf_counterpressures = models.IntegerField(blank=True, null=True)
    opponent_crosses_into_box = models.IntegerField(blank=True, null=True)
    opponent_successful_crosses_into_box = models.IntegerField(blank=True, null=True)
    opponent_successful_box_cross_ratio = models.FloatField(blank=True, null=True)
    opponent_average_defensive_x = models.FloatField(blank=True, null=True)
    opponent_counter_attacks = models.FloatField(blank=True, null=True)
    opponent_deep_completions_with_shot = models.FloatField(blank=True, null=True)
    opponent_deep_completion_rate = models.FloatField(blank=True, null=True)
    opponent_deep_completion_shot_rate = models.FloatField(blank=True, null=True)
    opponent_pressure_regain_rate = models.FloatField(blank=True, null=True)
    opponent_counterpressure_regain_rate = models.FloatField(blank=True, null=True)
    opponent_deep_completions_after_crosses = models.FloatField(blank=True, null=True)
    opponent_deep_completions_after_cutbacks = models.FloatField(blank=True, null=True)
    opponent_deep_completions_after_counters = models.FloatField(blank=True, null=True)
    opponent_avg_weighted_age = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team_event_data'


class User(models.Model):
    username = models.CharField(unique=True, max_length=100, db_collation='Latin1_General_CI_AS')
    hashed_password = models.CharField(max_length=255, db_collation='Latin1_General_CI_AS')
    role = models.CharField(max_length=50, db_collation='Latin1_General_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
