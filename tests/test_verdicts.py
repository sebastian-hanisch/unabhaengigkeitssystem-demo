"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jeder Zweig der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds."""

import pytest

import uns_constants as C
import uns_evaluation as ev
from uns_scenario import make_instance


def _a(**kw):
    base = dict(
        settings=ev.Settings(), inst=make_instance(6, 1), m=3, labels=("e0", "e1", "e2"), weights=(1.0, 1.001, 1.0), greedy_mask=0b010, opt_mask=0b101,
        greedy_value=1.001, opt_value=2.0, ratio=1.001 / 2.0, q=0.5, f_star=0b111, lr=1, ur=2, low_mask=0b010, high_mask=0b101, n_independent=5,
    )
    base.update(kw)
    return ev.Analysis(**base)


def test_formatting_helpers():
    assert ev.de(0.6, 3) == "0,600" and ev.de(16.666, 1) == "16,7" and ev.prozent(0.5006) == "50,1" and ev.prozent(0.6, 0) == "60"
    assert ev.gewicht(1.0) == "1" and ev.gewicht(1.001) == "1,001" and ev.gewicht(0.5) == "0,5" and ev.gewicht(0.0) == "0" and ev.gewicht(12.0) == "12"


def test_greedy_optimal_on_a_matroid_is_a_success_naming_quotient_one():
    kind, text = ev.verdict_greedy(_a(ratio=1.0, greedy_value=2.0, q=1.0))
    assert kind == "success" and "Gewicht 2" in text and "Rangquotient ist **1**" in text


def test_greedy_optimal_by_luck_on_a_non_matroid_is_an_info_that_names_the_guarantee():
    kind, text = ev.verdict_greedy(_a(ratio=1.0, greedy_value=2.0, q=0.6))
    assert kind == "info" and "Greedy trifft hier das Optimum (Gewicht 2)" in text and "nur **0,600** des Optimums" in text


def test_greedy_below_the_optimum_names_both_values_the_percentage_and_the_guarantee():
    kind, text = ev.verdict_greedy(_a(greedy_value=1.5, opt_value=2.0, ratio=0.75, q=0.5))
    assert kind == "warning" and "Gewicht 1,5 von 2" in text and "**75,0 %**" in text and "mindestens 50,0 % (Rangquotient 0,500)" in text
    assert "fast die schlechteste" not in text


def test_greedy_close_to_the_guarantee_is_called_almost_worst_case():
    assert "fast die schlechteste mögliche Lage" in ev.verdict_greedy(_a(ratio=0.5005, q=0.5))[1]
    assert "fast die schlechteste" in ev.verdict_greedy(_a(ratio=0.509, q=0.5))[1]               # unter 0,01 über q zählt mit
    assert "fast die schlechteste" not in ev.verdict_greedy(_a(ratio=0.511, q=0.5))[1]


def test_rank_text_for_a_non_matroid_names_the_sets_and_the_quotient():
    text = ev.rank_text(_a())
    assert "Schlimmste Teilmenge F = {e0, e1, e2} (3 Elemente)" in text and "hat 1 ({e1})" in text and "größte zulässige Teilmenge 2 ({e0, e2})" in text
    assert "q = 1 / 2 = **0,500**" in text


def test_rank_text_for_a_matroid_and_for_an_empty_system():
    assert "Rangquotient **1**" in ev.rank_text(_a(q=1.0, lr=1, ur=1, f_star=0b001)) and "Matroids" in ev.rank_text(_a(q=1.0, lr=1, ur=1, f_star=0b001))
    assert "kein zulässiges Element" in ev.rank_text(_a(f_star=0, q=1.0))


def test_names_of_a_mask():
    a = _a()
    assert ev.names(a, 0b101) == "e0, e2" and ev.names(a, 0) == "keine"


def test_distribution_verdict_branches():
    base = {"ratios": (1.0, 0.5), "q": 0.5, "runs": 1000, "integer": False, "mean": 0.9234, "min": 0.6022, "nonopt": 647, "violations": 0}
    kind, text = ev.verdict_distribution(base)
    assert kind == "info" and "Bei 1000 zufälligen Gewichtsvektoren aus Gewichten zwischen 0 und 1" in text and "in 647 Läufen (64,7 %) nicht optimal" in text
    assert "**92,3 %**" in text and "im schlechtesten Lauf 60,2 %" in text and "q = 0,500 wird nie unterschritten" in text
    assert "ganzen Zahlen 1 bis 3" in ev.verdict_distribution(dict(base, integer=True))[1]
    kind, text = ev.verdict_distribution(dict(base, q=1.0, nonopt=0, mean=1.0, min=1.0))
    assert kind == "success" and "in **allen** Läufen optimal (Rangquotient 1)" in text
    kind, text = ev.verdict_distribution(dict(base, violations=2))
    assert kind == "error" and "Bei 2 von 1000" in text


def test_maximal_verdict_branches():
    kind, text = ev.verdict_maximal({"sizes": {6: 180}, "total": 180, "lr": 6, "ur": 6})
    assert kind == "info" and "Alle 180 maximalen zulässigen Mengen haben dieselbe Größe 6" in text and "wie ein Matroid" in text
    kind, text = ev.verdict_maximal({"sizes": {5: 34, 6: 24}, "total": 58, "lr": 5, "ur": 6})
    assert kind == "warning" and "58 maximale zulässige Mengen: 34 mit 5, 24 mit 6 Elementen" in text and "Die Mengen mit 5 Elementen sind maximal, aber nicht größtmöglich (die größte hat 6)" in text


def test_scaling_verdict_names_the_ranges_and_flags_a_broken_pattern():
    rows = ev.scaling_rows()
    kind, text = ev.verdict_scaling(rows)
    assert kind == "info" and "q = 1/k bei allen 9 Größen (k = 3 bis 11)" in text and "(k = 2 bis 10)" in text and "bei 3 bis 11 Kanten q = 1/2 (nach dem bekannten Satz für Paarungen allgemein; bei 2 Kanten q = 1)" in text
    broken = [dict(r, q=0.9) if r["family"] == "Stern (unabhängige Menge)" else r for r in rows]
    assert ev.verdict_scaling(broken)[0] == "warning"


def test_play_verdicts():
    assert ev.verdict_play({"opt_value": 2.0, "greedy_value": 2.0, "ratio": 1.0, "q": 0.5}) == ("success", "Greedy trifft das Optimum (Gewicht 2).")
    kind, text = ev.verdict_play({"opt_value": 2.0, "greedy_value": 1.001, "ratio": 0.5006, "q": 0.5})
    assert kind == "warning" and "1,001 von 2" in text and "50,1 % des Optimums (Garantie mindestens 50,0 %)" in text


def test_constants_used_in_texts():
    assert C.DISTRIBUTION_RUNS == 1000 and C.DELTA == 0.001 and C.BUDGET_SHARE == 0.4 and C.UNIFORM_K == 4
    assert set(C.SYSTEM_MATROIDS) == {"wald", "uniform"} and set(C.SYSTEM_NAMES) == set(C.SYSTEMS) and set(C.WEIGHT_NAMES) == set(C.WEIGHTS)
    assert pytest.approx(0.001) == C.DELTA
