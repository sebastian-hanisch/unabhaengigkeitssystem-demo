"""Eigenschaftstests (ORACLE-PLAYBOOK §5): Aussagen, die für jedes System gelten müssen, auf festen Zufallsinstanzen.

Hier stehen die Garantie, ihre Schärfe, die Maximalität von Greedy, die Invarianz gegen die Reihenfolge und gegen streng wachsende Umrechnung der Gewichte
und die Reproduzierbarkeit über Prozesse (Hash-Reihenfolge)."""

import os
import random
import subprocess
import sys
from pathlib import Path

import pytest

import uns_constants as C
import uns_evaluation as ev
import uns_systems as S
from uns_algorithm import System, elements, popcount

ROOT = Path(__file__).resolve().parent.parent


def _plan_systems():
    for key in C.SYSTEMS:
        for n, seed in ((6, 1), (6, 5), (7, 8)):
            yield key, n, seed, S.get_system(key, n, seed)


def test_guarantee_never_violated_on_the_plan_systems_with_three_weight_kinds():
    rng = random.Random(2)
    for key, n, seed, s in _plan_systems():
        for kind in ("zufall", "ganz", "null"):
            for _ in range(30):
                w = [max(0.001, round(rng.random(), 3)) if kind == "zufall" else float(rng.randint(1, 3)) if kind == "ganz" else rng.choice((0.0, 0.0, 1.0)) for _ in range(s.m)]
                opt = s.opt(w)[0]
                assert s.value(s.greedy(w), w) >= s.q * opt - 1e-9, (key, n, seed, kind)


def test_sharp_weights_reach_the_quotient_on_every_plan_system():
    for key, n, seed, s in _plan_systems():
        w = s.sharp_weights(C.DELTA)
        ratio = s.value(s.greedy(w), w) / s.opt(w)[0]
        assert s.q - 1e-9 <= ratio <= s.q * (1 + 2 * C.DELTA) + 1e-9, (key, n, seed, ratio, s.q)
        if key in C.SYSTEM_MATROIDS:
            assert ratio == pytest.approx(1.0)
        else:
            assert ratio < 1 - 1e-6, (key, n, seed)


def test_matroids_have_quotient_one_and_greedy_is_always_optimal_and_non_matroids_have_less():
    for key, n, seed, s in _plan_systems():
        assert (s.q == 1.0) == (key in C.SYSTEM_MATROIDS), (key, n, seed, s.q)
        if key in C.SYSTEM_MATROIDS:
            rng = random.Random(seed)
            for _ in range(20):
                w = [float(rng.randint(0, 3)) for _ in range(s.m)]
                assert s.value(s.greedy(w), w) == s.opt(w)[0]


def test_greedy_is_always_feasible_and_maximal():
    rng = random.Random(8)
    for key, n, seed, s in _plan_systems():
        for _ in range(20):
            w = [float(rng.randint(0, 3)) for _ in range(s.m)]
            g = s.greedy(w)
            assert s.ok[g] and s.is_maximal(g), (key, n, seed)


def test_every_maximal_set_is_the_result_of_greedy_for_some_weights():
    for key in ("wald2", "paarung", "standorte", "budget"):
        settings = ev.Settings(n=6, seed=1, system=key)
        s = S.get_system(key, 6, 1)
        for i in s.ind:
            if s.is_maximal(i):
                w, g = ev.greedy_can_return(settings, i)
                assert g == i, (key, i)


def test_quotient_bounds_the_whole_ground_set_quotient_from_below():
    for key, n, seed, s in _plan_systems():
        full = s.full
        assert s.q <= s.lr[full] / s.ur[full] + 1e-12 and 0 < s.q <= 1


def test_quotient_does_not_depend_on_the_element_order():
    rng = random.Random(4)
    for _ in range(20):
        m = rng.randint(3, 7)
        tops = [rng.getrandbits(m) for _ in range(3)]
        ok = [any(mask & ~t == 0 for t in tops) for mask in range(1 << m)]
        s = System("a", m, ok)
        perm = list(range(m))
        rng.shuffle(perm)
        ok2 = [False] * (1 << m)
        for mask in range(1 << m):
            image = sum(1 << perm[e] for e in range(m) if mask >> e & 1)
            ok2[image] = ok[mask]
        assert System("b", m, ok2).q == pytest.approx(s.q)


def test_greedy_result_depends_only_on_the_order_of_the_weights():
    rng = random.Random(6)
    for key, n, seed, s in _plan_systems():
        w = rng.sample(range(1, 200), s.m)
        base = s.greedy([float(x) for x in w])
        assert s.greedy([float(x) ** 3 for x in w]) == base and s.greedy([float(x) + 1000 for x in w]) == base


def test_adding_a_constant_to_all_weights_cannot_lower_the_guarantee_value_below_q():
    rng = random.Random(10)
    for key, n, seed, s in _plan_systems():
        w = [rng.random() + 1.0 for _ in range(s.m)]
        assert s.value(s.greedy(w), w) >= s.q * s.opt(w)[0] - 1e-9


def test_analysis_numbers_are_consistent():
    for key in C.SYSTEMS:
        a = ev.analyse(ev.Settings(n=6, seed=2, system=key))
        s = S.get_system(key, 6, 2)
        assert s.ok[a.greedy_mask] and s.ok[a.opt_mask] and a.greedy_value <= a.opt_value + 1e-9
        assert a.ratio == pytest.approx(a.greedy_value / a.opt_value) and a.n_independent == len(s.ind)
        assert popcount(a.low_mask) == a.lr and popcount(a.high_mask) == a.ur and (a.f_star == 0 or a.low_mask & ~a.f_star == 0)
        assert all(w >= 0 for w in a.weights) and len(a.weights) == len(a.labels) == a.m


def test_statistics_are_identical_in_two_processes_with_different_hash_seeds():
    code = (
        "import sys; sys.path.insert(0, %r); import uns_evaluation as ev; "
        "s = ev.Settings(n=6, seed=3, system='wald2', gewichte='ganz', wseed=4); a = ev.analyse(s); d = ev.ratio_distribution(s, runs=100); "
        "print(a); print(d); print(ev.maximal_stats(s)); print(ev.scaling_rows()[:3])"
    ) % str(ROOT)
    outs = []
    for hash_seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed)
        outs.append(subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, timeout=120, check=True).stdout)
    assert outs[0] == outs[1] and outs[0].strip()
