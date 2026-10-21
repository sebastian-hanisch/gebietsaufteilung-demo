"""Kern: Teilen in k Gebiete, Prüfen des Zusammenhangs, Reparieren und Bezirkswachstum.

**Aufgabe:** Die Standorte eines Netzes in k Gebiete teilen, die **ausgewogen** (jedes höchstens ⌈(1 + δ) n / k⌉ Standorte) und **zusammenhängend** sind, mit möglichst wenigen Leitungen zwischen den Gebieten.

**Rekursive Bisektion:** wiederholt halbieren (Fiduccia–Mattheyses mit zufälligen Neustarts, Kern aus bisektion-demo und multilevel-partitionierung-demo); gut für den Schnitt, aber ein Gebiet kann in
mehrere Stücke zerfallen. **Reparatur:** Inseln umhängen (das kann ein Gebiet zu groß machen), dann zusammenhangswahrend ausgleichen und verbessern. **Bezirkswachstum:** k Keime, das kleinste Gebiet wächst um
den Nachbarn mit den meisten Leitungen: zusammenhängend von Anfang an, aber nicht ausgewogen und mit größerem Schnitt."""

import math
from dataclasses import dataclass

import geb_constants as C
import geb_scenario as S


@dataclass(frozen=True)
class WGraph:
    adj: tuple              # je Knoten ((Nachbar, Gewicht), ...) aufsteigend nach Nachbar
    vw: tuple               # Knotengewichte

    @property
    def n(self):
        return len(self.vw)

    @property
    def total(self):
        return sum(self.vw)

    @property
    def edge_total(self):
        return sum(w for a in self.adj for _u, w in a) // 2


def from_pairs(n, pairs):
    """Netz mit Knotengewicht 1 und Leitungsgewicht 1."""
    nb = [dict() for _ in range(n)]
    for u, v in pairs:
        nb[u][v] = 1
        nb[v][u] = 1
    return WGraph(tuple(tuple(sorted(d.items())) for d in nb), (1,) * n)


def cut_value(g, side):
    return sum(w for u in range(g.n) for v, w in g.adj[u] if u < v and side[u] != side[v])


def limit(total, eps):
    """Größtes erlaubtes Gewicht einer Hälfte: ⌈(1 + ε) · W / 2⌉ bei ε in Prozent, höchstens W − 1 (beide Hälften bleiben nichtleer)."""
    return min(int(math.ceil((1 + eps / 100.0) * total / 2 - 1e-9)), max(total - 1, 1))


def side_weights(g, side):
    w = [0, 0]
    for v in range(g.n):
        w[side[v]] += g.vw[v]
    return tuple(w)


def is_balanced(g, side, eps):
    return max(side_weights(g, side)) <= limit(g.total, eps)


# --- Fiduccia–Mattheyses mit Gewichten --------------------------------------------------------------------------------------------------------------


def gains(g, side):
    """Gewinn je Knoten: Leitungsgewicht nach außen minus nach innen (so viel sinkt der Schnitt, wenn der Knoten die Hälfte wechselt)."""
    return [sum(w if side[u] != side[v] else -w for u, w in g.adj[v]) for v in range(g.n)]


@dataclass(frozen=True)
class FMPass:
    moves: int              # Zahl der Züge (jeder Knoten höchstens einmal)
    best: int               # Länge des besten Anfangs der Zugfolge (0: nichts ausgeführt)
    gain: int
    cut_before: int
    cut_after: int


