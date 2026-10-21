"""Experimente über feste Netze (nie ein einzelner Zufalls-Seed als Befund). Jede Funktion gibt eine Liste von Zeilen (dict) zurück; Verdikte und Abbildungen lesen nur diese Zeilen.

1. `exact_rows`: Preis des Zusammenhangs bei k = 2 (alle ausgewogenen Zweiteilungen aufgezählt).
2. `split_rows`: wie oft zerfallen Gebiete der rekursiven Bisektion (je Netztyp und k)?
3. `repair_rows`: was kostet das Umhängen der Inseln und der Ausgleich (Schnitt, größtes Gebiet, Erfolg)?
4. `grow_rows`: Bezirkswachstum gegen Bisektion mit Reparatur.
Experimente 2 bis 4 teilen die Läufe auf denselben festen Netzen (`_runs`)."""

from functools import lru_cache

import geb_algorithm as A
import geb_constants as C
import geb_evaluation as ev
import geb_scenario as S


def kind_label(kind, deg):
    name = C.KIND_NAMES[kind]
    return f"{name}, Grad {deg:g}".replace(".", ",") if kind in ("random", "verbund") else name


@lru_cache(maxsize=None)
def _runs(kind, deg, k, seed):
    """Die Analyse eines festen Netzes mit EX_N Standorten (Spielraum DEFAULT_DELTA); mehrere Experimente teilen sie."""
    return ev.analyse(ev.Settings(kind=kind, n=C.EX_N, deg=deg if deg else C.DEFAULT_DEG, links=1, seed=seed, k=k, delta=C.DEFAULT_DELTA))


def _each(k):
    for kind, deg in C.EX_KINDS:
        yield kind, deg, [_runs(kind, deg, k, s) for s in C.SWEEP_SEEDS]


def exact_best(n, pairs, k_delta=C.DEFAULT_DELTA):
    """Kleinster Schnitt über alle ausgewogenen Zweiteilungen und über die, deren beide Hälften zusammenhängen: (beste Zahl, beste Zahl mit Zusammenhang). Standort n - 1 liegt immer in Hälfte 0."""
    lim = A.part_limit(n, 2, k_delta)
    adj = [0] * n
    for u, v in pairs:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    full = (1 << n) - 1

    def connected(mask):
        if mask == 0:
            return False
        seen = mask & -mask
        frontier = seen
        while frontier:
            low = frontier & -frontier
            frontier ^= low
            new = adj[low.bit_length() - 1] & mask & ~seen
            seen |= new
            frontier |= new
        return seen == mask
    best_any = best_conn = None
    for mask in range(1, 1 << (n - 1)):
        size = bin(mask).count("1")
        if size > lim or n - size > lim:
            continue
        other = full & ~mask
        cut, m = 0, mask
        while m:
            low = m & -m
            m ^= low
            cut += bin(adj[low.bit_length() - 1] & other).count("1")
        if best_any is None or cut < best_any:
            best_any = cut
        if (best_conn is None or cut < best_conn) and connected(mask) and connected(other):
            best_conn = cut
    return best_any, best_conn


def exact_rows():
    rows = []
    for kind, deg in C.EX_KINDS:
        sum_opt = sum_conn = differ = 0
        for seed in C.EX_EXACT_SEEDS:
            inst = S.make_instance(kind, C.EX_EXACT_N, deg if deg else C.DEFAULT_DEG, 1, seed)
            any_, conn = exact_best(inst.n, inst.pairs)
            sum_opt += any_
            sum_conn += conn
            differ += conn > any_
        rows.append({"kind": kind, "label": kind_label(kind, deg), "n": inst_n(kind), "nets": len(C.EX_EXACT_SEEDS), "differ": differ, "sum_opt": sum_opt, "sum_conn": sum_conn})
    return rows


def inst_n(kind):
    return S.make_instance(kind, C.EX_EXACT_N, 4.0, 1, C.EX_EXACT_SEEDS[0]).n


def split_rows():
    rows = []
    for k in C.EX_KS:
        for kind, deg, runs in _each(k):
            rb = [a.quality["rb"] for a in runs]
            rows.append({"kind": kind, "label": kind_label(kind, deg), "k": k, "n": C.EX_N, "nets": len(runs), "nets_split": sum(q.split_parts > 0 for q in rb), "parts": k * len(runs),
                         "parts_split": sum(q.split_parts for q in rb), "island_nodes": sum(q.island_nodes for q in rb), "sum_cut": sum(q.cut for q in rb)})
    return rows


def repair_rows():
    rows = []
    for k in C.EX_KS:
        if k == 2:
            continue
        for kind, deg, runs in _each(k):
            q = {key: [a.quality[key] for a in runs] for key in ("rb", "rep", "bal")}
            rows.append({"kind": kind, "label": kind_label(kind, deg), "k": k, "n": C.EX_N, "nets": len(runs), "nets_split": sum(x.split_parts > 0 for x in q["rb"]),
                         "ok_rep": sum(x.ok for x in q["rep"]), "ok_bal": sum(x.ok for x in q["bal"]),
                         **{f"sum_cut_{key}": sum(x.cut for x in q[key]) for key in q}, **{f"sum_ratio_{key}": sum(x.ratio for x in q[key]) for key in q}})
    return rows


def grow_rows():
    rows = []
    for k in C.EX_KS:
        if k == 2:
            continue
        for kind, deg, runs in _each(k):
            both = [a for a in runs if a.quality["bal"].ok and a.quality["growbal"].ok]
            rows.append({"kind": kind, "label": kind_label(kind, deg), "k": k, "n": C.EX_N, "nets": len(runs), "ok_bal": sum(a.quality["bal"].ok for a in runs), "ok_growbal": sum(a.quality["growbal"].ok for a in runs),
                         "n_both": len(both), "sum_bal_both": sum(a.quality["bal"].cut for a in both), "sum_grow_both": sum(a.quality["growbal"].cut for a in both),
                         "sum_cut_grow": sum(a.quality["grow"].cut for a in runs), "sum_ratio_grow": sum(a.quality["grow"].ratio for a in runs)})
    return rows


def checks_rows():
    """Zeugnisse über alle Läufe: wie oft besteht `validate`?"""
    rows = []
    for k in C.EX_KS:
        for kind, deg, runs in _each(k):
            rows.append({"kind": kind, "label": kind_label(kind, deg), "k": k, "n": C.EX_N, "nets": len(runs), "wrong": sum(1 for a in runs if ev.validate(a))})
    return rows
