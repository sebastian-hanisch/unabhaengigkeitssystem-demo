"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): ein Element, zwei Elemente, Gleichstand, Nullen, Grenzen."""

import pytest

import uns_constants as C
import uns_evaluation as ev
import uns_systems as S
from uns_algorithm import System, elements


def test_a_single_free_element():
    s = System("ein Element", 1, [True, True])
    assert s.q == 1.0 and s.maximal_sizes() == {1: 1} and elements(s.greedy([2.0]), 1) == [0]
    assert s.opt([2.0]) == (2.0, 1) and s.sharp_weights() == [1.001]       # q = 1: Gewichte nur auf F* = {0}


def test_a_single_blocked_element_leaves_only_the_empty_set():
    s = System("gesperrt", 1, [True, False])
    assert s.ind == [0] and s.q == 1.0 and s.f_star == 0 and s.greedy([5.0]) == 0 and s.maximal_sizes() == {0: 1}
    assert s.sharp_weights() == [1.0] and s.opt([5.0]) == (0.0, 0)


def test_exactly_two_elements_that_exclude_each_other():
    s = System("zwei Elemente", 2, [True, True, True, False])
    assert s.maximal_sizes() == {1: 2} and s.q == 1.0                 # uniformes U(1, 2): ein Matroid
    assert s.greedy([1.0, 2.0]) == 2 and s.greedy([2.0, 1.0]) == 1


def test_two_independent_elements_are_a_matroid():
    s = System("frei", 2, [True] * 4)
    assert s.q == 1.0 and s.maximal_sizes() == {2: 1}


def test_all_equal_weights_greedy_takes_the_smallest_indices_and_is_optimal_on_a_matroid(uniform):
    w = [1.0] * 4
    assert elements(uniform.greedy(w), 4) == [0, 1] and uniform.value(uniform.greedy(w), w) == uniform.opt(w)[0]


def test_all_weights_zero_gives_zero_and_ratio_one_in_the_verdict(paarung3):
    w = [0.0, 0.0, 0.0]
    assert paarung3.value(paarung3.greedy(w), w) == 0 and paarung3.opt(w)[0] == 0
    kind, text = ev.verdict_play({"opt_value": 0.0, "greedy_value": 0.0, "ratio": 1.0, "q": 0.5})
    assert kind == "info" and "Alle Gewichte sind 0" in text


def test_zero_weight_elements_do_not_change_the_value(paarung3):
    w = [1.0, 0.0, 1.0]
    assert paarung3.value(paarung3.greedy(w), w) == 2.0 == paarung3.opt(w)[0]


def test_invalid_systems_are_rejected():
    for m in (0, 17):
        with pytest.raises(ValueError):
            System("x", m, [True] * (1 << min(m, 3)))
    with pytest.raises(ValueError):
        System("x", 2, [False, True, True, True])                     # leere Menge nicht zulässig
    with pytest.raises(ValueError):
        System("x", 2, [True, True])                                  # falsche Länge


def test_non_down_closed_family_is_detected_by_the_checker():
    s = System("kaputt", 2, [True, False, False, True])               # {0, 1} zulässig, aber {0} nicht
    assert not s.check_down_closed()


def test_smallest_and_largest_plan_sizes_work_for_every_system():
    for n in (C.N_MIN, C.N_MAX):
        for key in C.SYSTEMS:
            a = ev.analyse(ev.Settings(n=n, seed=3, system=key))
            assert a.ratio <= 1 + 1e-9 and a.q <= 1.0 and a.greedy_value <= a.opt_value + 1e-9, (n, key)


def test_ground_set_sizes_of_the_systems():
    inst_sizes = {C.N_MIN: 10, C.N_MAX: 16}
    for n, m in inst_sizes.items():
        assert S.get_system("wald", n, 2).m == m and S.get_system("standorte", n, 2).m == n


def test_scaling_rows_cover_every_documented_size():
    rows = ev.scaling_rows()
    assert len(rows) == len(C.SCALING_STAR) + len(C.SCALING_PATH) + len(C.SCALING_KNAPSACK)
    assert {r["family"] for r in rows} == {"Stern (unabhängige Menge)", "Paarung auf einem Pfad", "Rucksack mit einem großen Gegenstand"}