def fm_pass(g, side, eps):
    """Ein Durchlauf von FM auf einer Kopie: gibt (neue Hälften, Durchlauf) zurück."""
    n = g.n
    side = list(side)
    maxw = limit(g.total, eps)
    wt = list(side_weights(g, side))
    gain = gains(g, side)
    locked = [False] * n
    start_cut = cut = cut_value(g, side)
    best_cut, best_i = cut, 0
    moved = []
    for _ in range(n):
        pick, pg = -1, None
        for v in range(n):
            if locked[v] or wt[1 - side[v]] + g.vw[v] > maxw:
                continue
            if pg is None or gain[v] > pg:
                pick, pg = v, gain[v]
        if pick < 0:
            break
        v = pick
        cut -= gain[v]
        s = side[v]
        wt[s] -= g.vw[v]
        wt[1 - s] += g.vw[v]
        side[v] = 1 - s
        locked[v] = True
        gain[v] = -gain[v]
        for u, w in g.adj[v]:
            if not locked[u]:
                gain[u] += -2 * w if side[u] == side[v] else 2 * w
        moved.append(v)
        if cut < best_cut:
            best_cut, best_i = cut, len(moved)
    for v in reversed(moved[best_i:]):
        side[v] = 1 - side[v]
    return side, FMPass(len(moved), best_i, start_cut - best_cut, start_cut, best_cut)


@dataclass(frozen=True)
class Refined:
    side: tuple
    cut: int
    passes: tuple           # FMPass je Durchlauf (der letzte ohne Gewinn)
    moves: int


def fm(g, side, eps, max_passes=C.MAX_PASSES):
    """FM bis ein Durchlauf nichts mehr gewinnt (oder `max_passes` Durchläufe)."""
    side = list(side)
    passes = []
    for _ in range(max_passes):
        new, p = fm_pass(g, side, eps)
        passes.append(p)
        if p.gain <= 0:
            break
        side = new
    return Refined(tuple(side), cut_value(g, side), tuple(passes), sum(p.moves for p in passes))


def random_bisection(g, rng, eps=C.DEFAULT_EPS):
    """Zufällige Anordnung: Knoten in zufälliger Reihenfolge der Hälfte 0 zuweisen, solange sie höchstens das erlaubte Gewicht hat und noch nicht die Hälfte des Gesamtgewichts erreicht; reicht das nicht für
    die andere Hälfte, kommen weitere passende Knoten dazu. So sind beide Hälften erlaubt, wenn das überhaupt möglich ist (beide nichtleer)."""
    order = S._shuffle(range(g.n), rng)
    maxw = limit(g.total, eps)
    side = [1] * g.n
    w = 0
    for v in order:
        if w >= g.total / 2 and w > 0:
            break
        if w + g.vw[v] <= maxw or w == 0:
            side[v] = 0
            w += g.vw[v]
    for v in order:
        if g.total - w <= maxw:
            break
        if side[v] == 1 and w + g.vw[v] <= maxw:
            side[v] = 0
            w += g.vw[v]
    return side


@dataclass(frozen=True)
class SLResult:
    side: tuple
    cut: int
    starts: tuple           # Schnitte der einzelnen Starts
    moves: int


def single_level(g, eps, rng, budget):
    """Einstufig: zufällige Anordnungen mit FM verbessern, bis die Züge das Budget erreichen (mindestens ein Start); gibt den besten Start zurück."""
    best, starts, moves = None, [], 0
    while moves < budget or not starts:
        r = fm(g, random_bisection(g, rng, eps), eps)
        moves += max(r.moves, 1)                  # ein Start ohne möglichen Zug (zwei Standorte) zählt als ein Zug, sonst endete die Schleife nie
        starts.append(r.cut)
        if best is None or r.cut < best.cut:
            best = r
    return SLResult(best.side, best.cut, tuple(starts), moves)


# --- Gebiete: Teilen, Prüfen, Reparieren, Wachsen ----------------------------------------------------------------------------------------------------


def part_limit(n, k, delta):
    """Größtes erlaubtes Gebiet: ⌈(1 + δ) · n / k⌉ bei δ in Prozent."""
    return int(math.ceil((1 + delta / 100.0) * n / k - 1e-9))


def induced(g, nodes):
    """Teilnetz auf `nodes` (neue Nummern in der Reihenfolge von `nodes`), alle Gewichte 1."""
    idx = {v: i for i, v in enumerate(nodes)}
    pairs = [(idx[u], idx[v]) for u in nodes for v, _w in g.adj[u] if v in idx and u < v]
    return from_pairs(len(nodes), pairs)


