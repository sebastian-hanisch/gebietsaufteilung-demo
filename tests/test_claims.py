"""Jede Zahl im README (Abschnitt „Befunde“) wird hier über dieselben Experimentfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Zähler und Summen über feste Netze (je Netztyp vier Netze mit 256 Standorten, bei der Aufzählung sechs Netze mit 16 Standorten), nie ein einzelner Zufalls-Seed. Netztypen in der Reihenfolge Kartennetz, Gitter,
Ring mit Abkürzungen, skalenfreies Netz, Zufallsnetz (Grad 4), Verbundnetz (Grad 5); Verbundnetze mit einer Leitung zwischen je zwei Regionen. Die Zahlen der Vormessung im Einzelplan stammen aus Wegwerfskripten
mit anderen Verfahren (mehrstufige Halbierung); maßgeblich sind diese hier."""

import geb_constants as C
import geb_evaluation as ev

from conftest import cached

LABELS = ["Kartennetz", "Gitter", "Ring mit Abkürzungen", "Skalenfreies Netz", "Zufallsnetz, Grad 4", "Verbundnetz, Grad 5"]


def _k(rows, k):
    return [r for r in rows if r["k"] == k]


def test_every_check_holds_on_every_analysis():
    rows = cached("checks_rows")
    assert len(rows) == 18 and all(r["nets"] == 4 and r["n"] == 256 for r in rows) and sum(r["nets"] for r in rows) == 72 and sum(r["wrong"] for r in rows) == 0
    assert [r["label"] for r in _k(rows, 4)] == LABELS


def test_connectivity_costs_something_in_four_of_36_networks_at_k_equals_two():
    rows = cached("exact_rows")
    assert [r["label"] for r in rows] == LABELS and all(r["n"] == 16 and r["nets"] == 6 for r in rows)
    assert [r["differ"] for r in rows] == [2, 0, 0, 1, 1, 0] and sum(r["differ"] for r in rows) == 4
    assert [r["sum_opt"] for r in rows] == [19, 24, 35, 48, 48, 30] and [r["sum_conn"] for r in rows] == [23, 24, 35, 49, 49, 30]
    assert sum(r["sum_opt"] for r in rows) == 204 and sum(r["sum_conn"] for r in rows) == 210


def test_the_share_of_networks_with_a_split_area_grows_with_k():
    rows = cached("split_rows")
    assert [r["nets_split"] for r in _k(rows, 2)] == [3, 0, 0, 0, 1, 4] and [r["nets_split"] for r in _k(rows, 4)] == [4, 1, 2, 2, 1, 4] and [r["nets_split"] for r in _k(rows, 8)] == [4, 2, 4, 4, 2, 4]
    assert [sum(r["nets_split"] for r in _k(rows, k)) for k in (2, 4, 8)] == [8, 14, 20]
    assert [sum(r["parts_split"] for r in _k(rows, k)) for k in (2, 4, 8)] == [12, 27, 56] and [sum(r["parts"] for r in _k(rows, k)) for k in (2, 4, 8)] == [48, 96, 192]
    assert [r["parts_split"] for r in _k(rows, 4)] == [13, 1, 2, 2, 1, 8] and [r["parts_split"] for r in _k(rows, 8)] == [23, 4, 8, 7, 4, 10]


def test_the_islands_are_large_only_on_map_and_union_networks():
    rows = cached("split_rows")
    assert [r["island_nodes"] for r in _k(rows, 2)] == [295, 0, 0, 0, 3, 165] and [r["island_nodes"] for r in _k(rows, 4)] == [332, 24, 35, 4, 3, 126] and [r["island_nodes"] for r in _k(rows, 8)] == [255, 32, 57, 30, 22, 93]
    assert [r["sum_cut"] for r in _k(rows, 4)] == [71, 144, 208, 664, 602, 414]


def test_the_repair_trades_the_cut_for_the_balance():
    rows = cached("repair_rows")
    assert all(r["nets"] == 4 and r["n"] == 256 for r in rows) and [r["k"] for r in rows] == [4] * 6 + [8] * 6
    four, eight = _k(rows, 4), _k(rows, 8)
    assert [r["sum_cut_rb"] for r in four] == [71, 144, 208, 664, 602, 414] and [r["sum_cut_rep"] for r in four] == [23, 136, 199, 661, 601, 230] and [r["sum_cut_bal"] for r in four] == [65, 137, 202, 661, 599, 374]
    assert [r["sum_cut_rb"] for r in eight] == [106, 288, 282, 854, 779, 805] and [r["sum_cut_rep"] for r in eight] == [54, 269, 259, 834, 770, 700] and [r["sum_cut_bal"] for r in eight] == [91, 270, 266, 834, 768, 709]
    assert [round(r["sum_ratio_rb"] / 4, 2) for r in four[:1] + four[5:]] == [1.04, 1.06] and [round(r["sum_ratio_rep"] / 4, 2) for r in four[:1] + four[5:]] == [1.59, 1.33] and [round(r["sum_ratio_bal"] / 4, 2) for r in four[:1] + four[5:]] == [1.16, 1.15]
    assert [round(r["sum_ratio_rb"] / 4, 2) for r in eight[:1] + eight[5:]] == [1.09, 1.09] and [round(r["sum_ratio_rep"] / 4, 2) for r in eight[:1] + eight[5:]] == [1.8, 1.4] and [round(r["sum_ratio_bal"] / 4, 2) for r in eight[:1] + eight[5:]] == [1.52, 1.25]


