"""Kennzahlen, Messreihen und Verdikte. Alle sichtbaren Zahlen kommen aus diesen Funktionen."""

import random
from dataclasses import dataclass

import uns_constants as C
from uns_algorithm import elements, popcount
from uns_scenario import Instance, make_instance
from uns_systems import get_system, knapsack_big_system, labels, make_weights, path_matching_system, star_system

EPS = 1e-9


def de(x: float, digits: int = 1) -> str:
    """Zahl mit Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


def prozent(x: float, digits: int = 1) -> str:
    return de(100.0 * x, digits)


def gewicht(x: float) -> str:
    """Gewicht ohne überflüssige Nullen (1 statt 1,000; 1,001 bleibt)."""
    text = f"{x:.3f}".rstrip("0").rstrip(".")
    return (text or "0").replace(".", ",")


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    system: str = "wald"
    gewichte: str = "zufall"
    wseed: int = C.DEFAULT_WSEED


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    inst: Instance
    m: int                  # Zahl der Elemente der Grundmenge
    labels: tuple
    weights: tuple
    greedy_mask: int
    opt_mask: int
    greedy_value: float
    opt_value: float
    ratio: float            # Greedy / Optimum (1, wenn das Optimum 0 ist)
    q: float
    f_star: int
    lr: int
    ur: int
    low_mask: int           # eine kleinste maximale zulässige Teilmenge von F*
    high_mask: int          # eine größte zulässige Teilmenge von F*
    n_independent: int


def analyse(settings: Settings) -> Analysis:
    sys_ = get_system(settings.system, settings.n, settings.seed)
    inst = make_instance(settings.n, settings.seed)
    w = make_weights(sys_, settings.gewichte, settings.wseed)
    g = sys_.greedy(w)
    opt_value, opt_mask = sys_.opt(w)
    gv = sys_.value(g, w)
    f = sys_.f_star
    return Analysis(
        settings, inst, sys_.m, tuple(labels(settings.system, inst)), tuple(w), g, opt_mask, gv, opt_value, gv / opt_value if opt_value > 0 else 1.0,
        sys_.q, f, sys_.lr[f], sys_.ur[f], sys_.smallest_maximal_in_f_star() if f else 0, sys_.largest_in_f_star() if f else 0, len(sys_.ind),
    )


def names(a: Analysis, mask: int) -> str:
    return ", ".join(a.labels[e] for e in elements(mask, a.m)) or "keine"


# --- Kernfrage und Rangquotient -----------------------------------------------------------------------------------------------------


def verdict_greedy(a: Analysis) -> tuple[str, str]:
    """Verdikt der Kernfrage: Wie gut ist Greedy hier, und was sagt die Garantie?"""
    if a.ratio >= 1 - EPS:
        if a.q >= 1 - EPS:
            return "success", (
                f"Greedy trifft das Optimum: Gewicht {gewicht(a.greedy_value)}. Der Rangquotient ist **1**: Auf diesem System kann Greedy "
                "bei keinen Gewichten unter dem Optimum liegen."
            )
        return "info", (
            f"Greedy trifft hier das Optimum (Gewicht {gewicht(a.greedy_value)}), obwohl die Garantie nur **{de(a.q, 3)}** des Optimums zusagt "
            f"(Rangquotient {de(a.q, 3)}). Mit anderen Gewichten, etwa den scharfen, liegt Greedy deutlich darunter."
        )
    near = " Das ist fast die schlechteste mögliche Lage." if a.ratio - a.q <= 0.01 else ""
    return "warning", (
        f"Greedy erreicht Gewicht {gewicht(a.greedy_value)} von {gewicht(a.opt_value)}: **{prozent(a.ratio)} %** des Optimums. "
        f"Die Garantie sagt: mindestens {prozent(a.q)} % (Rangquotient {de(a.q, 3)}).{near}"
    )


def rank_text(a: Analysis) -> str:
    """Beschreibung der schlimmsten Teilmenge F*."""
    if a.f_star == 0:
        return "Es gibt nichts zu prüfen: Die Grundmenge hat kein zulässiges Element."
    size = popcount(a.f_star)
    if a.q >= 1 - EPS:
        return (
            f"Rangquotient **1**: In jeder Teilmenge F der Grundmenge haben alle maximalen zulässigen Teilmengen dieselbe Größe "
            f"(zum Beispiel in F = {names(a, a.f_star)}: überall {a.lr}). Das ist die Eigenschaft eines Matroids."
        )
    return (
        f"Schlimmste Teilmenge F = {{{names(a, a.f_star)}}} ({size} Elemente): Die kleinste **maximale** zulässige Teilmenge hat {a.lr} "
        f"({{{names(a, a.low_mask)}}}), die größte zulässige Teilmenge {a.ur} ({{{names(a, a.high_mask)}}}). "
        f"Rangquotient q = {a.lr} / {a.ur} = **{de(a.q, 3)}**."
    )


# --- im Schnitt gegen im schlimmsten Fall --------------------------------------------------------------------------------------------


def ratio_distribution(settings: Settings, runs: int = C.DISTRIBUTION_RUNS) -> dict:
    """Verhältnis Greedy / Optimum über `runs` zufällige Gewichtsvektoren (Gleichverteilung zwischen 0 und 1, bei ganzen Zahlen 1 bis 3)."""
    sys_ = get_system(settings.system, settings.n, settings.seed)
    rng = random.Random(settings.wseed * 1000003 + 17)
    integer = settings.gewichte == "ganz"
    ws = [[float(rng.randint(1, 3)) if integer else max(0.001, round(rng.random(), 3)) for _ in range(sys_.m)] for _ in range(runs)]
    opts = sys_.opt_batch([[ws[b][e] for b in range(runs)] for e in range(sys_.m)])
    ratios = []
    for b, w in enumerate(ws):
        ratios.append(sys_.value(sys_.greedy(w), w) / float(opts[b]))
    return {
        "ratios": tuple(ratios), "q": sys_.q, "runs": runs, "integer": integer,
        "mean": sum(ratios) / runs, "min": min(ratios),
        "nonopt": sum(r < 1 - EPS for r in ratios), "violations": sum(r < sys_.q - EPS for r in ratios),
    }


def verdict_distribution(d: dict) -> tuple[str, str]:
    what = "ganzen Zahlen 1 bis 3" if d["integer"] else "Gewichten zwischen 0 und 1"
    if d["violations"]:
        return "error", f"Bei {d['violations']} von {d['runs']} Gewichtsvektoren liegt Greedy unter der Garantie q = {de(d['q'], 3)}. Das darf nicht sein: Rechenfehler."
    if d["q"] >= 1 - EPS:
        return "success", f"Bei {d['runs']} zufälligen Gewichtsvektoren aus {what} ist Greedy in **allen** Läufen optimal (Rangquotient 1)."
    return "info", (
        f"Bei {d['runs']} zufälligen Gewichtsvektoren aus {what}: Greedy ist in {d['nonopt']} Läufen ({prozent(d['nonopt'] / d['runs'])} %) nicht optimal, "
        f"im Mittel erreicht es **{prozent(d['mean'])} %** des Optimums, im schlechtesten Lauf {prozent(d['min'])} %. "
        f"Die Garantie q = {de(d['q'], 3)} wird nie unterschritten; sie ist der Wert im schlimmsten Fall (scharfe Gewichte), nicht der typische."
    )


# --- maximal gegen größtmöglich ------------------------------------------------------------------------------------------------------


def maximal_stats(settings: Settings) -> dict:
    sys_ = get_system(settings.system, settings.n, settings.seed)
    sizes = sys_.maximal_sizes()
    return {"sizes": sizes, "total": sum(sizes.values()), "lr": min(sizes), "ur": max(sizes)}


def verdict_maximal(stats: dict) -> tuple[str, str]:
    sizes = stats["sizes"]
    if len(sizes) == 1:
        (size, count), = sizes.items()
        return "info", (
            f"Alle {count} maximalen zulässigen Mengen haben dieselbe Größe {size}: Für die **ganze** Grundmenge verhält sich das System wie ein Matroid. "
            "Die Garantie hängt aber an allen Teilmengen (Experiment 2), nicht nur an der ganzen Grundmenge."
        )
    parts = ", ".join(f"{count} mit {size}" for size, count in sizes.items())
    return "warning", (
        f"{stats['total']} maximale zulässige Mengen: {parts} Elementen. Für jede gibt es Gewichte, bei denen Greedy genau diese Menge liefert. "
        f"Die Mengen mit {stats['lr']} Elementen sind maximal, aber nicht größtmöglich (die größte hat {stats['ur']})."
    )


def greedy_can_return(settings: Settings, mask: int):
    """Gewichte, bei denen Greedy genau `mask` liefert (Elemente von mask schwer, der Rest leicht), und das Ergebnis."""
    sys_ = get_system(settings.system, settings.n, settings.seed)
    w = [2.0 if mask >> e & 1 else 1.0 for e in range(sys_.m)]
    return w, sys_.greedy(w)


# --- Skalierung des Rangquotienten ---------------------------------------------------------------------------------------------------


def scaling_rows() -> list[dict]:
    rows = []
    for k in C.SCALING_STAR:
        s = star_system(k)
        rows.append({"family": "Stern (unabhängige Menge)", "size": k, "q": s.q, "lr": s.lr[s.f_star], "ur": s.ur[s.f_star]})
    for e in C.SCALING_PATH:
        s = path_matching_system(e)
        rows.append({"family": "Paarung auf einem Pfad", "size": e, "q": s.q, "lr": s.lr[s.f_star], "ur": s.ur[s.f_star]})
    for k in C.SCALING_KNAPSACK:
        s = knapsack_big_system(k)
        rows.append({"family": "Rucksack mit einem großen Gegenstand", "size": k, "q": s.q, "lr": s.lr[s.f_star], "ur": s.ur[s.f_star]})
    return rows


def verdict_scaling(rows: list[dict]) -> tuple[str, str]:
    by = {}
    for r in rows:
        by.setdefault(r["family"], []).append(r)
    star = by["Stern (unabhängige Menge)"]
    path = by["Paarung auf einem Pfad"]
    knap = by["Rucksack mit einem großen Gegenstand"]
    star_ok = all(abs(r["q"] - 1.0 / r["size"]) < 1e-12 for r in star)
    path_vals = sorted({round(r["q"], 6) for r in path if r["size"] >= 3})
    knap_ok = all(abs(r["q"] - 1.0 / r["size"]) < 1e-12 for r in knap)
    if not (star_ok and knap_ok and path_vals == [0.5]):
        return "warning", "Die Rangquotienten folgen nicht dem erwarteten Muster."
    return "info", (
        f"Beim Stern ist q = 1/k bei allen {len(star)} Größen (k = {star[0]['size']} bis {star[-1]['size']}), beim Rucksack mit einem großen Gegenstand ebenfalls (k = {knap[0]['size']} bis {knap[-1]['size']}): "
        f"der Quotient kann beliebig klein werden. Die Paarung auf einem Pfad hat bei 3 bis 11 Kanten q = 1/2 (nach dem bekannten Satz für Paarungen allgemein; bei 2 Kanten q = {de(path[0]['q'], 0)})."
    )


# --- Spielwiese ---------------------------------------------------------------------------------------------------------------------


def play_result(settings: Settings, weights) -> dict:
    sys_ = get_system(settings.system, settings.n, settings.seed)
    g = sys_.greedy(weights)
    ov, om = sys_.opt(weights)
    gv = sys_.value(g, weights)
    return {"greedy_mask": g, "opt_mask": om, "greedy_value": gv, "opt_value": ov, "ratio": gv / ov if ov > 0 else 1.0, "q": sys_.q}


def verdict_play(r: dict) -> tuple[str, str]:
    if r["opt_value"] <= 0:
        return "info", "Alle Gewichte sind 0: Greedy und Optimum haben beide Gewicht 0."
    if r["ratio"] >= 1 - EPS:
        return "success", f"Greedy trifft das Optimum (Gewicht {gewicht(r['greedy_value'])})."
    return "warning", f"Greedy erreicht {gewicht(r['greedy_value'])} von {gewicht(r['opt_value'])}: {prozent(r['ratio'])} % des Optimums (Garantie mindestens {prozent(r['q'])} %)."