def bisect(g, nodes, rng):
    """Halbiert `nodes` (aufsteigend) mit FM und zufälligen Neustarts: gibt (Hälfte 0, Hälfte 1) als Listen zurück."""
    sub = induced(g, nodes)
    r = single_level(sub, C.BISECT_EPS, rng, C.START_BUDGET * sub.n)
    return [v for i, v in enumerate(nodes) if r.side[i] == 0], [v for i, v in enumerate(nodes) if r.side[i] == 1]


def recursive_bisection(g, k, rng):
    """k Gebiete (k eine Zweierpotenz) durch wiederholtes Halbieren: gibt für jeden Standort die Nummer seines Gebiets zurück (0 bis k - 1, in der Reihenfolge des Halbierens)."""
    def split(nodes, parts):
        if parts == 1:
            return [nodes]
        a, b = bisect(g, nodes, rng)
        return split(a, parts // 2) + split(b, parts // 2)
    label = [-1] * g.n
    for i, members in enumerate(split(list(range(g.n)), k)):
        for v in members:
            label[v] = i
    return tuple(label)


def components(g, nodes):
    """Zusammenhangskomponenten des Teilnetzes auf `nodes`: Listen aufsteigender Standorte, die größte zuerst (bei Gleichstand die mit dem kleinsten Standort)."""
    inside = set(nodes)
    seen, out = set(), []
    for s in sorted(inside):
        if s in seen:
            continue
        comp, stack = [], [s]
        seen.add(s)
        while stack:
            v = stack.pop()
            comp.append(v)
            for u, _w in g.adj[v]:
                if u in inside and u not in seen:
                    seen.add(u)
                    stack.append(u)
        out.append(sorted(comp))
    out.sort(key=lambda c: (-len(c), c[0]))
    return out


def members(label, k):
    return [[v for v in range(len(label)) if label[v] == i] for i in range(k)]


def sizes(label, k):
    return tuple(sum(1 for x in label if x == i) for i in range(k))


def islands(g, label, k):
    """Standorte, die nicht in der größten Komponente ihres Gebiets liegen (aufsteigend)."""
    out = []
    for part in members(label, k):
        for comp in components(g, part)[1:]:
            out += comp
    return sorted(out)


def attach_islands(g, label, k):
    """Jede Insel (Komponente außer der größten) als Ganzes an das Nachbargebiet mit den meisten Leitungen zur Insel hängen (bei Gleichstand das mit der kleineren Nummer), bis jedes Gebiet zusammenhängt.
    Gibt (neue Gebiete, Zahl der umgehängten Standorte) zurück. Jeder Schritt verbindet die Insel mit einer Komponente des Zielgebiets, die Zahl aller Komponenten sinkt also bei jedem Schritt: das Verfahren endet."""
    label = list(label)
    moved = 0
    while True:
        done = True
        for i in range(k):
            comps = components(g, [v for v in range(g.n) if label[v] == i])
            for comp in comps[1:]:
                count = {}
                for v in comp:
                    for u, w in g.adj[v]:
                        if label[u] != i:
                            count[label[u]] = count.get(label[u], 0) + w
                target = min(count, key=lambda j: (-count[j], j))
                for v in comp:
                    label[v] = target
                moved += len(comp)
                done = False
        if done:
            return tuple(label), moved


def stays_connected(g, label, v):
    """Bleibt das Gebiet von `v` ohne `v` nichtleer und zusammenhängend?"""
    rest = [u for u in range(g.n) if label[u] == label[v] and u != v]
    return bool(rest) and len(components(g, rest)) == 1


def _counts(g, label, v):
    count = {}
    for u, w in g.adj[v]:
        count[label[u]] = count.get(label[u], 0) + w
    return count


def rebalance(g, label, k, lim):
    """Zu große Gebiete verkleinern: wiederholt den Randstandort eines zu großen Gebiets mit dem größten Gewinn (Leitungen zum Ziel minus zum eigenen Gebiet, bei Gleichstand der kleinere Standort)
    in ein Nachbargebiet verschieben, das danach höchstens `lim` Standorte hat, und nur, wenn das Quellgebiet zusammenhängend bleibt. Gibt (neue Gebiete, ausgewogen?) zurück; ohne zulässigen Zug endet es unausgewogen."""
    label = list(label)
    size = list(sizes(label, k))
    for _ in range(10 * g.n):
        if max(size) <= lim:
            return tuple(label), True
        best = None
        for v in range(g.n):
            i = label[v]
            if size[i] <= lim:
                continue
            count = _counts(g, label, v)
            for j in sorted(count):
                if j == i or size[j] + 1 > lim:
                    continue
                key = (count[j] - count.get(i, 0), -v)
                if best is None or key > best[0]:
                    if stays_connected(g, label, v):
                        best = (key, v, j)
        if best is None:
            return tuple(label), False
        _key, v, j = best
        size[label[v]] -= 1
        size[j] += 1
        label[v] = j
    return tuple(label), max(size) <= lim


def polish(g, label, k, lim, passes=C.POLISH_PASSES):
    """Schnitt verkleinern: Standorte in aufsteigender Reihenfolge in das Nachbargebiet mit dem größten positiven Gewinn verschieben, wenn das Ziel danach höchstens `lim` Standorte hat und das Quellgebiet
    zusammenhängend bleibt; so lange, bis ein Durchlauf nichts mehr verschiebt (höchstens `passes` Durchläufe)."""
    label = list(label)
    size = list(sizes(label, k))
    for _ in range(passes):
        moved = False
        for v in range(g.n):
            i = label[v]
            count = _counts(g, label, v)
            best, target = 0, None
            for j in sorted(count):
                if j == i or size[j] + 1 > lim:
                    continue
                if count[j] - count.get(i, 0) > best:
                    best, target = count[j] - count.get(i, 0), j
            if target is not None and stays_connected(g, label, v):
                size[i] -= 1
                size[target] += 1
                label[v] = target
                moved = True
        if not moved:
            break
    return tuple(label)


def seeds(g, k, rng):
    """k Keime: der erste zufällig, jeder weitere der Standort mit der größten Entfernung (Leitungen) zu den bisherigen (bei Gleichstand der kleinere)."""
    first = S._below(rng, g.n)
    chosen = [first]
    near = _distances(g, first)
    while len(chosen) < k:
        s = max(range(g.n), key=lambda v: (near[v], -v))
        chosen.append(s)
        d = _distances(g, s)
        near = [min(a, b) for a, b in zip(near, d)]
    return tuple(chosen)


def _distances(g, s):
    dist = [-1] * g.n
    dist[s] = 0
    queue = [s]
    for v in queue:
        for u, _w in g.adj[v]:
            if dist[u] < 0:
                dist[u] = dist[v] + 1
                queue.append(u)
    return [d if d >= 0 else g.n for d in dist]


def grow(g, k, rng):
    """Bezirkswachstum: k Keime; das jeweils kleinste Gebiet (bei Gleichstand die kleinere Nummer) nimmt den freien Nachbarn mit den meisten Leitungen zu sich. Jedes Gebiet bleibt zusammenhängend,
    weil es nur um Nachbarn wächst; gibt für jeden Standort die Nummer seines Gebiets zurück."""
    label = [-1] * g.n
    size = [0] * k
    front = [dict() for _ in range(k)]

    def take(v, i):
        label[v] = i
        size[i] += 1
        for f in front:
            f.pop(v, None)
        for u, w in g.adj[v]:
            if label[u] < 0:
                front[i][u] = front[i].get(u, 0) + w
    for i, s in enumerate(seeds(g, k, rng)):
        take(s, i)
    for _ in range(g.n - k):
        for i in sorted(range(k), key=lambda j: (size[j], j)):
            if front[i]:
                v = min(front[i], key=lambda u: (-front[i][u], u))
                take(v, i)
                break
        else:
            break
    return tuple(label)
