"""Gemeinsame Fixtures: kleine Systeme, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from uns_algorithm import System  # noqa: E402


@pytest.fixture
def paarung3():
    """Paarung auf einem Pfad mit 3 Kanten e0, e1, e2 (benachbarte Kanten schließen sich aus). Zulässig: ∅, {e0}, {e1}, {e2}, {e0, e2}.
    Maximal: {e1} (Größe 1) und {e0, e2} (Größe 2). F = alle: lr = 1, ur = 2, q = 1/2; jede echte Teilmenge hat lr = ur."""
    return System("Paarung auf Pfad", 3, [not (mask & 1 and mask & 2) and not (mask & 2 and mask & 4) for mask in range(8)])


@pytest.fixture
def stern4():
    """Zentrum 0 und 4 Blätter 1 bis 4: zulässig sind Mengen ohne das Zentrum mit beliebigen Blättern oder {0}. Maximal: {0} und {1, 2, 3, 4}. q = 1/4."""
    return System("Stern", 5, [not (mask & 1 and mask > 1) for mask in range(32)])


@pytest.fixture
def rucksack():
    """Größen (6, 3, 3), Kapazität 6: zulässig ∅, {0}, {1}, {2}, {1, 2}. Maximal: {0} (1) und {1, 2} (2). q = 1/2."""
    sizes = (6, 3, 3)
    return System("Rucksack", 3, [sum(sizes[e] for e in range(3) if mask >> e & 1) <= 6 for mask in range(8)])


@pytest.fixture
def uniform():
    """Uniformes Matroid U(2, 4): höchstens 2 von 4 Elementen. q = 1."""
    return System("U(2, 4)", 4, [bin(mask).count("1") <= 2 for mask in range(16)])
