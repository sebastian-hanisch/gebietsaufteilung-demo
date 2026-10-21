"""Kern an von Hand gerechneten Mini-Netzen (DEMO-PLAYBOOK §1b): Grenze, Teilnetz, Komponenten, Inseln, Umhängen, Ausgleichen, Verbessern, Keime, Bezirkswachstum, rekursive Bisektion."""

import random

import geb_algorithm as A

from conftest import FixedRandom, graph, path


def test_part_limit_is_the_ceiling_of_the_ideal_plus_the_deviation():
    assert A.part_limit(256, 4, 10) == 71 and A.part_limit(256, 4, 5) == 68 and A.part_limit(256, 4, 20) == 77 and A.part_limit(100, 4, 0) == 25
    assert A.part_limit(14, 2, 10) == 8 and A.part_limit(8, 8, 0) == 1 and A.part_limit(10, 3, 0) == 4


def test_induced_renumbers_in_the_order_of_the_nodes():
    g = graph(6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)])
    sub = A.induced(g, [4, 5, 0])
    assert sub.n == 3 and sub.adj == (((1, 1),), ((0, 1), (2, 1)), ((1, 1),)) and sub.total == 3


def test_components_largest_first_ties_by_the_smallest_node():
    g = graph(8, [(0, 1), (1, 2), (3, 4), (5, 6)])
    assert A.components(g, range(8)) == [[0, 1, 2], [3, 4], [5, 6], [7]]
    assert A.components(g, [4, 3, 6, 5, 0]) == [[3, 4], [5, 6], [0]]
    assert A.components(g, []) == []


def test_members_sizes_and_islands():
    g = path(8)
    label = (0, 0, 1, 0, 0, 1, 1, 1)
    assert A.members(label, 2) == [[0, 1, 3, 4], [2, 5, 6, 7]] and A.sizes(label, 2) == (4, 4)
    assert A.islands(g, label, 2) == [2, 3, 4]                                     # Gebiet 0: {0, 1} und {3, 4} gleich groß, die mit dem kleineren Standort bleibt; Gebiet 1: {5, 6, 7} und {2}
    assert A.islands(g, (0, 0, 0, 0, 1, 1, 1, 1), 2) == []


def test_cut_value_counts_the_edges_between_areas():
    g = graph(4, [(0, 1), (1, 2), (2, 3), (0, 3), (0, 2)])
    assert A.cut_value(g, (0, 0, 1, 1)) == 3 and A.cut_value(g, (0, 0, 0, 0)) == 0 and A.cut_value(g, (0, 1, 2, 3)) == 5


def test_attach_islands_moves_each_island_to_the_neighbour_with_the_most_edges():
    g = path(8)
    label, moved = A.attach_islands(g, (0, 0, 1, 0, 0, 1, 1, 1), 2)
    assert label == (0, 0, 1, 1, 1, 1, 1, 1) and moved == 2                       # die Insel {3, 4} (zwei Leitungen zu Gebiet 1) wechselt; Gebiet 1 ist danach in einem Stück
    again, moved2 = A.attach_islands(g, label, 2)
    assert again == label and moved2 == 0


def test_attach_islands_ties_go_to_the_smaller_area_number():
    g = graph(7, [(0, 1), (1, 2), (3, 4), (5, 6), (2, 3), (4, 5), (6, 0)])
    label, moved = A.attach_islands(g, (0, 0, 1, 2, 2, 1, 1), 3)
    assert A.islands(g, label, 3) == [] and moved >= 1
    one = graph(4, [(0, 1), (2, 3), (1, 2)])
    lab, mv = A.attach_islands(one, (0, 1, 0, 2), 3)                               # Insel {2} hat je eine Leitung zu Gebiet 1 und Gebiet 2: das kleinere gewinnt
    assert lab[2] == 1 and mv == 1


def test_stays_connected_is_false_for_a_cut_node_and_for_the_last_node():
    g = graph(4, [(0, 1), (1, 2), (1, 3)])
    label = (0, 0, 0, 1)
    assert A.stays_connected(g, label, 0) and A.stays_connected(g, label, 2) and not A.stays_connected(g, label, 1)
    assert not A.stays_connected(g, label, 3)                                       # Gebiet 1 hätte danach keinen Standort


def test_rebalance_moves_the_boundary_node_with_the_largest_gain():
    g = path(6)
    label, ok = A.rebalance(g, (0, 0, 0, 0, 0, 1), 2, 4)
    assert ok and label == (0, 0, 0, 0, 1, 1)
    same, ok2 = A.rebalance(g, (0, 0, 0, 1, 1, 1), 2, 3)
    assert ok2 and same == (0, 0, 0, 1, 1, 1)


def test_rebalance_gives_up_when_the_only_move_would_split_the_area():
    g = graph(4, [(0, 1), (1, 2), (1, 3)])
    label, ok = A.rebalance(g, (0, 0, 0, 1), 2, 2)
    assert not ok and label == (0, 0, 0, 1)


