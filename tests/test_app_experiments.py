"""AppTest: Hauptansicht, Experimente, Spielwiese, Permalink und PDF (DEMO-PLAYBOOK §3, §5)."""

import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

import uns_constants as C
import uns_evaluation as ev
from uns_pdf_export import build_pdf

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app(params=None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (params or {}).items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return [m.value for m in list(at.success) + list(at.info) + list(at.warning) + list(at.error)]


def _click_preset(at, name):
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, [str(e) for e in at.exception]


def test_kernfrage_verdict_matches_each_preset():
    expected = {
        "Standardfall (Voreinstellung)": "Greedy trifft das Optimum: Gewicht 4,052",
        "Wald, höchstens 3 Leitungen, scharfe Gewichte": "Greedy erreicht Gewicht 3,003 von 5,001",
        "Paarung": "Greedy erreicht Gewicht 1,624 von 2,355",
        "Standorte ohne Nachbarn": "Greedy erreicht Gewicht 1,084 von 1,914",
        "Budget-Auswahl (Rucksack)": "Greedy erreicht Gewicht 3,416 von 3,655",
    }
    at = _app()
    for name, needle in expected.items():
        _click_preset(at, name)
        assert any(needle in t for t in _texts(at)), name


def test_experiment_texts_for_the_standard_case():
    at = _app()
    texts = _texts(at)
    assert any("Alle 180 maximalen zulässigen Mengen haben dieselbe Größe 6" in t for t in texts)
    assert any("in **allen** Läufen optimal (Rangquotient 1)" in t for t in texts)
    assert any("Rangquotient **1**" in m.value for m in at.markdown)


def test_experiment_texts_for_a_non_matroid_show_the_worst_subset():
    at = _app(dict(system="wald2"))
    assert any("Schlimmste Teilmenge F" in m.value for m in at.markdown)
    assert any("34 mit 5, 24 mit 6 Elementen" in t for t in _texts(at))
    assert any("wird nie unterschritten" in t for t in _texts(at))


def test_scaling_button_shows_chart_table_and_verdict():
    at = _app()
    assert not any("q = 1/k bei allen" in t for t in _texts(at))
    at.button(key="scaling_run").click().run()
    assert not at.exception
    assert any("q = 1/k bei allen 9 Größen (k = 3 bis 11)" in t for t in _texts(at))


def test_scaling_stays_after_other_changes():
    at = _app()
    at.button(key="scaling_run").click().run()
    at.sidebar.selectbox(key="system_select").set_value("paarung").run()
    assert not at.exception and any("q = 1/k bei allen" in t for t in _texts(at))


def test_every_system_and_weight_kind_runs_without_exception():
    at = _app()
    for system in C.SYSTEMS:
        for gewichte in C.WEIGHTS:
            at.sidebar.selectbox(key="system_select").set_value(system)
            at.sidebar.selectbox(key="gewichte_select").set_value(gewichte)
            at.run()
            assert not at.exception, (system, gewichte, [str(e) for e in at.exception])


def test_weight_seed_is_disabled_for_sharp_weights_only():
    at = _app()
    assert not at.sidebar.number_input(key="wseed_input").disabled
    at.sidebar.selectbox(key="gewichte_select").set_value("scharf").run()
    assert at.sidebar.number_input(key="wseed_input").disabled
    assert [b for b in at.sidebar.button if b.label == "🎲 Neue Gewichte ziehen"][0].disabled


def test_new_weights_button_changes_the_weight_seed():
    at = _app()
    before = at.session_state["wseed_input"]
    [b for b in at.sidebar.button if b.label == "🎲 Neue Gewichte ziehen"][0].click().run()
    assert not at.exception and at.session_state["wseed_input"] != before


def test_permalink_loads_valid_values_and_ignores_invalid_choices():
    at = _app(dict(n="8", seed="3", system="paarung", gewichte="ganz", wseed="9"))
    assert at.sidebar.slider(key="n_slider").value == 8 and at.sidebar.number_input(key="seed_input").value == 3
    assert at.sidebar.selectbox(key="system_select").value == "paarung" and at.sidebar.selectbox(key="gewichte_select").value == "ganz"
    assert at.sidebar.number_input(key="wseed_input").value == 9
    bad = _app(dict(n="99", seed="-4", system="gibtsnicht", gewichte="x", wseed="abc"))
    assert bad.sidebar.slider(key="n_slider").value == C.N_MAX and bad.sidebar.number_input(key="seed_input").value == 0
    assert bad.sidebar.selectbox(key="system_select").value == "wald" and bad.sidebar.selectbox(key="gewichte_select").value == "zufall"
    assert bad.sidebar.number_input(key="wseed_input").value == C.DEFAULT_WSEED


def test_address_line_mirrors_the_settings():
    at = _app(dict(system="budget", gewichte="ganz"))
    assert str(at.query_params["system"]) in ("budget", "['budget']")


def test_playground_table_changes_with_the_system_and_the_result_is_a_pure_function():
    s = ev.Settings(n=7, seed=8, system="paarung")
    a = ev.analyse(s)
    r = ev.play_result(s, [1.0] * a.m)
    assert r["opt_value"] == 3.0 and r["greedy_value"] in (2.0, 3.0) and 0.5 <= r["ratio"] <= 1
    zero = ev.play_result(s, [0.0] * a.m)
    assert zero["opt_value"] == 0 and zero["ratio"] == 1.0


def test_playground_renders_for_every_system():
    for system in ("wald", "standorte", "budget"):
        at = _app(dict(system=system))
        assert any("Greedy wählt:" in c.value for c in at.caption), system


def test_pdf_button_makes_a_download():
    at = _app()
    at.button(key="pdf_make").click().run()
    assert not at.exception and "pdf_made" in at.session_state and at.session_state["pdf_made"][1][:4] == b"%PDF"


def test_pdf_builds_for_every_system():
    for key in C.SYSTEMS:
        s = ev.Settings(n=6, seed=2, system=key, gewichte="scharf")
        assert build_pdf(ev.analyse(s), s)[:4] == b"%PDF", key


def test_extreme_plan_sizes_with_every_system_do_not_raise():
    for n in (C.N_MIN, C.N_MAX):
        for system in ("wald3", "budget", "standorte"):
            at = _app(dict(n=str(n), system=system))
            assert not at.exception, (n, system)
