"""Kern gegen Handrechnung (kleine Systeme aus conftest.py) und die Systeme auf dem Plan (DEMO-PLAYBOOK §1b)."""

import pytest

import uns_constants as C
import uns_systems as S
from uns_algorithm import System, elements, popcount
from uns_scenario import make_instance


def test_paarung_on_a_path_by_hand(paarung3):
    s = paarung3
    assert s.ind == [0, 1, 2, 4, 5]                                # ∅, {e0}, {e1}, {e2}, {e0, e2}
    assert s.maximal_sizes() == {1: 1, 2: 1}                       # {e1} und {e0, e2}
    assert s.ur[7] == 2 and s.lr[7] == 1 and s.q == 0.5 and s.f_star == 7
    assert s.lr[3] == s.ur[3] == 1                                 # {e0, e1}: beide Mengen der Größe 1
    w = [1.0, 1.001, 1.0]
    g = s.greedy(w)
    assert elements(g, 3) == [1] and s.value(g, w) == pytest.approx(1.001)
    ov, om = s.opt(w)
    assert ov == pytest.approx(2.0) and elements(om, 3) == [0, 2]
    assert s.value(s.greedy([1.0, 1.0, 1.001]), [1.0, 1.0, 1.001]) == pytest.approx(2.001)   # e2 zuerst, dann e0: Optimum


def test_star_by_hand(stern4):
    s = stern4
    assert s.maximal_sizes() == {1: 1, 4: 1} and s.q == 0.25 and s.lr[s.f_star] == 1 and s.ur[s.f_star] == 4
    w = [1.001, 1.0, 1.0, 1.0, 1.0]
    assert elements(s.greedy(w), 5) == [0] and s.opt(w)[0] == pytest.approx(4.0)


def test_knapsack_by_hand(rucksack):
    s = rucksack
    assert s.maximal_sizes() == {1: 1, 2: 1} and s.q == 0.5
    w = [6.001, 3.0, 3.0]
    assert elements(s.greedy(w), 3) == [0] and s.value(s.greedy(w), w) == pytest.approx(6.001) and s.opt(w)[0] == pytest.approx(6.001)
    w2 = [5.0, 3.0, 3.0]                                           # jetzt gewinnt das Paar der kleinen: 6 gegen 5
    assert elements(s.greedy(w2), 3) == [0] and s.opt(w2)[0] == pytest.approx(6.0)
    assert s.value(s.greedy(w2), w2) / 6.0 == pytest.approx(5.0 / 6.0)


def test_uniform_matroid_has_quotient_one_and_all_maximal_sets_of_equal_size(uniform):
    assert uniform.q == 1.0 and uniform.maximal_sizes() == {2: 6}
    w = [4.0, 1.0, 3.0, 2.0]
    assert elements(uniform.greedy(w), 4) == [0, 2] and uniform.opt(w)[0] == pytest.approx(7.0)


def test_sharp_weights_by_hand(paarung3, stern4):
    assert paarung3.sharp_weights(0.001) == [1.0, 1.001, 1.0]       # F = alle, kleinste maximale Menge {e1}
    s = paarung3
    g = s.greedy(s.sharp_weights(0.001))
    assert s.value(g, s.sharp_weights(0.001)) / s.opt(s.sharp_weights(0.001))[0] == pytest.approx(0.5005, abs=1e-12)
    w = stern4.sharp_weights(0.001)
    assert w == [1.001, 1.0, 1.0, 1.0, 1.0]


def test_greedy_ties_go_to_the_smaller_index(uniform):
    assert elements(uniform.greedy([1.0, 1.0, 1.0, 1.0]), 4) == [0, 1]


def test_systems_are_down_closed_and_have_the_empty_set():
    for key in C.SYSTEMS:
        s = S.get_system(key, 6, 3)
        assert s.check_down_closed() and s.ok[0] and s.ind[0] == 0, key


def test_system_sizes_on_the_standard_plan():
    counts = {key: len(S.get_system(key, 7, 8).ind) for key in C.SYSTEMS}
    assert counts == {"wald": 1316, "wald3": 1238, "wald2": 690, "paarung": 60, "budget": 1093, "standorte": 19, "uniform": 794}


