# teams/labels.py

import re

def norm_comp_key(s: str | None) -> str:
    if not s:
        return ""
    s = s.strip()
    # 1) Alle Varianten von Apostroph in ein normales ' umwandeln
    # 2) Mehrfach-Apostrophe -> ein Apostroph
    s = re.sub(r"[\u2019\u2018`´']+", "'", s)
    # 3) Leerzeichen rund um Apostroph entfernen: "ha ' al" -> "ha'al"
    s = re.sub(r"\s*'\s*", "'", s)
    # 4) Mehrfachspaces normalisieren
    s = re.sub(r"\s+", " ", s)
    return s.casefold()

# spalten namen werden übersetzt und eine kleine legende hinzugefügt
# metriken werden kategorisiert 

COLUMN_LABELS = {
    "op_shots": ("Schüsse Sp", "Sp: aus dem Spiel", "int"),
    "op_shots_outside_box": ("Schüsse außerhalb der Box Sp", "Sp: aus dem Spiel", "int"),
    "sp_shots": ("Schüsse nach Standards", None, "int"),
    "op_xg": ("xG Sp", "Sp: aus dem Spiel", "float"),
    "sp_xg": ("xG St", "St: Standards", "float"),
    "np_xg_per_shot": ("xG pro Schuss, oE", "Durchschnittliche xG pro Schuss, oE: ohne Elfmeter", "float"),
    "op_shot_distance": ("Schussdistanz Sp", "Durchschnittliche Schussdistanz, Sp: aus dem Spiel", "float"),
    "sp_shot_distance": ("Schussdistanz St", "Durchschnittliche Schussdistanz aus Standards", "float"),
    "possession": ("Ballbesitz", None, "percent"),
    "directness": ("Direktheit", "Verhätlnis der Distanz in Richtung Tor zur Gesamtdistanz im Ballbesitz vor einem Schuss. hohe Werte = sehr direkter Angriff, niedrige Werte = viel Querspiel/Aufbau.", "float"),
    "pace_towards_goal": ("Angriffstempo", "Tempo des Angriffs vom Ballgewinn bis zum Schuss (m/s)", "float"),
    "box_cross_ratio": ("Anteil Flanken bei Straufraum-Pässen (%)", "Wie viele der Bälle in den Straufraum sind Flanken. (Alle , auch nicht angekommene)", "percent"),
    "passes_inside_box": ("Pässe im Straufraum", "Anzahl der innerhalb des Straufraums erfolgreich gespielten Pässe", "int"),   
    "corners": ("Ecken", None, "int"),
    "corner_xg": ("xG Ecken", None, "float"),
    "xg_per_corner": ("xG pro Ecke", "Durchschnittlicher xG Wert der Schüsse, die aus Ecken entstehen", "float"),
    "free_kicks": ("Freistöße", None, "int"),
    "free_kick_xg": ("xG Freistöße", None, "float"),
    "xg_per_free_kick": ("xG pro indirekten Freistoß", "Durchschnittlicher xG Wert der Schüsse, die aus indirekten Freistößen entstehen", "float" ),
    "direct_free_kicks": ("Direkte Freistöße", None, "float"),
    "direct_free_kick_xg": ("xG direkte Freistöße", None, "float"),
    "xg_per_direct_free_kick": ("xG pro direktem Freistoß", "Durchschnittlicher xG Wert der direkten Freistößen", "float"),
    "goals": ("Tore", None, "int"),
    "gk_pass_distance": ("GK Durchschnittliche Passlänge ", "Durchschnittliche Passlänge beim Spielaufbau", "float"),
    "gk_long_pass_ratio": ("GK Erfolgsquote lange Bälle", "Anteil erfolgreicher langer Torwartpässe (%)", "percent"),
    "opponent_gk_long_pass_ratio": ("GK Erfolgsquote lange Bälle Gegner", "Anteil erfolgreicher langer Torwartpässe des Gegners (%)", "percent"),
    "ppda": ("PPDA", "Anzahl der vom Gegner gespielten Pässe pro eigener Defensivaktion ( Tackling, Interception, Foul) im Angriffsdrittel, Maß für Pressingintensität", "float"),
    "average_defensive_x": ("Defensivlinien-Höhe", "Durchschnittliche Distanz vom eigenen Tor, aus der Defensivaktionen ausführt werden", "float"),
    "opp_passing_ratio": ("Passquote", None, "percent"),
    "opp_final_third_pass_ratio": ("F3-Quote (%)", "Prozentualer Anteil der Pässe des Gegners ins letzte Drittel, die erfolgreich ankommen", "percent"),
    "opponent_op_shots": ("Schüsse Gegner Sp", "Sp: aus dem Spiel", "int"),
    "opponent_op_shots_outside_box": ("Schüsse Gegner außerhalb der Box Sp", "Sp: aus dem Spiel", "int"),
    "opponent_sp_shots": ("Schüsse Gegner St", "St: Standards", "int"),
    "opponent_op_xg": ("xG Gegner Sp", "Sp: aus dem Spiel", "float"),
    "opponent_sp_xg": ("xG Gegner St", "St: Standards", "float"),
    "np_xgd": ("xG Differenz, oE", "oE: ohne Elfmeter", "float"),
    "opponent_np_xg_per_shot": ("xG pro Schuss Gegner oE", "oE: ohne Elfmeter", "float"),
    "opponent_op_shot_distance": ("Schussdistanz Gegner Sp", "Durchschnittliche Schussdistanz des Gegners, Sp: aus dem Spiel", "float"),
    "opponent_passes_inside_box": ("Gegnerische Pässe im Strafraum (erfolgreich)", "Anzahl der vom Gegner innerhalb des Strafraums erfolgreich gespielten Pässe", "int"),
    "throw_in_xg": ("xG Einwürfe", None, "float"),
    "xg_per_throw_in": ("xP pro Einwurf", "Durchschnittlicher xG Wert der Schüsse, die aus einem Einwurf entstehen", "float"),
    "counter_attacking_shots": ("Konter-Schüsse", "Anzahl der Schüsse, die innerhalb von 15 Sekunden nach einem Ballbesitzgewinn in der eignen Hälfte entstehen", "int"),
    "high_press_shots": ("Hohe-Presssing-Schüsse", "Anzahl der Schüsse die aus Balgewinnen von 5 Sekunden nach einer Defensivaktion in der gegnerischen Hälfte entstehen", "int"),
    "shots_in_clear": ("Shots in Clear", "Anzahl der Schüsse, bei denen nur der gegnerische Torhüter zwischen Schützen und Tor stand ( innerhalb des Korridors zwischen Schützen und Torstange)", "int"),
    "opponent_counter_attacking_shots": ("Konter-Schüsse Gegner", "Anzahl der Schüsse, die innerhalb von 15 Sekunden nach einem Ballverlust in der gegnerischen Hälfte entstehen", "int"),
    "opponent_shots_in_clear": ("Shots in Clear Gegner", "Anzahl der Schüsse, bei denen nur der Torhüter zwischen Schützen und Tor stand ( innerhalb des Korridors zwischen Schützen und Torstange)", "int"),
    "aggressive_actions": ("Agressive Aktionen", "Anzahl der Tacklings, Pressures und Fouls einer Mannschaft innerhalb von 2 Sekunden nach gegnerischer Ballannahme", "int"),
    "aggression": ("Aggression", "Anteil der gegnrischen Ballanahmen, die innerhalb von 2 Sekunden getackelt, gepresst oder gefoult werden (%)", "percent"),
    "penalty_goals": ("Elfmetertore", None, "int"),
    "opponent_penalty_goals": ("erhaltene Elfmetertore", None, "int"),
    "shots_from_corners": ("Schüsse nach Ecken", None, "int"),
    "goals_from_corners": ("Tore nach Ecken", None, "int"),
    "shots_from_free_kicks": ("Schüsse nach Freisstößen", None, "int"),
    "goals_from_free_kicks": ("Tore aus Freistößen", None, "int"),
    "direct_free_kick_goals": ("Tore nach direkten Freistößen", None, "int"),
    "shots_from_direct_free_kicks": ("Schüsse nach direkten Freistößen", None, "int"),
    "shots_from_throw_ins": ("Schüsse nach Einwürfen", None, "int"),
    "goals_from_throw_ins": ("Tore nach Einwürfen", None, "int"),
    "opponent_direct_free_kick_goals": ("Tore Gegner nach direkten Freistößen", None, "int"),
    "opponent_shots_from_direct_free_kicks": ("Schüsse Gegner nach direkten Freistößen", None, "int"),
    "opponent_corners": ("Ecken Gegner", None, "int"),
    "opponent_corner_xg": ("xG Ecken Gegner", None, "float"),
    "opponent_shots_from_corners": ("Schüsse Gegner nach Ecken", None, "int"),
    "opponent_goals_from_corners": ("Tore Gegner nach Ecken", None, "int"),
    "opponent_free_kicks": ("Freistöße Gegner", None, "int"),
    "opponent_free_kick_xg": ("xG Freistöße Gegner", None, "float"),
    "opponent_shots_from_free_kicks": ("Schüsse Gegner nach Freistößen", None, "int"),
    "opponent_goals_from_free_kicks": ("Tore Gegner nach Freistößen", None, "int"),
    "opponent_direct_free_kicks": ("Direkte Freistöße Gegner", None, "int"),
    "opponent_direct_free_kick_xg": ("xG direkte Freistöße Gegner", None, "float"),
    "opponent_throw_in_xg": ("xG Einwürfe Gegner", None, "float"),
    "opponent_shots_from_throw_ins": ("Schüsse Gegner nach Einwürfen", None, "int"),
    "opponent_goals_from_throw_ins": ("Tore Gegner nach Einwürfen", None, "int"),
    "corner_shot_ratio": ("Schussquote nach Ecken", "Anzahl der Schüsse pro Ecke", "percent"),
    "corner_goal_ratio": ("Torquote nach Ecken", "Anzahl der Tore pro Ecke", "percent"),
    "free_kick_shot_ratio": ("Schussquote nach Freistößen", "Anzahl der Schüsse pro Freistoß", "percent"),
    "free_kick_goal_ratio": ("Torquote nach Freistößen", "Anzahl der Tore pro Freistoß", "percent"),
    "direct_free_kick_goal_ratio": ("Torquote nach direkten Freistößne", None, "percent"),
    "throw_in_shot_ratio": ("Schussquote nach Einwürfen", "Anzahl der Schüsse nach Einwürfen", "percent"),
    "throw_in_goal_ratio": ("Torquote nach Einwürfen", "Anzahl der Tore nach Einwürfen", "percent"),
    "opponent_xg_per_corner": ("xG pro Ecke Gegner", "Durchschnittlicher xG Wert der Schüsse, die aus Ecken des Gegners entstehen", "float"),
    "opponent_corner_shot_ratio": ("Schussquote nach Ecken Gegner", "Anzahl der Schüsse pro Ecke des Gegners", "percent"),
    "opponent_corner_goal_ratio": ("Torquote nach Ecken Gegner", "Anzahl der Tore pro Ecke des Gegners", "percent"),
    "opponent_xg_per_free_kick": ("xG pro indirekten Freistoß Gegner", "Durchschnittlicher xG Wert der Schüsse, die aus indirekten Freistößen des Gegners entstehen", "float"),
    "opponent_free_kick_shot_ratio": ("Schussquote nach Freistößen Gegner", "Anzahl der Schüsse pro Freistoß des Gegners", "percent"),
    "opponent_free_kick_goal_ratio": ("Torquote nach Freistößen Gegner", "Anzahl der Tore pro Freistoß des Gegners", "percent"),
    "opponent_xg_per_direct_free_kick": ("xG pro direktem Freistoß Gegner", "Durchschnittlicher xG Wert der direkten Freistöße des Gegners", "float"),
    "opponent_direct_free_kick_goal_ratio": ("Torquote nach direkten Freistößen Gegner", "Anzahl der Tore pro direkten Freistoß des Gegners", "percent"),
    "opponent_xg_per_throw_in": ("xG pro Einwurf Gegner", "Durchschnittlicher xG Wert der Schüsse, die aus Einwürfen des Gegners entstehen", "float"),
    "opponent_throw_in_shot_ratio": ("Schussquote nach Einwürfen Gegner", "Anzahl der Schüsse nach Einwürfen des Gegners", "percent"),
    "opponent_throw_in_goal_ratio": ("Torquote nach Einwürfen Gegner", "Anzahl der Tore nach Einwürfen des Gegners", "percent"),
    "sp": ("Standards", "Anzahl der Standards", "int"),
    "xg_per_sp": ("xG pro Standard", "Durchschnittlicher xG Wert der Schüsse, die aus Standardsituationen entstehen", "float"),
    "sp_shot_ratio": ("Schussquote nach Standards", "Anzahl der Schüsse pro Standardsituation", "percent"),
    "sp_goals": ("Tore nach Standards", "Anzahl der Tore, die aus Standardsituationen erzielt wurden", "int"),
    "sp_goal_ratio": ("Torquote nach Standards", "Anzahl der Tore pro Standardsituation", "percent"),
    "opponent_sp": ("Standards Gegner", "Anzahl der Standardsituationen des Gegners", "int"),
    "opponent_xg_per_sp": ("xG pro Standard Gegner", "Durchschnittlicher xG Wert der Schüsse, die aus Standardsituationen des Gegners entstehen", "float"),
    "opponent_sp_shot_ratio": ("Schussquote nach Standards Gegner", "Anzahl der Schüsse pro Standardsituation des Gegners", "percent"),
    "opponent_sp_goals": ("Tore nach Standards Gegner", "Anzahl der Tore, die der Gegner aus Standardsituationen erzielt hat", "int"),
    "opponent_sp_goal_ratio": ("Torquote nach Standards Gegner", "Anzahl der Tore pro Standardsituation des Gegners", "percent"),
    "penalties_won": ("Erlangte Elfmeter", "Anzahl der von der Mannschaft gewonnenen Strafstöße", "int"),
    "opponent_penalties": ("Erlangte Elfmeter Gegner", "Anzahl der vom Gegner gewonnenen Strafstöße", "int"),
    "completed_dribbles": ("Erfolgreiche Dribblings", "Dribblings: Ein Versuch eines Spielers, einen Gegenspieler zu überwinden. Anzahl der erfolgreichen Dribblings (Spieler setzt sich gegen einen Gegner durch)", "int"),
    "failed_dribbles": ("Misslungene Dribblings", "Dribblings: Ein Versuch eines Spielers, einen Gegenspieler zu überwinden. Anzahl der misslungenen Dribblings (Ballverlust gegen einen Gegner)", "int"),
    "total_dribbles": ("Gesamtanzahl Dribblings", "Dribblings: Ein Versuch eines Spielers, einen Gegenspieler zu überwinden. Summe aus erfolgreichen und misslungenen Dribblings", "int"),
    "opponent_completed_dribbles": ("Erfolgreiche Dribblings Gegner", "Dribblings: Ein Versuch eines Spielers, einen Gegenspieler zu überwinden. Anzahl der erfolgreichen Dribblings des Gegners", "int"),
    "opponent_failed_dribbles": ("Misslungene Dribblings Gegner", "Dribblings: Ein Versuch eines Spielers, einen Gegenspieler zu überwinden. Anzahl der misslungenen Dribblings des Gegners", "int"),
    "opposition_dribble_ratio": ("Dribbling-Erfolgsquote Gegner", "Dribblings: Ein Versuch eines Spielers, einen Gegenspieler zu überwinden. Anteil der erfolgreichen Dribblings des Gegners an allen Dribbling-Versuchen (%)", "percent"),
    "dribble_ratio": ("Dribble-Erfolgsquote", "Dribblings: Ein Versuch eines Spielers, einen Gegenspieler zu überwinden. Anteil der erfolgreichen Dribllings (%)", "percent"),
    "opponent_high_press_shots": ("Hohe-Pressing-Schüsse Gegner", "Anzahl der Schüsse, die aus Ballverlusten innerhalb von 5 Sekunden nach einer Defensivaktion (Pressing, Tackling, Interception, geblockter Pass) in der eigenen Hälfte entstehen", "int"),
    "passing_ratio": ("Passquote", None, "percent"),
    "pressures": ("Pressures", "Anzahl der Aktionen, bei denen ein Spieler Druck auf den ballführenden Gegenspieler ausübt","int"),
    "counterpressures": ("Gegenpressing", "Anzahl der Pressures, die innerhalb von 5 Sekunden nach einem Ballverlust ausgeübt werden. Pressure: Eine Aktion bei der ein Spieler Druck auf den ballführenden Gegenspieler ausübt", "int"),
    "pressure_regains": ("Erfolgreiche Pressure", "Anzahl der Ballgewinne innerhalb von 5 Sekunden, nachdem ein Spieler Druck auf einen Gegenspieler ausgeübt hat", "int"),
    "opponent_pressure_regains": ("Erfolgreiche Pressure Gegner", "Anzahl der Ballverluste innerhalb von 5 Sekunden, nachdem ein Gegenspieler Druck auf einen Spieler ausgeübt hat", "int"),
    "counterpressure_regains": ("Erfolgreiche Gegenpressing", "Anzahl der Ballgewinne innerhalb von 5 Sekunden, nachdem ein Spieler im Gegenpressing Druck auf einen Gegenspieler ausgeübt hat", "int"),
    "defensive_action_regains": ("Erfolgreiche Defensiv-Aktion", "Anzahl der Ballgewinne innerhalb von 5 Sekunden nach einer defensiven Aktion (z. B. Tackling, Interception, geblockter Pass oder Pressure)","int"),
    "yellow_cards": ("Gelbe Karten", None, "int"),
    "second_yellow_cards": ("Zweite Gelbe Karte", None, "int"),
    "red_cards": ("Rote Karte", None, "int"),

    "fhalf_pressures": ("Pressures F2", "Anzahl der Pressures, die in der gegnerischen Spielfeldhälfte ausgeübt werden", "int"),

    "fhalf_counterpressures": ("Gegenpressing F2", "Anzahl der Gegenpressing, die in der gegnerischen Spielfeldhälfte ausgeübt werden", "int"),
    "fhalf_pressures_ratio": ("Pressure F2 (%)", "Prozentualer Anteil der Pressures, die in der gegnerischen Spielfeldhälfte ausgeübt werden", "percent"),
    "fhalf_counterpressures_ratio": ("Gegenpressing F2 (%)", "Prozentualer Anteil der Gegenpressing, die in der gegnerischen Spielfeldhälfte ausgeübt werden", "percent"),
    "crosses_into_box": ("Flanken in den Strafraum", None,"int"),
    "successful_crosses_into_box": ("Erfolgreiche Flanken in den Strafraum", "Anzahl der Flanken, die erfolgreich in den Strafraum gespielt werden (Mitspieler erreicht)","int"),
    "successful_box_cross_ratio": ("Anteil erfolgreiche Flanken in den Strafraum (%)", "Wie viel Prozent der erfolgreichen Pässe in den Strafraum waren Flanken.", "percent"),
    "deep_progressions": ("Deep Progressions", "Anzahl der Pässe, Dribblings und Ballführungen in das gegnerische letzte Drittel", "int"),
    "opponent_deep_progressions": ("Deep Progressions Gegner", "Anzahl der Pässe, Dribblings und Ballführungen des Gegners in das letzte Drittel", "int"),
    "obv": ("On-Ball Value (OBV)", "Modellbasierter Wert, der den Einfluss von Aktionen auf die Torchancen misst (positiv = eigene Chancen steigen, negativ = Risiko Gegentor steigt)", "float"),
    "obv_pass": ("OBV Pässe", "On-Ball Value (OBV) der Pässe: modellbasierter Wert, der den Einfluss von gespielten Pässen auf die Torchancen misst (positiv = eigene Chancen steigen, negativ = Risiko Gegentor steigt)", "float"),
    "obv_shot": ("OBV Schüsse", "On-Ball Value (OBV) der Schüsse: bewertet, wie stark ein Schuss die Torchancen gegenüber der Ausgangssituation verändert (Basis: Post-Shot xG; positiv = Chancen steigen, negativ = Chancen sinken)", "float"),
    "obv_defensive_action": ("OBV Defensivaktionen", "On-Ball Value (OBV) von Defensivaktionen: bewertet, wie stark Tacklings, Interceptions oder Blocks die Torwahrscheinlichkeit beeinflussen (positiv = Gegentor unwahrscheinlicher, negativ = Gegentor wahrscheinlicher)", "float"),
    "obv_dribble_carry": ("OBV Dribblings", "On-Ball Value (OBV) von Dribblings und Ballführungen: bewertet, wie stark diese Aktionen die Torwahrscheinlichkeit beeinflussen (positiv = Chancen steigen, negativ = Chancen sinken)", "float"),
    "obv_gk": ("OBV Torwart", "On-Ball Value (OBV) des Torwarts: bewertet, wie stark Torwartaktionen (z. B. Paraden) die Torwahrscheinlichkeit beeinflussen (positiv = Gegentor unwahrscheinlicher, negativ = Gegentor wahrscheinlicher)", "float"),
    "opponent_obv": ("On-Ball Value (OBV) Gegner", "Modellbasierter Wert, der den Einfluss der gegnerischen Aktionen auf die Torchancen misst (positiv = Chancen des Gegners steigen, negativ = Risiko Gegentor für den Gegner steigt)", "float"),
    "opponent_obv_pass": ("OBV Pässe Gegner", "On-Ball Value (OBV) der gegnerischen Pässe: bewertet, wie stark gegnerische Pässe die Torwahrscheinlichkeit beeinflussen (positiv = Chancen des Gegners steigen, negativ = Chancen sinken)", "float"),
    "opponent_obv_defensive_action": ("OBV Defensivaktionen Gegner", "On-Ball Value (OBV) von gegnerischen Defensivaktionen: bewertet, wie stark Tacklings, Interceptions oder Blocks des Gegners die Torwahrscheinlichkeit beeinflussen", "float"),
    "opponent_obv_dribble_carry": ("OBV Dribblings Gegner", "On-Ball Value (OBV) von gegnerischen Dribblings und Ballführungen: bewertet, wie stark diese Aktionen die Torwahrscheinlichkeit beeinflussen", "float"),
    "opponent_obv_gk": ("OBV Torwart Gegner", "On-Ball Value (OBV) des gegnerischen Torwarts: bewertet, wie stark gegnerische Torwartaktionen (z. B. Paraden) die Torwahrscheinlichkeit beeinflussen", "float"),
    "obv_shot_nconceded": ("OBV Schüsse Gegentor-Risiko", "On-Ball Value (OBV) der gegnerischen Schüsse: bewertet, wie stark gegnerische Schüsse die eigene Torchance verringern bzw. das Gegentor-Risiko erhöhen", "float"),
    "successful_passes": ("Erfolgreiche Pässe", "Anzahl der beim Mitspieler angekommenen Pässe", "int"),
    "opponent_successful_passes": ("Erfolgreiche Pässe Gegner", "Anzahl der Pässe des Gegners, die beim Mitspieler angekommen sind", "int"),
    "op_passes": ("Pässe Sp", "Anzahl der gespielten Pässe, Sp: aus dem Spiel", "int"),
    "avg_weighted_age": ("Durchschnittsalter", "Gewichtet nach Spielminuten", "float"),
    "counter_attacks": ("Konterangriffe", "Anzahl der Angriffe nach Ballgewinn außerhalb des gegnerischen Drittels, die mindestens 75% direkt zum Tor gespielt wurden und mindestens 18 Meter Raumgewinn erzielten", "int"),
    "deep_completions": ("Deep Completions", "Anzahl erfolgreicher Aktionen (Pass, Dribbling, Carry, Flanken...), die außerhalb des Strafraums starten und innerhalb des Strafraums enden", "int"),
    "opponent_deep_completions": ("Deep Completions Gegner", "Anzahl erfolgreicher Aktionen des Gegners (Pass, Dribbling, Carry, Flanken...), die außerhalb des Strafraums starten und innerhalb des Strafraums enden", "int"),
    "deep_completions_after_crosses": ("Deep Completions nach Flanken", "Anzahl der Deep Completions, die durch eine Flanke entstanden sind", "int"),
    "deep_completions_after_cutbacks": ("Deep Completions nach Cutbacks", "Anzahl der Deep Completions, die durch einen Cutback entstanden sind. Cutbacks: Flache Pässe aus den seitlichen Zonen nahe der Grundlinie in den zentralen Straufraumbereich vor dem Tor", "int"),
    "deep_completions_after_counters": ("Deep Completions nach Kontern", "Anzahl der Deep Completions, die Teil eines Konterangriffs waren. Konter: Angriffe nach Ballgewinn außerhalb des gegnerischen Drittels, die mindestens 75% direkt zum Tor gespielt wurden und mindestens 18 Meter Raumgewinn erzielten","int"),
    "deep_completions_with_shot": ("Deep Completions mit Abschluss", "Anzahl der Deep Completions, nach denen im gleichen Ballbesitz zumindest ein Schuss erfolgte", "int"),
    "deep_completion_rate": ("Deep Progression zu Deep Completions", "Anteil der Deep Progressions, die in Deep Completions enden (%)", "percent"),
    "opponent_deep_completion_rate": ("Deep Progression zu Deep Completions Gegner", "Anteil der Deep Progressions, in denen ein Deep Completion zugelassen wird (%)", "percent"),
    "deep_completion_shot_rate": ( "Deep Completion mit Abschluss (%)", "Anteil der Deep Completions, nach denen im selben Ballbesitz ein Schuss erfolgte (%)", "percent"),
    "opponent_deep_completion_shot_rate": ( "Deep Completion mit Abschluss (%) Gegner", "Anteil der Deep Completions des Gegners, nach denen im selben Ballbesitz ein Schuss zugelassen wird (%)", "percent"),
    "pressure_regain_rate": ("Erfolgreiche Pressure Quote", "Anteil der Pressures, die innerhalb von 5 Sekunden zu einem Ballgewinn führen (%)", "percent"),
    "counterpressure_regain_rate": ("Erfolgreiche Gegenpressure Quote", "Anteil der Gegenpressing, die innerhalb von 5 Sekunden zu einem Ballgewinn führen (%)", "percent"),
    "opponent_possessions": ("Ballbesitzphasen Gegner", "Absolute Anzahl der Ballbesitzphasen des Gegners", "int"),
    "opponent_possession": ("Ballbesitz Gegner", None,"percent"),
    "opponent_directness": ( "Direktheit Gegner", "Verhätlnis der Distanz in Richtung Tor zur Gesamtdistanz im Ballbesitz vor einem Schuss. hohe Werte = sehr direkter Angriff, niedrige Werte = viel Querspiel/Aufbau.", "float"),
    "opponent_pace_towards_goal": ("Angriffstempo Gegner", "Tempo des Angriffs vom Ballgewinn bis zum Schuss (m/s)", "float"),
    "opponent_gk_pass_distance": ("GK Durchschnittliche Passlänge Gegner", "Durchschnittliche Passlänge beim Spielaufbau des gegnerischen Torwarts", "float"),
    "opponent_ppda": ("PPDA Gegner", "Anzahl der vom Team gespielten Pässe pro gegnerischer Defensivaktion (Tackling, Interception, Foul) im Angriffsdrittel; Maß für die Pressingintensität des Gegners", "float"),
    "opponent_opp_passing_ratio": ("Passquote Gegner", "Sp: aus dem Spiel", "percent"),
    "opponent_opp_final_third_pass_ratio": ("F3-Quote Gegner (%)", "Prozentualer Anteil der gegnerischen Pässe ins letzte Drittel, die erfolgreich ankommen", "percent"),
    "opponent_aggression": ("Aggression Gegner", "Anteil der eigenen Ballannahmen, die innerhalb von 2 Sekunden vom Gegner getackelt, gepresst oder gefoult werden (%)", "percent"),
    "opponent_passing_ratio": ("Passquote Gegner (gesamt)", "Anteil der erfolgreichen Pässe des Gegners (%)", "percent"),
    "opponent_pressures": ("Pressures Gegner", "Anzahl der Aktionen, bei denen ein gegnerischer Spieler Druck auf den ballführenden Spieler ausübt", "int"),
    "opponent_counterpressures": ("Gegenpressing Gegner", "Anzahl der Pressures, die der Gegner innerhalb von 5 Sekunden nach einem Ballverlust ausgeübt hat", "int"),
    "opponent_counterpressure_regains": ("Erfolgreiche Gegenpressing Gegner", "Anzahl der Ballgewinne des Gegners innerhalb von 5 Sekunden, nachdem er im Gegenpressing Druck ausgeübt hat", "int"),
    "opponent_defensive_action_regains": ("Erfolgreiche Defensiv-Aktionen Gegner", "Anzahl der Ballgewinne des Gegners innerhalb von 5 Sekunden nach einer defensiven Aktion (z. B. Tackling, Interception, geblockter Pass,...)", "int"),
    "opponent_fhalf_pressures": ("Pressures Gegner F2", "Anzahl der Pressures des Gegners in der eigenen Spielfeldhälfte", "int"),

    "opponent_fhalf_counterpressures": ("Gegenpressing Gegner F2", "Anzahl der Gegenpressing des Gegners in der eigenen Spielfeldhälfte (aus Teamsicht also gegnerische Offensivhälfte)", "int"),
    "opponent_crosses_into_box": ("Zugelassene Flanken in den Strafraum", None, "int"),
    "opponent_successful_crosses_into_box": ("Erfolgreiche zugelassene Flanken in den Straufram", "Anzahl der vom Gegner in den Strafraum gespielten erfolgreichen Flanken (Mitspieler erreicht)", "int"),
    "opponent_successful_box_cross_ratio": ("Anteil erfolgreiche Flanken in den Strafraum Gegner", "Wie viel Prozent der zugelassenen Bälle in den Straufraum, die beim Gegenspieler angekommen sind, waren Flanken", "percent"),
    "opponent_average_defensive_x": ("Defensivlinien-Höhe Gegner", "Durchschnittliche Distanz vom eigenen Tor, aus der der Gegner seine Defensivaktionen ausführt", "float"),
    "opponent_counter_attacks": ("Konterangriffe Gegner", "Anzahl der Konterangriffe des Gegners nach Ballgewinn außerhalb des Drittels der verteidigenden Mannschaft, die mindestens 75% direkt zum Tor gespielt wurden und mindestens 18 Meter Raumgewinn erzielten", "int"),
    "opponent_deep_completions_with_shot": ( "Deep Completions mit Abschluss Gegner", "Anzahl der gegnerischen Deep Completions, nach denen im gleichen Ballbesitz zumindest ein Schuss erfolgte", "int"),
    "opponent_pressure_regain_rate": ("Erfolgreiche Pressure Quote Gegner", "Anteil der gegnerischen Pressures, die innerhalb von 5 Sekunden zu einem Ballgewinn führen (%)", "percent"),
    "opponent_counterpressure_regain_rate": ("Erfolgreiche Gegenpressing Quote Gegner", "Anteil der gegnerischen Gegenpressing, die innerhalb von 5 Sekunden zu einem Ballgewinn führen (%)", "percent"),
    "opponent_deep_completions_after_crosses": ("Deep Completions nach Flanken Gegner", "Anzahl der gegnerischen Deep Completions, die durch eine Flanke entstanden sind", "int"),
    "opponent_deep_completions_after_cutbacks": ("Deep Completions nach Cutbacks Gegner", "Anzahl der gegnerischen Deep Completions, die durch einen Cutback entstanden sind", "int"),
    "opponent_deep_completions_after_counters": ("Deep Completions nach Kontern Gegner", "Anzahl der gegnerischen Deep Completions, die Teil eines Konterangriffs waren", "int"),
    "opponent_avg_weighted_age": ("Durchschnittsalter Gegner", "Gewichtetes Durchschnittsalter der gegnerischen Spieler nach Spielminuten", "float"),
    "opponent_goals": ("Gegentore", None, "int"),
    "possessions": ("Ballbesitzphasen", "Absolute Anzahl der Ballbesitzphasen", "int"),
    "opponent_fhalf_counterpressures": ("Gegenpressing F2 Gegner", None, "int"),





}

