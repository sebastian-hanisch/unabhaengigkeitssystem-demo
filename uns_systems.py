"""Die Unabhängigkeitssysteme der Demo, gebaut aus einem Leitungsnetz (Plan), dazu die Gewichte."""

import random
from functools import lru_cache

import uns_constants as C
from uns_algorithm import System, popcount
from uns_scenario import Instance, make_instance


def _forest_ok(inst: Instance, maxdeg: int) -> list[bool]:
    """Wald: kein Kreis, und mit maxdeg > 0 höchstens maxdeg Leitungen an jedem Standort."""
    n, m = inst.n, inst.m
    ok = [False] * (1 << m)
    for mask in range(1 << m):
        label = list(range(n))
        deg = [0] * n
        good = True
        for e in range(m):
            if mask >> e & 1:
                u, v, _ = inst.edges[e]
                deg[u] += 1
                deg[v] += 1
                if (maxdeg and (deg[u] > maxdeg or deg[v] > maxdeg)) or label[u] == label[v]:
                    good = False
                    break
                old, new = label[v], label[u]
                label = [new if x == old else x for x in label]
        ok[mask] = good
    return ok


def build_system(key: str, inst: Instance) -> System:
    """System `key` (aus C.SYSTEMS) auf dem Plan. Grundmenge: die Leitungen, bei "standorte" die Standorte."""
    if key not in C.SYSTEMS:
        raise ValueError(f"unbekanntes System: {key}")
    name = C.SYSTEM_NAMES[key]
    m = inst.m
    if key == "wald":
        return System(name, m, _forest_ok(inst, 0))
    if key == "wald3":
        return System(name, m, _forest_ok(inst, 3))
    if key == "wald2":
        return System(name, m, _forest_ok(inst, 2))
    if key == "paarung":
        return System(name, m, _forest_ok(inst, 1))
    if key == "budget":
        cap = int(C.BUDGET_SHARE * sum(c for _, _, c in inst.edges))
        return System(name, m, [sum(inst.edges[e][2] for e in range(m) if mask >> e & 1) <= cap for mask in range(1 << m)])
    if key == "standorte":
        n = inst.n
        return System(name, n, [all(not (mask >> u & 1 and mask >> v & 1) for u, v, _ in inst.edges) for mask in range(1 << n)])
    return System(name, m, [popcount(mask) <= C.UNIFORM_K for mask in range(1 << m)])


@lru_cache(maxsize=24)
def get_system(key: str, n: int, seed: int) -> System:
    """Gleiches System für gleiche (key, n, seed): der Aufbau kostet bei 16 Leitungen etwa eine Sekunde."""
    return build_system(key, make_instance(n, seed))


def budget_cap(inst: Instance) -> int:
    return int(C.BUDGET_SHARE * sum(c for _, _, c in inst.edges))


def labels(key: str, inst: Instance) -> list[str]:
    """Beschriftung der Elemente: Leitungen "A–B", bei "standorte" die Standortnamen."""
    return [inst.name(v) for v in range(inst.n)] if key == "standorte" else [inst.label(e) for e in range(inst.m)]


def make_weights(sys_: System, mode: str, seed: int) -> list[float]:
    """Gewichte der Elemente: Zufall (drei Stellen, zwischen 0,001 und 1), ganze Zahlen 1 bis 3, oder scharf aus dem Rangquotienten."""
    if mode == "scharf":
        return sys_.sharp_weights(C.DELTA)
    rng = random.Random(seed)
    if mode == "ganz":
        return [float(rng.randint(1, 3)) for _ in range(sys_.m)]
    if mode == "zufall":
        return [max(0.001, round(rng.random(), 3)) for _ in range(sys_.m)]
    raise ValueError(f"unbekannte Gewichtsart: {mode}")


# --- kleine Systeme für die Skalierung (Experiment 5) ---------------------------------------------------------------------------------


def star_system(k: int) -> System:
    """Unabhängige Menge im Stern: Zentrum 0 und k Blätter; Zentrum und Blätter schließen sich aus."""
    n = k + 1
    return System(f"Stern mit {k} Blättern", n, [not (mask & 1 and mask > 1) for mask in range(1 << n)])


def path_matching_system(e: int) -> System:
    """Paarung auf einem Pfad mit e Kanten: benachbarte Kanten schließen sich aus."""
    return System(f"Pfad mit {e} Kanten", e, [all(not (mask >> i & 1 and mask >> (i + 1) & 1) for i in range(e - 1)) for mask in range(1 << e)])


def knapsack_big_system(k: int) -> System:
    """Rucksack: ein Gegenstand der Größe k und k Gegenstände der Größe 1, Kapazität k."""
    sizes = [k] + [1] * k
    return System(f"Rucksack mit einem Gegenstand der Größe {k}", k + 1, [sum(sizes[e] for e in range(k + 1) if mask >> e & 1) <= k for mask in range(1 << (k + 1))])
