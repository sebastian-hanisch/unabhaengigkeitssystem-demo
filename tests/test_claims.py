"""Jede Zahl der README („Befunde“) wird hier mit den Funktionen der App nachgerechnet (DEMO-PLAYBOOK §4)."""

import re
from pathlib import Path

import pytest

import uns_constants as C
import uns_evaluation as ev
import uns_systems as S

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
PLAN = (7, 8)


def _settings(key, gewichte="zufall", wseed=1):
    return ev.Settings(PLAN[0], PLAN[1], key, gewichte, wseed)


def test_system_table_sizes_and_quotients():
    expected = {"wald": (1316, 1.0), "wald3": (1238, 0.6), "wald2": (690, 0.6), "paarung": (60, 0.5), "budget": (1093, 2 / 3), "standorte": (19, 1 / 3), "uniform": (794, 1.0)}
    for key, (count, q) in expected.items():
        s = S.get_system(key, *PLAN)
        assert len(s.ind) == count and s.q == pytest.approx(q), key
    assert S.get_system("wald", *PLAN).m == 12


def test_sharp_weights_ratios_per_system():
    expected = {"wald": 1.0, "wald3": 0.6005, "wald2": 0.6004, "paarung": 0.5005, "budget": 0.6671, "standorte": 0.3337, "uniform": 1.0}
    for key, ratio in expected.items():
        a = ev.analyse(_settings(key, "scharf"))
        assert round(a.ratio, 4) == ratio, key
        if key in C.SYSTEM_MATROIDS:
            assert a.ratio == pytest.approx(1.0)
        else:
            assert 0 < a.ratio - a.q <= 0.0006, key


def test_random_weights_table():
    expected = {  # nicht optimal, Mittel (Prozent), schlechtester Lauf (Prozent), jeweils Plan 7/8, Gewichts-Seed 1, 1000 Vektoren zwischen 0 und 1
        "wald": (0, "100,0", "100,0"), "wald3": (77, "99,7", "86,3"), "wald2": (450, "97,1", "77,7"), "paarung": (389, "95,3", "63,6"),
        "budget": (401, "97,5", "79,0"), "standorte": (327, "93,8", "37,1"), "uniform": (0, "100,0", "100,0"),
    }
    for key, (nonopt, mean, worst) in expected.items():
        d = ev.ratio_distribution(_settings(key))
        assert d["runs"] == 1000 and d["nonopt"] == nonopt and ev.prozent(d["mean"]) == mean and ev.prozent(d["min"]) == worst, key


def test_guarantee_never_violated_in_the_readme_runs():
    total = 0
    for key in C.SYSTEMS:
        for g in ("zufall", "ganz"):
            d = ev.ratio_distribution(_settings(key, g))
            assert d["violations"] == 0, (key, g)
            total += 1
    assert total == 14 and len(C.SYSTEMS) == 7


def test_standard_case_numbers():
    a = ev.analyse(_settings("wald"))
    assert ev.gewicht(a.greedy_value) == "4,052" == ev.gewicht(a.opt_value) and a.q == 1.0
    assert ev.maximal_stats(_settings("wald"))["sizes"] == {6: 180}


def test_preset_numbers():
    expected = {
        "Wald, höchstens 3 Leitungen, scharfe Gewichte": ("3,003", "5,001", "60,0"),
        "Paarung": ("1,624", "2,355", "69,0"),
        "Standorte ohne Nachbarn": ("1,084", "1,914", "56,6"),
        "Budget-Auswahl (Rucksack)": ("3,416", "3,655", "93,5"),
    }
    for name, (greedy, opt, percent) in expected.items():
        a = ev.analyse(ev.Settings(**C.PRESETS[name]))
        assert (ev.gewicht(a.greedy_value), ev.gewicht(a.opt_value), ev.prozent(a.ratio)) == (greedy, opt, percent), name
    assert C.PRESETS["Paarung"]["wseed"] == 6 and C.PRESETS["Standorte ohne Nachbarn"]["wseed"] == 8 and C.PRESETS["Budget-Auswahl (Rucksack)"]["wseed"] == 1


def test_maximal_sizes_in_the_readme():
    expected = {
        "wald": {6: 180}, "wald3": {6: 152}, "wald2": {5: 34, 6: 24}, "paarung": {2: 2, 3: 16}, "budget": {4: 15, 5: 128, 6: 53}, "standorte": {2: 4, 3: 2}, "uniform": {4: 495},
    }
    for key, sizes in expected.items():
        assert ev.maximal_stats(_settings(key))["sizes"] == sizes, key


def test_scaling_numbers():
    rows = ev.scaling_rows()
    star = [r for r in rows if r["family"].startswith("Stern")]
    knap = [r for r in rows if r["family"].startswith("Rucksack")]
    path = [r for r in rows if r["family"].startswith("Paarung")]
    assert [r["size"] for r in star] == list(range(3, 12)) and all(r["q"] == pytest.approx(1 / r["size"]) for r in star)
    assert [r["size"] for r in knap] == list(range(2, 11)) and all(r["q"] == pytest.approx(1 / r["size"]) for r in knap)
    assert [r["size"] for r in path] == list(range(2, 12)) and path[0]["q"] == 1.0 and all(r["q"] == 0.5 for r in path[1:])


def test_budget_and_system_description_in_the_readme():
    assert C.BUDGET_SHARE == 0.4 and C.UNIFORM_K == 4 and C.DELTA == 0.001 and C.DISTRIBUTION_RUNS == 1000
    assert S.get_system("wald3", *PLAN).maximal_sizes() == {6: 152}                  # „alle 152 maximalen Mengen haben sechs Leitungen“
    assert S.get_system("wald3", *PLAN).q == pytest.approx(0.6)


def test_readme_names_every_checked_number():
    for needle in ("**4,052**", "**180**", "0 Verletzungen", "**3,003 von 5,001**", "**60,0 %**", "**69,0 %**", "**56,6 %**", "**93,5 %**", "**34 mit 5 und 24 mit 6**",
                   "495 mit 4", "q = **1/k** für k = 3 bis 11", "**1/2** bei 3 bis 11 Kanten", "alle 152 maximalen Mengen", "höchstens 0,0006", "| 1316 |", "| 1238 |",
                   "| 690 |", "| 60 |", "| 1093 |", "| 19 |", "| 794 |", "77, 99,7 %, 86,3 %", "450, 97,1 %, 77,7 %", "389, 95,3 %, 63,6 %", "401, 97,5 %, 79,0 %",
                   "327, 93,8 %, 37,1 %"):
        assert needle in README, needle


def test_readme_table_has_no_decimal_points():
    table = README.split("## Befunde (gemessen, keine Behauptungen)")[1].split("## Ehrliche Grenzen")[0]
    assert not re.search(r"\d\.\d", table)