def test_the_repair_often_reaches_the_limit_but_not_on_map_and_union_networks():
    rows = cached("repair_rows")
    four, eight = _k(rows, 4), _k(rows, 8)
    assert [r["ok_rep"] for r in four] == [0, 3, 3, 4, 4, 0] and [r["ok_rep"] for r in eight] == [0, 2, 0, 1, 2, 0]
    assert [r["ok_bal"] for r in four] == [2, 4, 4, 4, 4, 2] and [r["ok_bal"] for r in eight] == [1, 4, 4, 4, 4, 2]
    assert sum(r["nets"] for r in rows) == 48 and sum(r["nets_split"] for r in rows) == 34 and sum(r["ok_rep"] for r in rows) == 19 and sum(r["ok_bal"] for r in rows) == 39
    mean = lambda key: sum(r[f"sum_ratio_{key}"] for r in rows) / 48   # noqa: E731
    assert (round(mean("rb"), 2), round(mean("rep"), 2), round(mean("bal"), 2)) == (1.06, 1.27, 1.15)


def test_the_district_growth_reaches_the_limit_everywhere_at_k_equals_four_and_wins_on_map_networks():
    rows = cached("grow_rows")
    four, eight = _k(rows, 4), _k(rows, 8)
    assert [r["ok_growbal"] for r in four] == [4, 4, 4, 4, 4, 4] and [r["ok_growbal"] for r in eight] == [4, 2, 4, 4, 4, 1] and [r["ok_bal"] for r in four] == [2, 4, 4, 4, 4, 2] and [r["ok_bal"] for r in eight] == [1, 4, 4, 4, 4, 2]
    assert sum(r["ok_growbal"] for r in rows) == 43 and sum(r["ok_bal"] for r in rows) == 39
    assert [r["n_both"] for r in four] == [2, 4, 4, 4, 4, 2] and [r["n_both"] for r in eight] == [1, 2, 4, 4, 4, 1] and sum(r["n_both"] for r in rows) == 36
    assert [r["sum_bal_both"] for r in four] == [30, 137, 202, 661, 599, 195] and [r["sum_grow_both"] for r in four] == [16, 270, 286, 759, 639, 229]
    assert [r["sum_bal_both"] for r in eight] == [28, 132, 266, 834, 768, 183] and [r["sum_grow_both"] for r in eight] == [18, 249, 336, 888, 845, 208]
    assert sum(r["sum_bal_both"] for r in rows) == 4035 and sum(r["sum_grow_both"] for r in rows) == 4743
    assert [r["sum_cut_grow"] for r in four] == [42, 286, 352, 782, 657, 330] and [r["sum_cut_grow"] for r in eight] == [108, 498, 403, 906, 879, 823]
    assert [round(r["sum_ratio_grow"] / 4, 2) for r in four[:1] + four[5:]] == [1.24, 1.31] and [round(r["sum_ratio_grow"] / 4, 2) for r in eight[:1] + eight[5:]] == [1.16, 1.42]


def _a(name, **over):
    return ev.analyse(ev.Settings(**{**C.PRESETS[name], **over}))


def test_the_preset_descriptions_hold():
    q = _a("Kartennetz: Bisektion lässt Inseln").quality
    assert (q["rb"].cut, q["rb"].split_parts, q["rb"].island_nodes, q["rep"].cut, round(q["rep"].ratio, 2)) == (17, 2, 72, 7, 1.81) and not q["bal"].balanced
    q = _a("Verbundnetz: Reparatur gelingt").quality
    assert (q["rb"].split_parts, q["rb"].island_nodes, round(q["rep"].ratio, 2), q["bal"].cut, q["rb"].cut) == (2, 18, 1.33, 105, 106) and q["bal"].ok
    q = _a("Gitter: nichts zu reparieren").quality
    assert (q["rb"].cut, q["rb"].split_parts, q["grow"].cut) == (32, 0, 65) and q["rb"].ok
    q = _a("Zufallsnetz: kaum Probleme").quality
    assert (q["rb"].cut, q["rb"].split_parts, q["grow"].cut) == (158, 0, 173)
    q = _a("Acht Gebiete im Kartennetz").quality
    assert (q["rb"].split_parts, q["rb"].island_nodes, round(q["bal"].ratio, 2), round(q["growbal"].ratio, 2)) == (7, 80, 1.5, 1.31) and not q["bal"].balanced and not q["growbal"].balanced
    q = _a("Zwei Gebiete: ein Gebiet zerfällt").quality
    assert (q["rb"].cut, q["rb"].split_parts, q["rb"].island_nodes, q["growbal"].cut) == (9, 1, 53, 12) and q["growbal"].ok and not q["bal"].ok
    q = _a("Weite Grenze (20 %): nur Wachstum schafft es").quality
    assert q["growbal"].ok and q["growbal"].cut == 14 and not q["bal"].ok and round(q["bal"].ratio, 2) == 1.48
