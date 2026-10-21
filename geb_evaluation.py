"""Kennzahlen, Prüfung der Ergebnisse und Verdikte. Verdikte sind reine Funktionen (Art, Text): Zahlen kommen aus den Zeilen, nie aus dem Text.

Standorte sind in der Anzeige ab 1 nummeriert (`inst.name`), im Kern ab 0."""

from dataclasses import dataclass, field

import geb_algorithm as A
import geb_constants as C
import geb_scenario as S


@dataclass(frozen=True)
class Settings:
    kind: str = C.DEFAULT_KIND
    n: int = C.DEFAULT_N
    deg: float = C.DEFAULT_DEG
    links: int = C.DEFAULT_LINKS
    seed: int = C.DEFAULT_SEED
    k: int = C.DEFAULT_K
    delta: int = C.DEFAULT_DELTA


def run_rng(seed, salt=0):
    """Zufallsquelle: Salz 0 für das Halbieren, 1 für die Keime des Bezirkswachstums."""
    return S.make_rng(seed * 53 + 4242, salt)


@dataclass(frozen=True)
class Quality:
    cut: int                 # Leitungen zwischen verschiedenen Gebieten
    sizes: tuple             # Standorte je Gebiet
    ratio: float             # größtes Gebiet geteilt durch das Ideal n / k
    split_parts: int         # Gebiete, die aus mehreren Stücken bestehen
    island_nodes: int        # Standorte außerhalb der größten Komponente ihres Gebiets
    balanced: bool           # größtes Gebiet höchstens ⌈(1 + δ) n / k⌉
    connected: bool          # jedes Gebiet zusammenhängend

    @property
    def ok(self):
        return self.balanced and self.connected


def quality(g, label, k, lim) -> Quality:
    sz = A.sizes(label, k)
    comps = [len(A.components(g, part)) for part in A.members(label, k)]
    isl = A.islands(g, label, k)
    return Quality(A.cut_value(g, label), sz, max(sz) * k / g.n, sum(1 for c in comps if c > 1), len(isl), max(sz) <= lim, all(c == 1 for c in comps))


STAGES = (
    ("rb", "Rekursive Bisektion"),
    ("rep", "Inseln umhängen"),
    ("bal", "… und ausgleichen"),
    ("grow", "Bezirkswachstum"),
    ("growbal", "… und ausgleichen"),
)
STAGE_LONG = {
    "rb": "Rekursive Bisektion",
    "rep": "Bisektion, Inseln umgehängt",
    "bal": "Bisektion, Inseln umgehängt und ausgeglichen",
    "grow": "Bezirkswachstum",
    "growbal": "Bezirkswachstum, ausgeglichen",
}


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    inst: S.Instance = field(compare=False, repr=False)
    graph: A.WGraph = field(compare=False, repr=False)
    limit: int
    labels: dict = field(compare=False, repr=False)         # Schlüssel aus STAGES -> Gebiet je Standort
    quality: dict = field(compare=False, repr=False)        # Schlüssel -> Quality
    moved: int = 0                                          # beim Umhängen der Inseln bewegte Standorte
    bal_ok: bool = True                                     # erreicht der Ausgleich der Bisektion die Grenze?
    growbal_ok: bool = True
    seeds: tuple = ()

    @property
    def n(self):
        return self.graph.n

    @property
    def m(self):
        return self.inst.m


def repair_pipeline(g, label, k, lim):
    """Umhängen der Inseln, dann zusammenhangswahrend ausgleichen und verbessern: (umgehängt, ausgeglichen, bewegte Standorte, Grenze erreicht?)."""
    rep, moved = A.attach_islands(g, label, k)
    bal, ok = A.rebalance(g, rep, k, lim)
    return rep, A.polish(g, bal, k, lim), moved, ok


def analyse(settings: Settings) -> Analysis:
    inst = S.make_instance(settings.kind, settings.n, settings.deg, settings.links, settings.seed)
    g = A.from_pairs(inst.n, inst.pairs)
    k = settings.k
    lim = A.part_limit(g.n, k, settings.delta)
    rb = A.recursive_bisection(g, k, run_rng(settings.seed))
    rep, bal, moved, bal_ok = repair_pipeline(g, rb, k, lim)
    gr = A.grow(g, k, run_rng(settings.seed, 1))
    grb, growbal_ok = A.rebalance(g, gr, k, lim)
    grb = A.polish(g, grb, k, lim)
    labels = {"rb": rb, "rep": rep, "bal": bal, "grow": gr, "growbal": grb}
    quals = {key: quality(g, lab, k, lim) for key, lab in labels.items()}
    return Analysis(settings, inst, g, lim, labels, quals, moved, bal_ok, growbal_ok, A.seeds(g, k, run_rng(settings.seed, 1)))


