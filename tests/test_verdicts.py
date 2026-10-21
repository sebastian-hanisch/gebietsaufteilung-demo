"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds; so prüft der Test Grenzen und jede genannte Zahl direkt."""

import geb_constants as C
import geb_evaluation as ev


def test_formats():
    assert ev._i(1234567) == "1.234.567" and ev._dec(3.0) == "3" and ev._dec(1234.5) == "1.234,5" and ev._dec(0.75) == "0,8" and ev._dec(2.25, 2) == "2,25"
    assert ev._of(3, 1200) == "3 von 1.200" and ev._gebiete(1) == "1 Gebiet" and ev._gebiete(6) == "6 Gebiete"


def test_verdict_exact_counts_nets_and_extra_edges():
    rows = [{"n": 16, "nets": 3, "differ": 1, "sum_opt": 10, "sum_conn": 12}, {"n": 16, "nets": 3, "differ": 0, "sum_opt": 5, "sum_conn": 5}]
    assert ev.verdict_exact(rows) == ("info", "Bei k = 2 und 16 Standorten (je Netztyp 3 Netze, 6 insgesamt; alle ausgewogenen Zweiteilungen aufgezählt) kostet der Zusammenhang beider Hälften "
                                              "in 1 von 6 Netzen etwas: insgesamt 2 Leitungen mehr (15 gegen 17).")


def test_verdict_split_lists_every_k_and_the_largest_k_per_type():
    rows = [{"label": "A", "k": 2, "nets": 4, "nets_split": 1, "parts": 8, "parts_split": 1}, {"label": "B", "k": 2, "nets": 4, "nets_split": 0, "parts": 8, "parts_split": 0},
            {"label": "A", "k": 4, "nets": 4, "nets_split": 4, "parts": 16, "parts_split": 6}, {"label": "B", "k": 4, "nets": 4, "nets_split": 2, "parts": 16, "parts_split": 2}]
    assert ev.verdict_split(rows) == ("info", "Netze mit mindestens einem zerfallenen Gebiet der rekursiven Bisektion: k = 2: 1 von 8; k = 4: 6 von 8. Bei k = 4 je Netztyp: A: 4 von 4; B: 2 von 4. "
                                              "Zerfallene Gebiete bei k = 4 insgesamt: 8 von 32.")


def test_verdict_repair_gives_the_three_mean_ratios_and_the_counts():
    rows = [{"nets": 4, "nets_split": 4, "ok_rep": 0, "ok_bal": 2, "sum_ratio_rb": 4.0, "sum_ratio_rep": 6.0, "sum_ratio_bal": 4.8},
            {"nets": 4, "nets_split": 1, "ok_rep": 3, "ok_bal": 4, "sum_ratio_rb": 4.4, "sum_ratio_rep": 4.8, "sum_ratio_bal": 4.4}]
    assert ev.verdict_repair(rows) == ("info", "Von 8 Netzen (Netztypen mal k = 4 und 8 mal Netze) hatten 5 ein zerfallenes Gebiet. Das größte Gebiet ist im Mittel das 1,05-Fache des Ideals (Bisektion), "
                                               "nach dem Umhängen der Inseln das 1,35-Fache, nach dem Ausgleich das 1,15-Fache. Zusammenhängend und innerhalb der Grenze sind nach dem Umhängen 3 von 8 Netze, nach dem Ausgleich 6 von 8.")


def test_verdict_grow_counts_successes_and_compares_the_cuts_on_common_nets():
    rows = [{"nets": 4, "ok_bal": 2, "ok_growbal": 4, "n_both": 2, "sum_bal_both": 30, "sum_grow_both": 16}, {"nets": 4, "ok_bal": 4, "ok_growbal": 3, "n_both": 3, "sum_bal_both": 100, "sum_grow_both": 140}]
    assert ev.verdict_grow(rows) == ("info", "Bezirkswachstum mit Ausgleich erfüllt Grenze und Zusammenhang in 7 von 8 Netzen, Bisektion mit Reparatur in 6 von 8. "
                                             "Auf den 5 Netzen, in denen beide es schaffen, ist der Schnitt 130 (Reparatur) gegen 156 (Bezirkswachstum).")


def test_verdict_checks_reports_deviations():
    rows = [{"nets": 4, "n": 256, "wrong": 0}, {"nets": 4, "n": 256, "wrong": 0}]
    kind, text = ev.verdict_checks(rows)
    assert kind == "info" and text.startswith("Alle 8 Analysen (2 Netztyp-k-Paare mit je 4 festen Netzen mit 256 Standorten) bestehen die Prüfung:") and text.endswith("Abweichungen: 0.")
    rows[1]["wrong"] = 2
    assert ev.verdict_checks(rows) == ("warning", "Bei 2 von 8 Analysen weicht die Prüfung ab.")


def _a(**over):
    return ev.analyse(ev.Settings(**over))


def test_verdict_run_when_a_bisection_area_splits_and_the_repair_cannot_balance():
    kind, text = ev.verdict_run(ev.analyse(ev.Settings(**C.PRESETS["Kartennetz: Bisektion lässt Inseln"])))
    assert kind == "warning"
    assert text == ("**Bei 256 Standorten sind 2 der 4 Gebiete der Bisektion nicht zusammenhängend** (72 Standorte liegen in Inseln; Schnitt 17, größtes Gebiet das 1,06-Fache des Ideals). "
                    "Das Umhängen der Inseln gibt zusammenhängende Gebiete mit Schnitt 7, aber das größte Gebiet ist dann das 1,81-Fache des Ideals (außerhalb der Grenze von 71 Standorten). "
                    "Der zusammenhangswahrende Ausgleich **erreicht die Grenze nicht** (Schnitt 20, größtes Gebiet das 1,58-Fache). "
                    "Das Bezirkswachstum ist von Anfang an zusammenhängend, mit Schnitt 15 und größtem Gebiet das 1,31-Fache; ausgeglichen: Schnitt 22, Grenze nicht erreicht.")


def test_verdict_run_when_the_balancing_reaches_the_limit():
    kind, text = ev.verdict_run(ev.analyse(ev.Settings(**C.PRESETS["Verbundnetz: Reparatur gelingt"])))
    assert kind == "info" and "Der zusammenhangswahrende Ausgleich erreicht die Grenze: Schnitt 105, größtes Gebiet das 1,11-Fache." in text and text.endswith("ausgeglichen: Schnitt 114, Grenze erreicht.")


def test_verdict_run_when_nothing_splits():
    kind, text = ev.verdict_run(ev.analyse(ev.Settings(**C.PRESETS["Gitter: nichts zu reparieren"])))
    assert kind == "info" and text.startswith("**Bei 256 Standorten und 4 Gebieten ist jedes Gebiet der Bisektion zusammenhängend** (Schnitt 32, größtes Gebiet das 1-Fache des Ideals): Hier fehlt nichts zu reparieren.")


def test_verdict_run_when_the_repair_stays_within_the_limit():
    kind, text = ev.verdict_run(_a(kind="ring", n=256, deg=4.0, links=1, seed=100000, k=4, delta=10))
    assert kind == "info" and "(innerhalb der Grenze von 71 Standorten). Der Ausgleich ist nicht nötig; verbessert ergibt sich Schnitt 46." in text