def test_rebalance_does_not_overfill_the_target():
    g = path(4)
    label, ok = A.rebalance(g, (0, 0, 0, 1), 2, 2)
    assert ok and label == (0, 0, 1, 1)
    g3 = path(6)
    lab3, ok3 = A.rebalance(g3, (0, 0, 0, 0, 1, 2), 3, 2)                          # Gebiet 2 darf nicht über 2 wachsen; Standort 3 geht zu Gebiet 1 (Leitung 3–4), nicht zu 2
    assert A.sizes(lab3, 3)[0] <= 2 or not ok3


def test_polish_takes_a_move_with_positive_gain_and_keeps_the_limit():
    g = graph(5, [(0, 1), (1, 2), (2, 3), (2, 4), (3, 4)])
    label = A.polish(g, (0, 0, 0, 1, 1), 2, 4)
    assert label == (0, 0, 1, 1, 1) and A.cut_value(g, label) == 1
    assert A.polish(g, (0, 0, 0, 1, 1), 2, 2) == (0, 0, 0, 1, 1)                  # Gebiet 1 dürfte nicht auf drei wachsen
    assert A.polish(g, (0, 0, 1, 1, 1), 2, 4) == (0, 0, 1, 1, 1)


def test_polish_never_empties_or_splits_an_area():
    g = graph(4, [(0, 1), (1, 2), (2, 3), (0, 3)])
    label = A.polish(g, (0, 0, 1, 0), 2, 4)                                         # Standort 2 hätte Gewinn 2, aber Gebiet 1 wäre danach leer
    assert label == (0, 0, 1, 0)


def test_seeds_start_random_and_then_take_the_farthest():
    g = path(8)
    assert A.seeds(g, 3, FixedRandom()) == (7, 0, 3)                                # Standort 3 und 4 sind gleich weit, der kleinere gewinnt
    assert A.seeds(g, 1, FixedRandom()) == (7,)


def test_grow_takes_turns_by_size_and_stays_connected():
    g = path(8)
    assert A.grow(g, 2, FixedRandom()) == (1, 1, 1, 1, 0, 0, 0, 0)
    label = A.grow(g, 4, FixedRandom())
    assert A.sizes(label, 4) == (2, 2, 2, 2) and A.islands(g, label, 4) == []


def test_grow_prefers_the_free_neighbour_with_the_most_edges_and_breaks_ties_by_the_smaller_node():
    g = graph(6, [(5, 4), (5, 3), (4, 3), (3, 2), (2, 1), (1, 0)])
    label = A.grow(g, 2, FixedRandom())                                             # Keime 5 und 0; Gebiet 0 nimmt 3 (Gleichstand mit 4, der kleinere), später 4 (zwei Leitungen) statt 2 (eine)
    assert label == (1, 1, 1, 0, 0, 0)
    tie = graph(5, [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4)])
    lab = A.grow(tie, 2, FixedRandom())                                             # Keime 4 und 0; Gebiet 1 nimmt 1 (Gleichstand 1 und 2), dann ist Gebiet 0 (gleich groß, kleinere Nummer) an der Reihe
    assert lab == (1, 1, 0, 0, 0)


def test_recursive_bisection_halves_a_path_in_order():
    g = path(8)
    assert A.recursive_bisection(g, 2, FixedRandom()) == (0, 0, 0, 0, 1, 1, 1, 1)
    label = A.recursive_bisection(path(16), 4, FixedRandom())
    assert A.sizes(label, 4) == (4, 4, 4, 4) and A.cut_value(path(16), label) == 3 and label[0] == 0 and label[15] == 3


def test_bisect_is_deterministic_and_returns_both_halves():
    g = path(10)
    a1, b1 = A.bisect(g, list(range(10)), random.Random(3))
    a2, b2 = A.bisect(g, list(range(10)), random.Random(3))
    assert (a1, b1) == (a2, b2) and sorted(a1 + b1) == list(range(10)) and a1 and b1
    sub_a, sub_b = A.bisect(g, [2, 3, 4, 5], FixedRandom())
    assert sub_a == [2, 3] and sub_b == [4, 5]


def test_single_level_terminates_when_no_move_is_possible():
    g = path(2)                                                                    # zwei Standorte: jede Halbierung ist 1 + 1, kein Zug möglich
    r = A.single_level(g, 3, FixedRandom(), 10)
    assert r.cut == 1 and r.side == (0, 1) and len(r.starts) == 10 and r.moves == 10
    assert A.recursive_bisection(path(4), 4, FixedRandom()) == (0, 1, 2, 3)


def test_polish_considers_the_last_node_too():
    g = graph(5, [(0, 1), (1, 4), (2, 4), (3, 4), (2, 3)])
    label = A.polish(g, (0, 0, 1, 1, 0), 2, 4)                                     # nur Standort 4 (zwei Leitungen zu Gebiet 1, eine zu Gebiet 0) hat einen Gewinn
    assert label == (0, 0, 1, 1, 1) and A.cut_value(g, label) == 1
