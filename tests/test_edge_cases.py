"""Randfälle der Kernroutinen und der Auswertung: kleinste Netze, Grenzen der Regler, jede Art von Prüffehler an verfälschten Analysen (DEMO-PLAYBOOK §12)."""

import dataclasses

import pytest

import geb_algorithm as A
import geb_constants as C
import geb_evaluation as ev

from conftest import FixedRandom, graph, path


def test_quality_by_hand_on_a_path_with_islands():
    g = path(8)
    q = ev.quality(g, (0, 0, 1, 0, 0, 1, 1, 1), 2, 4)
    assert q == ev.Quality(cut=3, sizes=(4, 4), ratio=1.0, split_parts=2, island_nodes=3, balanced=True, connected=False) and not q.ok
    q2 = ev.quality(g, (0, 0, 0, 1, 1, 1, 1, 1), 2, 4)
    assert q2.cut == 1 and q2.sizes == (3, 5) and q2.ratio == 1.25 and not q2.balanced and q2.connected and not q2.ok
    q3 = ev.quality(g, (0, 0, 0, 0, 1, 1, 1, 1), 2, 4)
    assert q3.ok and q3.split_parts == 0 and q3.island_nodes == 0


def test_the_smallest_networks_and_the_largest_k():
    g = path(4)
    assert A.recursive_bisection(g, 2, FixedRandom()) == (0, 0, 1, 1)
    assert A.recursive_bisection(g, 4, FixedRandom()) == (0, 1, 2, 3)
    assert A.seeds(g, 4, FixedRandom()) == (3, 0, 1, 2) and A.grow(g, 4, FixedRandom()) == (1, 2, 3, 0)         # jeder Standort ist sein eigenes Gebiet
    assert A.attach_islands(g, (0, 1, 2, 3), 4) == ((0, 1, 2, 3), 0)
    assert A.rebalance(g, (0, 0, 1, 1), 2, 2) == ((0, 0, 1, 1), True)
    assert A.polish(g, (0, 0, 1, 1), 2, 2) == (0, 0, 1, 1)


def test_a_star_cannot_be_balanced_without_splitting_the_centre_area():
    g = graph(5, [(0, 1), (0, 2), (0, 3), (0, 4)])
    label, ok = A.rebalance(g, (0, 0, 0, 0, 1), 2, 3)
    assert not ok and label == (0, 0, 0, 0, 1)                                      # nur Blätter dürften wechseln, aber sie haben keine Leitung zu Gebiet 1


def test_every_kind_at_the_smallest_and_largest_size_validates():
    for kind in C.KINDS:
        for n, k, delta in ((C.N_MIN, 8, 5), (C.N_MIN, 2, 20), (C.N_MAX, 8, 10)):
            a = ev.analyse(ev.Settings(kind=kind, n=n, k=k, delta=delta))
            assert ev.validate(a) == [], (kind, n, k, delta)
            assert all(q.connected for key, q in a.quality.items() if key != "rb"), (kind, n, k, delta)


def test_the_analysis_is_deterministic_and_the_seed_changes_the_network():
    s = ev.Settings(kind="geometric", n=120, seed=5)
    a1, a2 = ev.analyse(s), ev.analyse(s)
    assert a1.labels == a2.labels and a1.quality == a2.quality and a1.seeds == a2.seeds and a1.moved == a2.moved
    assert ev.analyse(dataclasses.replace(s, seed=6)).labels["rb"] != a1.labels["rb"]
    assert ev.run_rng(5).random() != ev.run_rng(6).random() and ev.run_rng(5, 0).random() != ev.run_rng(5, 1).random()


def test_the_analysis_properties():
    a = ev.analyse(ev.Settings(kind="verbund", n=100, deg=5.0, links=2, seed=3, k=4, delta=10))
    assert a.n == a.graph.n == 100 and a.m == a.inst.m and a.limit == A.part_limit(100, 4, 10) == 28 and len(a.seeds) == 4
    assert set(a.labels) == set(a.quality) == {key for key, _name in ev.STAGES} and set(ev.STAGE_LONG) == set(a.labels)


def test_the_grid_is_rounded_to_a_rectangle():
    a = ev.analyse(ev.Settings(kind="grid", n=37, k=2, delta=10))
    assert a.n == 36 and ev.validate(a) == []


def test_validate_reports_every_kind_of_problem_on_tampered_analyses():
    a = ev.analyse(ev.Settings(kind="geometric", n=120, seed=7, k=4, delta=10))
    assert ev.validate(a) == []

    def with_label(key, label):
        return dataclasses.replace(a, labels={**a.labels, key: label})
    out_of_range = tuple(5 if v == 0 else x for v, x in enumerate(a.labels["rb"]))
    assert any("ohne Gebiet" in p for p in ev.validate(with_label("rb", out_of_range)))
    empty = tuple(0 if x == 3 else x for x in a.labels["rb"])
    assert any("leeres Gebiet" in p for p in ev.validate(with_label("rb", empty)))
    other = tuple(x if v else (x + 1) % 4 for v, x in enumerate(a.labels["growbal"]))
    assert any("Nachzählung" in p for p in ev.validate(with_label("growbal", other)))
    wrong_cut = dataclasses.replace(a, quality={**a.quality, "rep": dataclasses.replace(a.quality["rep"], cut=a.quality["rep"].cut + 1)})
    assert any("Nachzählung" in p for p in ev.validate(wrong_cut))
    split = dataclasses.replace(a, labels={**a.labels, "bal": a.labels["rb"]}, quality={**a.quality, "bal": a.quality["rb"]})
    assert any("unzusammenhängendes" in p for p in ev.validate(split)) if a.quality["rb"].split_parts else True
    wrong_split = dataclasses.replace(a, quality={**a.quality, "rb": dataclasses.replace(a.quality["rb"], split_parts=a.quality["rb"].split_parts + 1)})
    assert any("zerfallenen" in p for p in ev.validate(wrong_split))
    wrong_flag = dataclasses.replace(a, bal_ok=not a.bal_ok)
    assert any("Grenze anders" in p for p in ev.validate(wrong_flag))
    wrong_flag2 = dataclasses.replace(a, growbal_ok=not a.growbal_ok)
    assert any("Grenze anders" in p for p in ev.validate(wrong_flag2))


def test_part_limit_never_exceeds_n_for_the_allowed_choices():
    for n in (C.N_MIN, 100, C.N_MAX):
        for k in C.K_CHOICES:
            for delta in C.DELTA_CHOICES:
                assert A.part_limit(n, k, delta) >= -(-n // k) and A.part_limit(n, k, delta) < n


def test_unknown_stage_names_are_not_used():
    assert [key for key, _n in ev.STAGES] == ["rb", "rep", "bal", "grow", "growbal"]
    with pytest.raises(KeyError):
        ev.STAGE_LONG["nope"]


def test_the_exact_enumeration_includes_the_split_with_a_single_node():
    import geb_experiments as ex
    assert ex.exact_best(4, [(0, 1), (1, 2), (1, 3), (2, 3)], 100) == (1, 1)         # bei weiter Grenze darf Standort 0 allein ein Gebiet sein (Schnitt 1)
    assert ex.exact_best(4, [(0, 1), (1, 2), (1, 3), (2, 3)], 10) == (1, 1)          # auch bei 10 %: Grenze ⌈1,1 · 2⌉ = 3 erlaubt eins gegen drei
    assert ex.exact_best(4, [(0, 1), (1, 2), (1, 3), (2, 3)], 0) == (2, 2)           # ohne Spielraum genau zwei gegen zwei: Schnitt 2