METRIC_CATEGORIES = {

    # Metriken die nur über NUR über ALLE angezeigt werden
    "Core_ALLE": ["goals", "opponent_goals",
                  "op_xg", "opponent_op_xg", 
                  "penalty_goals", "opponent_penalty_goals", 
                  "xg_per_sp", "opponent_xg_per_sp",
                  "sp_goals", "opponent_sp_goals", 
                  "sp_goal_ratio", "opponent_sp_goal_ratio",
                  "yellow_cards", "second_yellow_cards", "red_cards", 
                  "deep_progressions", "opponent_deep_progressions",
                  "obv", "opponent_obv", 
                  "avg_weighted_age"],

    # metriken die auf Spieltag - Übersicht angezeigt werden 
    "Spieltag_Übersicht": ["op_xg",  "opponent_op_xg",
                           "op_shots", "opponent_op_shots",
                           "possession", "opponent_possession", 
                           "opp_passing_ratio", "opponent_opp_passing_ratio",
                           "successful_passes", "opponent_successful_passes", 
                           "sp", "opponent_sp", 
                           "obv", "opponent_obv", 
                           "deep_completions", "opponent_deep_completions",
                           "deep_progressions", "opponent_deep_progressions",
                           "avg_weighted_age",  "opponent_avg_weighted_age",
                           ],











    # metriken die auf Offensive Allgemein angezeigt werden
    "Offensiv_Allgemein": ["op_shots", "op_xg",
                           "completed_dribbles", "failed_dribbles",
                           "total_dribbles", "dribble_ratio",
                           "obv_dribble_carry", 
                           "deep_progressions", "deep_completions",
                           "deep_completion_rate",
                           "obv", 
                           "obv_pass", 
                           "successful_passes", "op_passes", 
                           ],

    # hier soll rein "Ballbesitz Dauer" = ( ball_in_play_time * possession) / possessions
    "Offensive_Spiel": ["directness", "pace_towards_goal", 
                        "deep_progressions", 
                        "obv_pass",
                        "deep_completion_rate",
                        "opponent_ppda",
                        "opponent_aggression",
                        "opponent_pressures", "opponent_pressure_regains", "opponent_pressure_regain_rate",
                        "opponent_defensive_action_regains", "possessions",
                        "opponent_fhalf_pressures", # selber rechnen opponent_fhalf_pressures_regains
                        "opponent_average_defensive_x"],

    "Offensive_F3": ["box_cross_ratio", "successful_box_cross_ratio",
                     "crosses_into_box","successful_crosses_into_box",
                     "corners", 
                     "throw_in_xg",
                     "opponent_obv_defensive_action",
                     "deep_progressions", "deep_completions",
                     "deep_completion_rate",
                     "deep_completions_after_crosses",
                     "deep_completions_after_cutbacks",
                     "deep_completions_after_counters",
                     "deep_completions_after_counters",
                     ],

    # chancen + chancen qualität
    "Chancen": ["op_shots_outside_box",
                "op_xg",
                "np_xg_per_shot",
                "op_shot_distance",
                "passes_inside_box",
                "shots_in_clear",
                "penalties_won",
                "obv_shot", "opponent_obv_gk",
                "deep_completions",
                "deep_completions_with_shot", "deep_completion_shot_rate"],











    # transition # counterpressures padj
    "transition": ["counter_attacking_shots", "opponent_counter_attacking_shots",
                   "high_press_shots", "opponent_high_press_shots", 

                   "counterpressures", "counterpressure_regains", 
                   "opponent_counterpressures", "opponent_counterpressure_regains", 

                   "fhalf_counterpressures", "fhalf_counterpressures_ratio", 
                   "opponent_fhalf_counterpressures",  "opponent_fhalf_counterpressures", # opp fhalf counter pre fehlt ?

                   "counterpressure_regain_rate", "opponent_counterpressure_regain_rate",

        
                   "counter_attacks", "deep_completions_after_counters",
                   "opponent_counter_attacks", "opponent_deep_completions_after_counters"],







    #Def Allgemein         # pressures padj machen
    "Def_Allgemein": ["average_defensive_x", "opp_final_third_pass_ratio", "opponent_counter_attacking_shots", "aggressive_actions",
                      "opponent_completed_dribbles", "opponent_failed_dribbles", "opposition_dribble_ratio", "pressures", "pressure_regains",
                      "defensive_action_regains", "fhalf_pressures_ratio", "opponent_deep_progressions", "obv_defensive_action", "opponent_obv",
                      "opponent_obv_pass", "opponent_obv_dribble_carry", "pressure_regain_rate", "opponent_directness", "opponent_pace_towards_goal",
                      "opponent_opp_final_third_pass_ratio", "fhalf_pressures", "aggression"],

    #Def Spielaufbau Gegner.  # "Ballbesitz Dauer" = ( ball_in_play_time * possession) / possessions vom gegner
    "Def_Spielaufbau_Gegner": ["opponent_gk_long_pass_ratio", "ppda", "fhalf_pressures", "fhalf_counterpressures_ratio", "opponent_possessions",
                               "opponent_directness", "opponent_pace_towards_goal", "opponent_gk_pass_distance",
                               "opponent_opp_final_third_pass_ratio", "aggression"],

    #Def Box
    "Boxverteidigung": ["opponent_op_shots", "opponent_op_shots_outside_box", "opponent_np_xg_per_shot", "opponent_op_shot_distance",
                        "opponent_passes_inside_box", "opponent_shots_in_clear", "opponent_corners", "opponent_throw_in_xg",
                        "opponent_penalties", "obv_defensive_action", "obv_gk", "obv_shot_nconceded", "opponent_deep_completions", 
                        "opponent_deep_completion_rate", "opponent_deep_completion_shot_rate", "opponent_crosses_into_box",
                        "opponent_successful_crosses_into_box", "opponent_successful_box_cross_ratio", "opponent_deep_completions_with_shot",
                        "opponent_deep_completions_after_crosses", "opponent_deep_completions_after_cutbacks"],





    # Standards Allgemein
    "Standards_Allgemein": ["sp_xg", "opponent_sp_xg", "sp_shots", "opponent_sp_shots", "free_kick_goal_ratio", "opponent_xg_per_free_kick",
                            "opponent_free_kick_goal_ratio", "sp", "xg_per_sp", "sp_shot_ratio", "sp_goals", "sp_goal_ratio", "opponent_sp", 
                            "opponent_xg_per_sp", "opponent_sp_shot_ratio", "opponent_sp_goals", "opponent_sp_goal_ratio"],

    # Standards Freistöße Off
    "Standards_Freistöße_Off_Allgemein": ["free_kicks", "free_kick_xg", "xg_per_free_kick", "shots_from_free_kicks", "goals_from_free_kicks", 
                                          "free_kick_shot_ratio", "free_kick_goal_ratio", "opponent_free_kick_shot_ratio"],

    # Standards Freistöße Off direkt
    "Standards_Freistöße_Off_Direkt": ["sp_shot_distance", "direct_free_kicks", "direct_free_kick_xg", "xg_per_direct_free_kick", "direct_free_kick_goals",
                                       "shots_from_direct_free_kicks", "direct_free_kick_goal_ratio"],

    # Standards Freistöße Def 
    "standards_freistöße_def_allgemein": ["opponent_free_kicks", "opponent_free_kick_xg", "opponent_shots_from_free_kicks", "opponent_goals_from_free_kicks",
                                          "opponent_xg_per_free_kick", "opponent_free_kick_goal_ratio"],

    # Standards Freistöße Def direkt
    "standards_freistöße_def_direkt": ["opponent_direct_free_kick_goals", "opponent_shots_from_direct_free_kicks", "opponent_direct_free_kicks",
                                       "opponent_direct_free_kick_xg", "opponent_xg_per_direct_free_kick", "opponent_direct_free_kick_goal_ratio"],
   
    # Standards Einfwürfe off
    "standards_einwürfe_off": ["throw_in_xg", "xg_per_throw_in", "shots_from_throw_ins", "goals_from_throw_ins", "throw_in_shot_ratio", "throw_in_goal_ratio"],

    # Standards Einwürfe def
    "standards_einwürfe_def": ["opponent_throw_in_xg", "opponent_shots_from_throw_ins", "opponent_goals_from_throw_ins", "opponent_xg_per_throw_in",
                               "opponent_throw_in_shot_ratio", "opponent_throw_in_goal_ratio"],

    


    # Standards Ecken Off
    "Ecken_Off": ["corners", "corner_xg", "xg_per_corner", "shots_from_corners", "goals_from_corners", "corner_shot_ratio", "corner_goal_ratio"],

    # Standards Ecken Def
    "ecken_def": ["opponent_corners", "opponent_corner_xg", "opponent_shots_from_corners", "opponent_goals_from_corners", "opponent_xg_per_corner",
                  "opponent_corner_shot_ratio", "opponent_corner_goal_ratio"],

    # GK Off 
    "GK_Off": ["gk_pass_distance", "gk_long_pass_ratio"],

    #GK Def
    "GK_def": ["obv_gk", "obv_shot_nconceded"],



    


}




