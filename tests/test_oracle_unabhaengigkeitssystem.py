"""Orakel-Tests (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK): Kernroutinen gegen einen anderen Rechenweg.

Orakel: (1) lr, ur und q direkt über alle Paare (F, I) ohne die Teilmengen-DP des Moduls, auf 60 zufälligen Systemen und den Systemen des Plans;
(2) Optimum durch Aufzählen aller zulässigen Mengen; (3) networkx: größter Spannbaum (Wald), maximales gewichtetes Matching (Paarung),
größte gewichtete Clique im Komplement (unabhängige Standorte); (4) Rucksack-Dynamik über die Kapazität (Budget); (5) Greedy ist zulässig und maximal
(eigener Prüfer). Alles unter 10 s."""

import random

import pytest

import uns_constants as C
import uns_systems as S
from uns_algorithm import System, elements, popcount
from uns_scenario import make_instance


def _random_system(rng, m):
    """Zufälliges nach unten abgeschlossenes System: Abschluss einiger zufälliger Mengen nach unten."""
    tops = [rng.getrandbits(m) for _ in range(rng.randint(1, 5))]
    ok = [any(mask & ~t == 0 for t in tops) for mask in range(1 << m)]
    ok[0] = True
    return System("zufällig", m, ok)


def _oracle_ranks(s):
    """lr, ur und q ohne Teilmengen-DP: für jedes F alle zulässigen I ⊆ F, davon die maximalen und die größten."""
    q = None
    for f in range(1, 1 << s.m):
        inside = [i for i in range(1 << s.m) if i & ~f == 0 and s.ok[i]]
        ur = max(popcount(i) for i in inside)
        if ur == 0:
            continue
        maximal = [i for i in inside if all(not s.ok[i | 1 << e] for e in range(s.m) if f >> e & 1 and not i >> e & 1)]
        lr = min(popcount(i) for i in maximal)
        assert (s.lr[f], s.ur[f]) == (lr, ur), (f, s.lr[f], lr, s.ur[f], ur)
        q = lr / ur if q is None else min(q, lr / ur)
    return q if q is not None else 1.0


def test_ranks_and_quotient_match_the_direct_computation_on_60_random_systems():
    rng = random.Random(11)
    for _ in range(60):
        s = _random_system(rng, rng.randint(2, 7))
        assert s.check_down_closed()
        assert s.q == pytest.approx(_oracle_ranks(s))


def test_ranks_match_the_direct_computation_on_the_hand_systems(paarung3, stern4, rucksack, uniform):
    for s in (paarung3, stern4, rucksack, uniform):
        assert s.q == pytest.approx(_oracle_ranks(s))


def test_optimum_matches_enumeration_on_random_systems_and_weights():
    rng = random.Random(5)
    for _ in range(40):
        s = _random_system(rng, rng.randint(2, 8))
        w = [rng.random() for _ in range(s.m)]
        best = max(sum(w[e] for e in elements(i, s.m)) for i in s.ind)
        assert s.opt(w)[0] == pytest.approx(best)
        assert s.opt_batch([[x] for x in w])[0] == pytest.approx(best)


def test_greedy_is_feasible_and_maximal_by_an_independent_check():
    rng = random.Random(7)
    for _ in range(60):
        s = _random_system(rng, rng.randint(2, 8))
        w = [float(rng.randint(1, 3)) for _ in range(s.m)]
        g = s.greedy(w)
        assert s.ok[g]
        assert all(not s.ok[g | 1 << e] for e in range(s.m) if not g >> e & 1)


def test_wald_optimum_equals_the_networkx_maximum_spanning_tree():
    nx = pytest.importorskip("networkx")
    for seed in range(20):
        inst = make_instance(6 + seed % 3, seed)
        s = S.get_system("wald", inst.n, seed)
        w = S.make_weights(s, "zufall", seed)
        g = nx.Graph()
        g.add_weighted_edges_from((u, v, w[e]) for e, (u, v, _) in enumerate(inst.edges))
        assert s.opt(w)[0] == pytest.approx(nx.maximum_spanning_tree(g).size(weight="weight"))


def test_paarung_optimum_equals_the_networkx_maximum_weight_matching():
    nx = pytest.importorskip("networkx")
    for seed in range(20):
        inst = make_instance(6 + seed % 3, seed)
        s = S.get_system("paarung", inst.n, seed)
        w = S.make_weights(s, "zufall", seed + 1)
        g = nx.Graph()
        g.add_weighted_edges_from((u, v, w[e]) for e, (u, v, _) in enumerate(inst.edges))
        matching = nx.max_weight_matching(g)
        assert s.opt(w)[0] == pytest.approx(sum(g[u][v]["weight"] for u, v in matching))


def test_standorte_optimum_equals_the_maximum_weight_independent_set_via_a_clique_in_the_complement():
    nx = pytest.importorskip("networkx")
    for seed in range(20):
        inst = make_instance(6 + seed % 3, seed)
        s = S.get_system("standorte", inst.n, seed)
        w = S.make_weights(s, "zufall", seed + 2)
        comp = nx.complement(nx.Graph([(u, v) for u, v, _ in inst.edges]))
        comp.add_nodes_from(range(inst.n))
        for v in range(inst.n):
            comp.nodes[v]["weight"] = max(1, round(w[v] * 1000))
        _, weight = nx.max_weight_clique(comp, weight="weight")
        scaled = [max(1, round(x * 1000)) for x in w]
        assert s.opt(scaled)[0] == weight


def test_budget_optimum_equals_a_capacity_dynamic_program():
    for seed in range(20):
        inst = make_instance(6 + seed % 3, seed)
        s = S.get_system("budget", inst.n, seed)
        w = S.make_weights(s, "ganz", seed)
        cap = S.budget_cap(inst)
        best = [0.0] * (cap + 1)
        for e, (_, _, size) in enumerate(inst.edges):
            for c in range(cap, size - 1, -1):
                best[c] = max(best[c], best[c - size] + w[e])
        assert s.opt(w)[0] == pytest.approx(best[cap])


def test_guarantee_greedy_at_least_q_times_the_optimum_on_random_systems():
    rng = random.Random(3)
    for _ in range(40):
        s = _random_system(rng, rng.randint(2, 8))
        for _ in range(25):
            w = [rng.choice((0.0, 1.0, 2.0, rng.random())) for _ in range(s.m)]
            opt = s.opt(w)[0]
            assert s.value(s.greedy(w), w) >= s.q * opt - 1e-9, (s.q, w)


def test_the_guarantee_is_sharp_on_random_systems():
    rng = random.Random(13)
    seen_below_one = 0
    for _ in range(40):
        s = _random_system(rng, rng.randint(2, 8))
        w = s.sharp_weights(1e-6)
        opt = s.opt(w)[0]
        if opt <= 0:
            continue
        ratio = s.value(s.greedy(w), w) / opt
        assert s.q - 1e-9 <= ratio <= s.q * (1 + 1e-5) + 1e-9, (s.q, ratio)
        seen_below_one += s.q < 1 - 1e-9
    assert seen_below_one > 10


def test_plan_systems_match_the_direct_rank_computation_on_a_small_plan():
    for key in C.SYSTEMS:
        s = S.get_system(key, 5, 4)                          # 5 Standorte, 8 Leitungen: das direkte Orakel bleibt schnell
        assert s.q == pytest.approx(_oracle_ranks(s)), key