def test_quotients_on_the_standard_plan():
    q = {key: S.get_system(key, 7, 8).q for key in C.SYSTEMS}
    assert q["wald"] == 1.0 and q["uniform"] == 1.0
    assert q["wald3"] == pytest.approx(0.6) and q["wald2"] == pytest.approx(0.6) and q["paarung"] == 0.5
    assert q["budget"] == pytest.approx(2 / 3) and q["standorte"] == pytest.approx(1 / 3)


def test_maximal_sizes_on_the_standard_plan():
    assert S.get_system("wald", 7, 8).maximal_sizes() == {6: 180}
    assert S.get_system("wald3", 7, 8).maximal_sizes() == {6: 152}
    assert S.get_system("wald2", 7, 8).maximal_sizes() == {5: 34, 6: 24}
    assert S.get_system("paarung", 7, 8).maximal_sizes() == {2: 2, 3: 16}
    assert S.get_system("standorte", 7, 8).maximal_sizes() == {2: 4, 3: 2}


def test_budget_system_respects_the_capacity():
    inst = make_instance(7, 8)
    cap = S.budget_cap(inst)
    s = S.build_system("budget", inst)
    assert cap == int(C.BUDGET_SHARE * sum(c for _, _, c in inst.edges))
    for mask in s.ind:
        assert sum(inst.edges[e][2] for e in elements(mask, s.m)) <= cap
    for mask in range(1 << s.m):
        if not s.ok[mask]:
            assert sum(inst.edges[e][2] for e in elements(mask, s.m)) > cap


def test_standorte_system_has_no_edge_inside_a_set():
    inst = make_instance(7, 8)
    s = S.build_system("standorte", inst)
    for mask in s.ind:
        assert not any(mask >> u & 1 and mask >> v & 1 for u, v, _ in inst.edges)


def test_forest_systems_have_the_documented_degree_bounds():
    inst = make_instance(7, 8)
    for key, bound in (("wald3", 3), ("wald2", 2), ("paarung", 1)):
        s = S.build_system(key, inst)
        for mask in s.ind:
            degree = [0] * inst.n
            for e in elements(mask, s.m):
                degree[inst.edges[e][0]] += 1
                degree[inst.edges[e][1]] += 1
            assert max(degree) <= bound, key


def test_weights_modes():
    s = S.get_system("wald", 7, 8)
    z = S.make_weights(s, "zufall", 5)
    g = S.make_weights(s, "ganz", 5)
    assert len(z) == len(g) == s.m and all(0.001 <= w <= 1 for w in z) and all(w in (1.0, 2.0, 3.0) for w in g)
    assert S.make_weights(s, "zufall", 5) == z and S.make_weights(s, "zufall", 6) != z
    assert S.make_weights(S.get_system("wald3", 7, 8), "scharf", 99) == S.make_weights(S.get_system("wald3", 7, 8), "scharf", 1)
    with pytest.raises(ValueError):
        S.make_weights(s, "unbekannt", 1)


def test_labels_of_edges_and_nodes():
    inst = make_instance(7, 8)
    assert S.labels("wald", inst) == [inst.label(e) for e in range(inst.m)]
    assert S.labels("standorte", inst) == list("ABCDEFG")


def test_scaling_systems_by_hand():
    assert S.star_system(4).q == 0.25 and S.star_system(4).m == 5
    assert S.path_matching_system(2).q == 1.0 and S.path_matching_system(3).q == 0.5
    k = S.knapsack_big_system(10)
    assert k.q == pytest.approx(0.1) and k.m == 11


def test_build_system_rejects_unknown_keys():
    with pytest.raises(ValueError):
        S.build_system("unbekannt", make_instance(6, 1))


def test_get_system_is_cached_and_deterministic():
    assert S.get_system("wald", 6, 1) is S.get_system("wald", 6, 1)
    a, b = S.build_system("wald3", make_instance(6, 1)), S.get_system("wald3", 6, 1)
    assert a.ind == b.ind and a.q == b.q


def test_popcount_and_elements():
    assert popcount(0b10110) == 3 and elements(0b10110, 5) == [1, 2, 4] and elements(0, 5) == []