CATEGORY_LABELS = {
    "Core_ALLE": "Basis Team-Werte",
    "Spieltag_Übersicht": "Spieltag – Übersicht",
    "Offensiv_Allgemein": "Offensive – Allgemein",
    "Offensive_Spiel": "Offensive – Spielstruktur",
    "Offensive_F3": "Offensive – Letztes Drittel",
    "Chancen": "Chancen & Qualität",
    "transition": "Umschalten",
    "Def_Allgemein": "Defensive – Allgemein",
    "Def_Spielaufbau_Gegner": "Defensive – Spielaufbau Gegner",
    "Boxverteidigung": "Defensive letztes Drittel",
    "Standards_Allgemein": "Standards – Allgemein",
    "Standards_Freistöße_Off_Allgemein": "Freistöße – Offensive Allgemein",
    "Standards_Freistöße_Off_Direkt": "Freistöße – Offensive Direkt",
    "standards_freistöße_def_allgemein": "Freistöße – Defensive Allgemein",
    "standards_freistöße_def_direkt": "Freistöße – Defensive Direkt",
    "standards_einwürfe_off": "Einwürfe – Offensive",
    "standards_einwürfe_def": "Einwürfe – Defensive",
    "Ecken_Off": "Ecken – Offensive",
    "ecken_def": "Ecken – Defensive",
    "GK_Off": "Torwart – Aufbau",
    "GK_def": "Torwart – Abwehr",
}


