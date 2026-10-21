"""Zweige der Hauptansicht (Nullspalte-Lehre): Jeder Weg, den die App zeigt, kommt in mindestens einem Preset oder einem festen Netz vor.

Ein Preset, das seine Beschreibung nicht einlöst, fällt in `test_claims.py` auf. Hier: die Zweige und dass jede Abbildung für jeden Zweig gebaut werden kann (kein Fehler, nichtleere Daten)."""

import geb_algorithm as A
import geb_constants as C
import geb_evaluation as ev
import geb_visualization as V

from conftest import cached


def _all():
    return {name: ev.analyse(ev.Settings(**p)) for name, p in C.PRESETS.items()}


def test_every_preset_validates_clean():
    for name, a in _all().items():
        assert ev.validate(a) == [], name


def test_every_branch_of_the_result_is_reached():
    analyses = list(_all().values())
    assert any(a.quality["rb"].split_parts == 0 for a in analyses) and any(a.quality["rb"].split_parts > 0 for a in analyses)
    assert any(a.quality["bal"].ok for a in analyses) and any(not a.quality["bal"].ok for a in analyses)
    assert any(a.quality["growbal"].ok for a in analyses) and any(not a.quality["growbal"].ok for a in analyses)
    assert {a.settings.k for a in analyses} == set(C.K_CHOICES) and {a.settings.delta for a in analyses} == {10, 20}
    assert any(a.moved > 0 for a in analyses) and any(a.moved == 0 for a in analyses)


def test_every_net_kind_but_the_ring_is_used_by_a_preset():
    assert {p["kind"] for p in C.PRESETS.values()} == set(C.KINDS) - {"ring", "scalefree"}                  # Ring und skalenfreies Netz kommen in den Experimenten und in den Orakel-Tests vor


def test_the_figures_build_for_every_preset_and_every_stage():
    keys = [key for key, _name in ev.STAGES]
    names = [ev.STAGE_LONG[key] for key in keys]
    for name, a in _all().items():
        assert V.build_cuts(a, keys, names).data and V.build_ratios(a, keys, names).data, name
        for key in keys:
            fig = V.build_map(a.inst, a.graph, a.labels[key], a.settings.k, seeds=a.seeds if key.startswith("grow") else ())
            assert fig.data, (name, key)
            marker_traces = [t for t in fig.data if t.mode == "markers"]
            assert sum(len(t.x) for t in marker_traces if t.name and not t.name.startswith(("Inseln", "Keime"))) + len(A.islands(a.graph, a.labels[key], a.settings.k)) == a.n, (name, key)


def test_the_experiment_figures_build_from_the_cached_rows():
    assert V.build_exact(cached("exact_rows")).data and V.build_split(cached("split_rows")).data and V.build_repair(cached("repair_rows")).data and V.build_grow(cached("grow_rows")).data
