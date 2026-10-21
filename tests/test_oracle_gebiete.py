"""Orakel-Test gebietsaufteilung-demo: Komponenten, Inseln, Schnitt, Umhängen, Ausgleichen, Bezirkswachstum und die exakte Aufzählung gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12).

Unabhängig: `networkx` (Zusammenhangskomponenten, Teilgraphen, `cut_size`, `is_connected`) und die Aufzählung aller Zuordnungen mit networkx-Prüfung bei höchstens 11 Standorten. Feste Netze (Seeds)."""

import itertools
import math
import random

import pytest

import geb_algorithm as A
import geb_evaluation as ev
import geb_experiments as ex
import geb_scenario as S

nx = pytest.importorskip("networkx")

KINDS = ("geometric", "grid", "ring", "scalefree", "random", "verbund")


def _nets(count=18, base=8000, n=60):
    for k in range(count):
        inst = S.make_instance(KINDS[k % 6], n + 4 * (k % 3), 4.0, 1, base + k)
        yield inst, A.from_pairs(inst.n, inst.pairs)


def _nx(inst):
    h = nx.Graph()
    h.add_nodes_from(range(inst.n))
    h.add_edges_from(inst.pairs)
    return h


def _label(inst, g, k, seed):
    return A.recursive_bisection(g, k, ev.run_rng(seed))


def test_components_equal_the_networkx_components_on_random_subsets():
    rng = random.Random(3)
    for inst, g in _nets():
        h = _nx(inst)
        for _ in range(4):
            subset = [v for v in range(g.n) if rng.random() < 0.5]
            expected = sorted((sorted(c) for c in nx.connected_components(h.subgraph(subset))), key=lambda c: (-len(c), c[0]))
            assert A.components(g, subset) == expected


def test_cut_value_equals_networkx_cut_sizes():
    rng = random.Random(4)
    for inst, g in _nets():
        h = _nx(inst)
        label = tuple(rng.randrange(4) for _ in range(g.n))
        total = sum(nx.cut_size(h, [v for v in range(g.n) if label[v] == i]) for i in range(4))
        assert A.cut_value(g, label) * 2 == total


def test_islands_are_the_nodes_outside_the_largest_networkx_component_of_each_area():
    for k, (inst, g) in enumerate(_nets(12)):
        h = _nx(inst)
        label = _label(inst, g, 4, 8000 + k)
        expected = []
        for i in range(4):
            comps = sorted((sorted(c) for c in nx.connected_components(h.subgraph([v for v in range(g.n) if label[v] == i]))), key=lambda c: (-len(c), c[0]))
            for c in comps[1:]:
                expected += c
        assert A.islands(g, label, 4) == sorted(expected)


def test_attach_islands_leaves_every_area_connected_and_moves_nothing_without_islands():
    for k, (inst, g) in enumerate(_nets(18, 8100)):
        h = _nx(inst)
        label = _label(inst, g, 4, 8100 + k)
        before = set(A.islands(g, label, 4))
        new, moved = A.attach_islands(g, label, 4)
        assert all(nx.is_connected(h.subgraph([v for v in range(g.n) if new[v] == i])) for i in range(4) if any(x == i for x in new))
        changed = sum(1 for x, y in zip(label, new) if x != y)
        assert changed <= moved and (moved == 0) == (not before) and (before or new == label)       # ohne Inseln bleibt alles, mit Inseln wird mindestens eine bewegt


def test_rebalance_and_polish_keep_every_area_connected_nonempty_and_within_the_limit():
    for k, (inst, g) in enumerate(_nets(18, 8200)):
        h = _nx(inst)
        for areas in (2, 4):
            lim = A.part_limit(g.n, areas, 10)
            rep, _moved = A.attach_islands(g, _label(inst, g, areas, 8200 + k), areas)
            bal, ok = A.rebalance(g, rep, areas, lim)
            pol = A.polish(g, bal, areas, lim)
            for label in (bal, pol):
                assert all(nx.is_connected(h.subgraph([v for v in range(g.n) if label[v] == i])) for i in range(areas))
            assert ok == (max(A.sizes(bal, areas)) <= lim)
            assert A.cut_value(g, pol) <= A.cut_value(g, bal) and max(A.sizes(pol, areas)) <= max(lim, max(A.sizes(bal, areas)))


def test_grow_gives_connected_areas_for_every_network_type_and_k():
    for k, (inst, g) in enumerate(_nets(18, 8300)):
        h = _nx(inst)
        for areas in (2, 4, 8):
            label = A.grow(g, areas, ev.run_rng(8300 + k, 1))
            assert min(label) == 0 and max(label) == areas - 1 and len(set(label)) == areas
            assert all(nx.is_connected(h.subgraph([v for v in range(g.n) if label[v] == i])) for i in range(areas))


def _brute(inst, delta):
    n = inst.n
    h = _nx(inst)
    lim = A.part_limit(n, 2, delta)
    best_any = best_conn = None
    for mask in range(1, 1 << (n - 1)):
        side = [v for v in range(n) if (mask >> v) & 1]
        other = [v for v in range(n) if not (mask >> v) & 1]
        if len(side) > lim or len(other) > lim:
            continue
        cut = nx.cut_size(h, side)
        best_any = cut if best_any is None else min(best_any, cut)
        if (best_conn is None or cut < best_conn) and nx.is_connected(h.subgraph(side)) and nx.is_connected(h.subgraph(other)):
            best_conn = cut
    return best_any, best_conn


def test_the_exact_enumeration_equals_a_networkx_enumeration_on_small_networks():
    for k in range(9):
        inst = S.make_instance(("geometric", "random", "ring", "verbund", "scalefree")[k % 5], 10 + k % 2, 3.0, 1, 8400 + k)
        for delta in (10, 20):
            assert ex.exact_best(inst.n, inst.pairs, delta) == _brute(inst, delta), (inst.kind, inst.n, delta)


def test_the_exact_optimum_is_never_beaten_by_the_heuristics_and_connectivity_costs_at_most_the_difference():
    for k in range(10):
        inst = S.make_instance(("geometric", "verbund", "random")[k % 3], 12, 3.0, 1, 8500 + k)
        g = A.from_pairs(inst.n, inst.pairs)
        any_, conn = ex.exact_best(inst.n, inst.pairs, 20)
        lim = A.part_limit(g.n, 2, 20)
        assert conn is not None and conn >= any_
        grown, ok = A.rebalance(g, A.grow(g, 2, random.Random(k)), 2, lim)
        if ok:
            assert A.cut_value(g, grown) >= conn
        rb = A.recursive_bisection(g, 2, random.Random(k))
        if max(A.sizes(rb, 2)) <= lim:
            assert A.cut_value(g, rb) >= any_


def test_part_limit_equals_the_exact_ceiling_in_fractions():
    from fractions import Fraction
    for n in (24, 100, 255, 256, 300):
        for k in (2, 4, 8):
            for delta in (0, 5, 10, 20):
                assert A.part_limit(n, k, delta) == math.ceil(Fraction(100 + delta, 100) * Fraction(n, k))


def test_a_bisection_result_is_a_partition_into_k_areas_of_roughly_equal_size():
    for k, (inst, g) in enumerate(itertools.islice(_nets(), 6)):
        label = _label(inst, g, 4, 8000 + k)
        sizes = A.sizes(label, 4)
        assert sum(sizes) == g.n and min(sizes) >= 1 and max(sizes) <= math.ceil(1.03 * 1.03 * g.n / 4) + 1
