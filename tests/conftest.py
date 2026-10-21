"""Gemeinsame Fixtures: Hilfsfunktionen und Mini-Netze, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Teure Experimente laufen einmal je Testlauf (`lru_cache`) und werden von Claims-, Verdikt- und Branch-Tests gemeinsam genutzt."""

import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class FixedRandom:
    """Liefert immer fast 1: Fisher–Yates lässt die Reihenfolge unverändert (Identität), `random_bisection` füllt Hälfte 0 mit den ersten Knoten, `_below` liefert den letzten Index."""

    def random(self):
        return 0.999999


def graph(n, pairs):
    import geb_algorithm as A
    return A.from_pairs(n, pairs)


def path(n):
    return graph(n, [(v, v + 1) for v in range(n - 1)])


@lru_cache(maxsize=None)
def cached(name):
    """Einmal je Testlauf berechnete Experimente (Name der Funktion in geb_experiments)."""
    import geb_experiments as ex
    return getattr(ex, name)()