def validate(a: Analysis) -> list:
    """Unabhängige Prüfung vor der Anzeige: gibt die Liste der Probleme zurück (leer = alles in Ordnung)."""
    problems = []
    g, k = a.graph, a.settings.k
    for key, label in a.labels.items():
        if len(label) != g.n or any(not 0 <= x < k for x in label) or min(A.sizes(label, k)) < 1:
            problems.append(f"{STAGE_LONG[key]}: Standorte ohne Gebiet oder ein leeres Gebiet")
            return problems
    for key, q in a.quality.items():
        label = a.labels[key]
        if q.cut != A.cut_value(g, label) or q.sizes != A.sizes(label, k) or sum(q.sizes) != g.n:
            problems.append(f"{STAGE_LONG[key]}: Schnitt oder Größen stimmen nicht mit der Nachzählung überein")
            return problems
    if not all(a.quality[key].connected for key in ("rep", "bal", "grow", "growbal")):
        problems.append("Ein repariertes Ergebnis oder das Bezirkswachstum hat ein unzusammenhängendes Gebiet")
    if a.quality["rb"].split_parts != sum(1 for part in A.members(a.labels["rb"], k) if len(A.components(g, part)) > 1):
        problems.append("Zahl der zerfallenen Gebiete stimmt nicht")
    if a.quality["bal"].balanced != a.bal_ok or a.quality["growbal"].balanced != a.growbal_ok:
        problems.append("Der Ausgleich meldet die Grenze anders, als die Nachzählung sie findet")
    return problems


# --- Formate ---------------------------------------------------------------------------------------------------------------------------------------


def _i(x) -> str:
    """Ganze Zahl mit Punkt als Tausendertrenner."""
    return f"{x:,.0f}".replace(",", ".")


def _dec(x, digits=1) -> str:
    """Zahl mit Komma; ganze Werte ohne Nachkommastelle."""
    x = float(x)
    if x == int(x):
        return _i(x)
    return f"{x:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _of(k, n) -> str:
    return f"{_i(k)} von {_i(n)}"


def _gebiete(c) -> str:
    return "1 Gebiet" if c == 1 else f"{_i(c)} Gebiete"


# --- Verdikte -------------------------------------------------------------------------------------------------------------------------------------


def verdict_run(a: Analysis):
    """Kernfrage: Sind die Gebiete der Bisektion zusammenhängend, und was kostet das Reparieren?"""
    s = a.settings
    rb, rep, bal, gr, gb = (a.quality[x] for x in ("rb", "rep", "bal", "grow", "growbal"))
    k = s.k
    if rb.split_parts == 0:
        head = (f"**Bei {_i(a.n)} Standorten und {k} Gebieten ist jedes Gebiet der Bisektion zusammenhängend** (Schnitt {_i(rb.cut)}, größtes Gebiet das {_dec(rb.ratio, 2)}-Fache des Ideals): Hier fehlt nichts zu reparieren.")
    else:
        head = (f"**Bei {_i(a.n)} Standorten sind {_i(rb.split_parts)} der {_i(k)} Gebiete der Bisektion nicht zusammenhängend** ({_i(rb.island_nodes)} Standorte liegen in Inseln; Schnitt {_i(rb.cut)}, "
                f"größtes Gebiet das {_dec(rb.ratio, 2)}-Fache des Ideals).")
        head += (f" Das Umhängen der Inseln gibt zusammenhängende Gebiete mit Schnitt {_i(rep.cut)}, aber das größte Gebiet ist dann das {_dec(rep.ratio, 2)}-Fache des Ideals"
                 f" ({'innerhalb' if rep.balanced else 'außerhalb'} der Grenze von {_i(a.limit)} Standorten).")
        if rep.balanced:
            head += f" Der Ausgleich ist nicht nötig; verbessert ergibt sich Schnitt {_i(bal.cut)}."
        elif bal.balanced:
            head += f" Der zusammenhangswahrende Ausgleich erreicht die Grenze: Schnitt {_i(bal.cut)}, größtes Gebiet das {_dec(bal.ratio, 2)}-Fache."
        else:
            head += f" Der zusammenhangswahrende Ausgleich **erreicht die Grenze nicht** (Schnitt {_i(bal.cut)}, größtes Gebiet das {_dec(bal.ratio, 2)}-Fache)."
    tail = (f" Das Bezirkswachstum ist von Anfang an zusammenhängend, mit Schnitt {_i(gr.cut)} und größtem Gebiet das {_dec(gr.ratio, 2)}-Fache; ausgeglichen: Schnitt {_i(gb.cut)}, "
            f"{'Grenze erreicht' if gb.balanced else 'Grenze nicht erreicht'}.")
    return "info" if (bal.ok or rb.split_parts == 0) else "warning", head + tail


