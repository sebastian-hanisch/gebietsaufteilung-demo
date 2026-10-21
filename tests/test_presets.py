"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen; Permalink-Grenzen."""

import geb_constants as C
import geb_evaluation as ev
import geb_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds_and_choices():
    for name, preset in C.PRESETS.items():
        assert preset["kind"] in C.KINDS and preset["k"] in C.K_CHOICES and preset["delta"] in C.DELTA_CHOICES, name
        assert C.N_MIN <= preset["n"] <= C.N_MAX and C.DEG_MIN <= preset["deg"] <= C.DEG_MAX and C.LINKS_MIN <= preset["links"] <= C.LINKS_MAX and 0 <= preset["seed"] <= C.SEED_MAX, name


def test_the_first_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[next(iter(C.PRESETS))]) == ev.Settings()


def test_setting_specs_cover_every_preset_key_and_every_choice_field_is_listed():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert {spec.url_param for spec in P.SETTING_SPECS.values()} == {"kind", "n", "deg", "links", "seed", "k", "delta"}
    assert set(P.CHOICES) == {"kind_select", "k_select", "delta_select"}
    assert P.CHOICES["kind_select"] == C.KINDS and P.CHOICES["k_select"] == C.K_CHOICES and P.CHOICES["delta_select"] == C.DELTA_CHOICES


def test_every_default_is_a_member_of_its_range():
    assert C.DEFAULT_KIND in C.KINDS and C.DEFAULT_K in C.K_CHOICES and C.DEFAULT_DELTA in C.DELTA_CHOICES
    assert C.N_MIN <= C.DEFAULT_N <= C.N_MAX and C.DEG_MIN <= C.DEFAULT_DEG <= C.DEG_MAX and C.LINKS_MIN <= C.DEFAULT_LINKS <= C.LINKS_MAX
    assert C.N_MIN < C.N_MAX and C.DEG_MIN < C.DEG_MAX and C.LINKS_MIN < C.LINKS_MAX and min(C.K_CHOICES) < max(C.K_CHOICES) and min(C.DELTA_CHOICES) < max(C.DELTA_CHOICES)   # kein Regler mit min == max
    assert C.N_MIN >= 3 * max(C.K_CHOICES)                                          # jedes Gebiet hat auch beim kleinsten Netz mindestens drei Standorte


def test_k_choices_are_powers_of_two():
    assert all(k & (k - 1) == 0 for k in C.K_CHOICES)


def test_every_kind_has_a_name_a_help_text_and_a_regler_note():
    assert set(C.KIND_NAMES) == set(C.KIND_HELP) == set(C.KIND_REGLER) == set(C.KINDS)
    assert len(C.COLOR_PARTS) >= max(C.K_CHOICES)


def test_the_experiment_grid_uses_only_known_kinds_and_sizes_inside_the_limits():
    assert [kind for kind, _deg in C.EX_KINDS] == list(C.KINDS)
    assert C.N_MIN <= C.EX_N <= C.N_MAX and int(C.EX_N ** 0.5) ** 2 == C.EX_N and int(C.EX_EXACT_N ** 0.5) ** 2 == C.EX_EXACT_N and all(C.DEG_MIN <= d <= C.DEG_MAX for _k, d in C.EX_KINDS if d)
    assert set(C.EX_KS) == set(C.K_CHOICES) and len(set(C.SWEEP_SEEDS)) == len(C.SWEEP_SEEDS) == 4 and len(set(C.EX_EXACT_SEEDS)) == 6 and C.EX_EXACT_N <= 16