METRIC_NICHT = {

    "shot_assists": ("Schuss Assist", None, "int"),
    "throughballs": ("Troughballs", "Bälle die die letzte Linie brechen", None, "int"),
    "passes_into_f3": ("Pässe F3", "Pässe die im letzten Drittel enden", "int"),
    "passes_into_box": ("Pässe i.d. Box", "Pässe die in der Box enden", "int"),
    "cutbacks": ("Cutbacks", "Cutbacks: Flache Pässe aus den seitlichen Zonen nahe der Grundlinie in den zentralen Straufraumbereich vor dem Tor", "int"),
    "harmonic_mean_pass_actions": ("PDI", "Pass Danger Index, beschreibt wie viel Gefahr von einer Mannschaft durch Passspiel in gefährlichen Zonen ausgeht", "float"),
 




    "opponent_defensive_distance_ppda": ("Defensivlinien-Höhe Gegner (PPDA)", "Durchschnittliche Distanz vom eigenen Tor, aus der der Gegner seine Defensivaktionen im Rahmen von PPDA ausführt", "float"),
    "opponent_np_xgd": ("xG Differenz Gegner oE", "xG Differenz des Gegners, ohne Elfmeter", "float"),
    "defensive_distance_ppda": (None, None, None),
    "result": ("Ergebnis", None, "string"),
    "match_date": ("Datum", None, "date"),
    "opponent_shot_assists": (None, None, None),
    "opponent_throughballs": (None, None, None),
    "opponent_passes_into_f3": (None, None, None),
    "opponent_passes_into_box": (None, None, None),
    "opponent_cutbacks": (None, None, None),
    "opponent_harmonic_mean_pass_actions": (None, None, None),
    "team_name": ("Mannschaft", None, "string"),
    "opposition_name": ("Gegner", None, "string"),
    "competition_name": ("Liga", None, "string"),
    "np_shots": ("Schüsse oE", "oE: ohne Elfmeter", "int"),
    "np_xg": ("xG oE", "oE: ohne Elfmeter", "float"),
    "np_shot_distance": ("Schussdistanz oE", "Durchschnittliche Schussdistanz, oE: ohne ELfmeter", "float"),
    "opponent_np_shots": ("Schüsse Gegner oE", "oE: ohne Elfmeter", "int"),
    "opponent_np_xg": ("xG Gegner oE", "oE: ohne Elfmeter", "float"),
    "xgd": ("xG Differenz", None, "float"),
    "opponent_np_shot_distance": ("Schussdistanz Gegner oE", "Durchschnittliche Schussdistanz des Gegners, oE: ohne Elfmeter", "float"),
    "opponent_sp_shot_distance": ("Schussdistanu Gegner St", "Durchschnittliche Schussdistanz des Gegners, St: Standards", "float"),
    "throw_ins": ("Einfwürfe", None, "int"),
    "ball_in_play_time": ("Effektive Spielzeit", "Tatsächliche Zeit, die der Ball während eines Spiels im Feld ist (Minuten)", "float"),
    "own_goals": ("Eigentore", None, "int"),  #. + auf geschossene Tore pro spieltag beim gegner
    "opponent_own_goals": ("Eigentore Gegner", None, "int"), # +1 geschosseene Tore pro spieltag 
    "opponent_throw_ins": ("Einwürfe Gegner", None, "int"),
    "opponent_total_dribbles": ("Gesamtanzahl Dribblings Gegner", "Dribblings: Ein Versuch eines Spielers, einen Gegenspieler zu überwinden. Summe aus erfolgreichen und misslungenen Dribblings des Gegners", "int"),
    "opponent_yellow_cards": ("Gelbe Karten Gegner", None, "int"),
    "opponent_passes": ("Pässe Gegner", "Anzahl der vom Gegner gespielten (versuchten) Pässe", "int"),
    "passes": ("Pässe", "Anzahl der gespielten (versuchten) Pässe", "int"),
    "opponent_op_passes": ("Pässe Gegner Sp", "Anzahl der vom Gegner gespielten Pässe, Sp: aus dem Spiel", "int"),
    "opponent_ball_in_play_time": ("Effektive Spielzeit Gegner", "Tatsächliche Zeit (in Minuten), die der Ball während des Spiels beim Gegner im Feld war", "float"),
    "opponent_second_yellow_cards": ("Zweite Gelbe Karten Gegner", "Anzahl der zweiten Gelben Karten gegen den Gegner", "int"),
    "opponent_red_cards": ("Rote Karten Gegner", "Anzahl der Roten Karten gegen den Gegner", "int"),
    "gd": ("Tordifferenz", None, "int"),
    

    
}

