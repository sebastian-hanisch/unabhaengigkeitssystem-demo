"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und jedes Preset zeigt den Effekt, den sein Hilfetext verspricht."""

import uns_constants as C
import uns_evaluation as ev
import uns_presets as P


def _analysis(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_bounds_and_choices():
    for preset in C.PRESETS.values():
        assert C.N_MIN <= preset["n"] <= C.N_MAX and 0 <= preset["seed"] <= C.SEED_MAX and 0 <= preset["wseed"] <= C.SEED_MAX
        assert preset["system"] in C.SYSTEMS and preset["gewichte"] in C.WEIGHTS


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Standardfall (Voreinstellung)"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key_and_have_valid_defaults():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    for spec in P.SETTING_SPECS.values():
        assert spec.choices is None or (spec.default in spec.choices and spec.lo in spec.choices and spec.hi in spec.choices)


def test_standard_preset_is_a_matroid_and_greedy_is_optimal():
    a = _analysis("Standardfall (Voreinstellung)")
    assert a.q == 1.0 and abs(a.ratio - 1.0) < 1e-12 and ev.verdict_greedy(a)[0] == "success"


def test_sharp_preset_shows_greedy_at_the_guarantee():
    a = _analysis("Wald, höchstens 3 Leitungen, scharfe Gewichte")
    assert abs(a.q - 0.6) < 1e-12 and 0.6 <= a.ratio <= 0.6006 and ev.verdict_greedy(a)[0] == "warning" and "fast die schlechteste" in ev.verdict_greedy(a)[1]


def test_paarung_and_standorte_presets_are_below_the_optimum_but_above_the_guarantee():
    for name in ("Paarung", "Standorte ohne Nachbarn"):
        a = _analysis(name)
        assert a.q <= a.ratio < 1 and ev.verdict_greedy(a)[0] == "warning", name
    assert abs(_analysis("Paarung").ratio - 0.690) < 0.001 and abs(_analysis("Standorte ohne Nachbarn").ratio - 0.566) < 0.001


def test_budget_preset_is_close_to_but_below_the_optimum():
    a = _analysis("Budget-Auswahl (Rucksack)")
    assert 0.9 < a.ratio < 1 and abs(a.q - 2 / 3) < 1e-12
