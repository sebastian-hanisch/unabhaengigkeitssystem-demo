"""Kern der Demo: Unabhängigkeitssysteme auf höchstens 16 Elementen (Bitmasken), Greedy, Optimum durch Aufzählen und der Rangquotient.

Ein Unabhängigkeitssystem ist eine nach unten abgeschlossene Familie von Teilmengen einer Grundmenge: mit jeder zulässigen Menge sind auch
alle ihre Teilmengen zulässig. Elemente sind Zahlen 0 .. m − 1, eine Menge ist die Bitmaske `sum(1 << e)`.

ur(F) = Größe der größten zulässigen Teilmenge von F, lr(F) = Größe der kleinsten MAXIMALEN zulässigen Teilmenge von F.
Rangquotient q = min über F mit ur(F) > 0 von lr(F) / ur(F). Greedy (Maximierung) erreicht mindestens q mal das Optimum; die Schranke ist scharf."""

import numpy as np


def popcount(x: int) -> int:
    return bin(x).count("1")


def elements(mask: int, m: int) -> list[int]:
    return [e for e in range(m) if mask >> e & 1]


class System:
    """Unabhängigkeitssystem auf m Elementen; ok[mask] sagt, ob die Menge `mask` zulässig ist."""

    def __init__(self, name: str, m: int, ok):
        if not 1 <= m <= 16:
            raise ValueError(f"m = {m} außerhalb von 1 bis 16")
        if len(ok) != 1 << m or not ok[0]:
            raise ValueError("ok braucht 2**m Einträge, und die leere Menge muss zulässig sein")
        self.name, self.m, self.ok = name, m, list(ok)
        self.full = (1 << m) - 1
        self.ind = [mask for mask in range(1 << m) if self.ok[mask]]
        self.ind_matrix = np.array([[mask >> e & 1 for e in range(m)] for mask in self.ind], dtype=float)
        self._ranks()

    # --- Eigenschaften ----------------------------------------------------------------------------------------------------------------

    def check_down_closed(self) -> bool:
        """Mit jeder zulässigen Menge sind alle Mengen ohne ein Element zulässig (genügt für alle Teilmengen)."""
        return all(self.ok[mask & ~(1 << e)] for mask in self.ind for e in range(self.m) if mask >> e & 1)

    def can_add(self, mask: int, e: int) -> bool:
        return not mask >> e & 1 and self.ok[mask | 1 << e]

    def is_maximal(self, mask: int) -> bool:
        """Zulässig, und kein weiteres Element lässt sich hinzufügen."""
        return self.ok[mask] and not any(self.can_add(mask, e) for e in range(self.m))

    def _ranks(self):
        m, ok = self.m, self.ok
        ur = [0] * (1 << m)
        for mask in range(1, 1 << m):
            ur[mask] = popcount(mask) if ok[mask] else max(ur[mask & ~(1 << e)] for e in range(m) if mask >> e & 1)
        lr = [0] * (1 << m)
        for i in sorted(self.ind, key=popcount):           # kleinste zuerst: die erste Zuweisung ist das Minimum
            addable = 0
            for e in range(m):
                if self.can_add(i, e):
                    addable |= 1 << e
            free = self.full & ~i & ~addable                # i ist maximal in jeder Menge F mit i ⊆ F ⊆ ~addable
            s = free
            while True:
                f = i | s
                if f and lr[f] == 0:
                    lr[f] = popcount(i)
                if s == 0:
                    break
                s = (s - 1) & free
        self.ur, self.lr = ur, lr
        best = None
        for f in range(1, 1 << m):
            if ur[f] > 0:
                q = lr[f] / ur[f]
                if best is None or q < best[0] - 1e-15:
                    best = (q, f)
        self.q, self.f_star = best if best else (1.0, 0)

    def maximal_sizes(self) -> dict[int, int]:
        """Zahl der maximalen zulässigen Mengen je Größe (der Reihe nach aufsteigend)."""
        sizes: dict[int, int] = {}
        for i in self.ind:
            if self.is_maximal(i):
                sizes[popcount(i)] = sizes.get(popcount(i), 0) + 1
        return dict(sorted(sizes.items()))

    # --- Greedy und Optimum -----------------------------------------------------------------------------------------------------------

    def greedy(self, w) -> int:
        """Elemente nach Gewicht absteigend (bei Gleichstand der kleinere Index), jedes nehmen, das zulässig bleibt."""
        order = sorted(range(self.m), key=lambda e: (-w[e], e))
        mask = 0
        for e in order:
            if self.can_add(mask, e):
                mask |= 1 << e
        return mask

    def value(self, mask: int, w) -> float:
        return sum(w[e] for e in range(self.m) if mask >> e & 1)

    def opt(self, w) -> tuple[float, int]:
        """Größtes Gewicht einer zulässigen Menge und eine Menge, die es erreicht (bei Gleichstand die zuerst aufgezählte)."""
        values = self.ind_matrix @ np.asarray(w, dtype=float)
        i = int(np.argmax(values))
        return float(values[i]), self.ind[i]

    def opt_batch(self, W) -> np.ndarray:
        """W: m × B Gewichte; das Optimum je Spalte."""
        return (self.ind_matrix @ np.asarray(W, dtype=float)).max(axis=0)

    # --- scharfe Gewichte -------------------------------------------------------------------------------------------------------------

    def smallest_maximal_in_f_star(self) -> int:
        """Eine kleinste maximale zulässige Teilmenge der schlimmsten Menge F* (Größe lr(F*))."""
        f, target = self.f_star, self.lr[self.f_star]
        for i in self.ind:
            if i & ~f == 0 and popcount(i) == target and all(not self.can_add(i, e) for e in range(self.m) if f >> e & 1):
                return i
        raise AssertionError("keine kleinste maximale Teilmenge gefunden")

    def largest_in_f_star(self) -> int:
        """Eine größte zulässige Teilmenge von F* (Größe ur(F*))."""
        f, target = self.f_star, self.ur[self.f_star]
        for i in self.ind:
            if i & ~f == 0 and popcount(i) == target:
                return i
        raise AssertionError("keine größte Teilmenge gefunden")

    def sharp_weights(self, delta: float = 0.001) -> list[float]:
        """Gewichte, bei denen Greedy nur etwa q mal das Optimum erreicht: 1 + delta auf einer kleinsten maximalen Teilmenge von F*,
        1 auf dem Rest von F*, 0 sonst. Bei q = 1 (Matroid) sind das einfach Gewichte auf F*, Greedy bleibt optimal."""
        if self.f_star == 0:
            return [1.0] * self.m
        low = self.smallest_maximal_in_f_star()
        return [(1.0 + delta if low >> e & 1 else 1.0) if self.f_star >> e & 1 else 0.0 for e in range(self.m)]