COMPETITION_LABELS = {
    "Eredivisie": "Eredivisie, NLD 1",
    "Ligue 2": "Ligue 2, FR 2",
    "Ekstraklasa": "Ekstraklasa, POL 1",
    "La Liga 2": "La Liga 2, ESP 2",
    "Jupiler Pro League": "Jupiler Pro League, BEL 1",
    "Bundesliga": "Bundesliga, AUT 1",
    "Eerste Divisie": "Erste Divisie, NLD 2",
    "Allsvenskan": "Allsvenskan, SWE 1",
    "Czech Liga": "Czech Liga, CZE 1",
    "Superliga": "Superliga, DNK 1",
    "1. HNL": "1. HNL, HVR 1",
    "Super League": "Super League, CHE 1",
    "Eliteserien": "Eliteserien, NOR 1",
    "A-League": "A-League, AUS 1",
    "J1 League": "J1 League, JNP 1",
    "K League 1": "K League 1, KOR 1",
    "Super Liga": "Super Liga, SVK 1",
    "Championnat National": "Championnat National, FR 3",
    "Challenge League": "Challenge League, CHE 2",
    "PSL": "PSL, ZAF 1",
    "1. Division": "1. Division, DNK 2",
    "Segunda Liga": "Segunda Liga, PRT 2",
    "Challenger Pro League": "Challenger Pro League, BEL 2",
    "ligat ha'al": "Ligat Ha'Al, ISR 1",
    "2. Liga": "2. Liga, AUT 2",
    "1. SNL": "1. SNL, SVN 1"
}





PLAYER_CATEGORIES = {

# Infos Player
"player_infos": ["player_name", "team_name", "competition_name", "season_name", "birth_date", "weight", "height",
                 "primary_position", "secondary_position", "minutes", "90s_played", "appearances", "starting_appearances"
                  ], 






}

PLAYER_NICHT = {
    "player_id": ("Spieler-ID", "Eindeutige ID des Spielers", "int"),
    "team_id": ("Team-ID", "Eindeutige ID der Mannschaft", "int"),
    "competition_id": ("Liga-ID", "Eindeutige ID des Wettbewerbs", "int"),
    "season_id": ("Saison-ID", "Eindeutige ID der Saison", "int"),
    "player_female": ("Frauen-Team", "True, wenn die Spielerin in einem Frauen-Team spielt", "bool"),
    "most_recent_match": ("Letztes Spiel (ID)", "ID des jüngsten Spiels des Spielers", "int"),


}