def verdict_exact(rows):
    nets = sum(r["nets"] for r in rows)
    differ = sum(r["differ"] for r in rows)
    extra = sum(r["sum_conn"] - r["sum_opt"] for r in rows)
    return "info", (f"Bei k = 2 und {_i(rows[0]['n'])} Standorten (je Netztyp {_i(rows[0]['nets'])} Netze, {_i(nets)} insgesamt; alle ausgewogenen Zweiteilungen aufgezählt) kostet der Zusammenhang beider Hälften "
                    f"in {_of(differ, nets)} Netzen etwas: insgesamt {_i(extra)} Leitungen mehr ({_i(sum(r['sum_opt'] for r in rows))} gegen {_i(sum(r['sum_conn'] for r in rows))}).")


def verdict_split(rows):
    ks = sorted({r["k"] for r in rows})
    per_k = []
    for k in ks:
        sel = [r for r in rows if r["k"] == k]
        per_k.append(f"k = {k}: {_of(sum(r['nets_split'] for r in sel), sum(r['nets'] for r in sel))}")
    kmax = ks[-1]
    sel = [r for r in rows if r["k"] == kmax]
    types = "; ".join(f"{r['label']}: {_of(r['nets_split'], r['nets'])}" for r in sel)
    return "info", ("Netze mit mindestens einem zerfallenen Gebiet der rekursiven Bisektion: " + "; ".join(per_k) + f". Bei k = {kmax} je Netztyp: {types}. "
                    f"Zerfallene Gebiete bei k = {kmax} insgesamt: {_of(sum(r['parts_split'] for r in sel), sum(r['parts'] for r in sel))}.")


def verdict_repair(rows):
    nets = sum(r["nets"] for r in rows)
    mean = lambda key: sum(r[f"sum_ratio_{key}"] for r in rows) / nets   # noqa: E731
    return "info", (f"Von {_i(nets)} Netzen (Netztypen mal k = 4 und 8 mal Netze) hatten {_i(sum(r['nets_split'] for r in rows))} ein zerfallenes Gebiet. Das größte Gebiet ist im Mittel das {_dec(mean('rb'), 2)}-Fache des Ideals "
                    f"(Bisektion), nach dem Umhängen der Inseln das {_dec(mean('rep'), 2)}-Fache, nach dem Ausgleich das {_dec(mean('bal'), 2)}-Fache. Zusammenhängend und innerhalb der Grenze sind nach dem Umhängen "
                    f"{_of(sum(r['ok_rep'] for r in rows), nets)} Netze, nach dem Ausgleich {_of(sum(r['ok_bal'] for r in rows), nets)}.")


def verdict_grow(rows):
    both = sum(r["n_both"] for r in rows)
    nets = sum(r["nets"] for r in rows)
    return "info", (f"Bezirkswachstum mit Ausgleich erfüllt Grenze und Zusammenhang in {_of(sum(r['ok_growbal'] for r in rows), nets)} Netzen, Bisektion mit Reparatur in {_of(sum(r['ok_bal'] for r in rows), nets)}. "
                    f"Auf den {_i(both)} Netzen, in denen beide es schaffen, ist der Schnitt {_i(sum(r['sum_bal_both'] for r in rows))} (Reparatur) gegen {_i(sum(r['sum_grow_both'] for r in rows))} (Bezirkswachstum).")


def verdict_checks(rows):
    nets, wrong = sum(r["nets"] for r in rows), sum(r["wrong"] for r in rows)
    if wrong:
        return "warning", f"Bei {_i(wrong)} von {_i(nets)} Analysen weicht die Prüfung ab."
    return "info", (f"Alle {_i(nets)} Analysen ({_i(len(rows))} Netztyp-k-Paare mit je {_i(rows[0]['nets'])} festen Netzen mit {_i(rows[0]['n'])} Standorten) bestehen die Prüfung: Schnitt und Größen gleich der Nachzählung, "
                    f"kein Gebiet leer, nach dem Umhängen, dem Ausgleich und beim Bezirkswachstum jedes Gebiet zusammenhängend. Abweichungen: 0.")
