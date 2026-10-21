"""Konstanten: Regler-Grenzen, feste Annahmen, Experiment-Raster, Farben und Presets."""

KINDS = ("geometric", "grid", "ring", "scalefree", "random", "verbund")
KIND_NAMES = {"geometric": "Kartennetz", "grid": "Gitter", "ring": "Ring mit Abkürzungen", "scalefree": "Skalenfreies Netz", "random": "Zufallsnetz", "verbund": "Verbundnetz"}
KIND_HELP = {
    "geometric": "Zufällige Punkte in einem Quadrat, jeder mit seinen drei nächsten Nachbarn verbunden: ein Straßennetz im Kleinen.",
    "grid": "Standorte auf einem Raster, Verbindungen zu den vier Nachbarn.",
    "ring": "Vier nächste Nachbarn auf einem Ring, ein Zehntel der Leitungen führt zu einem zufälligen Standort.",
    "scalefree": "Neue Standorte hängen sich bevorzugt an gut vernetzte an (je zwei Leitungen).",
    "random": "Zufallsbaum plus zufällige Leitungen; der mittlere Grad ist einstellbar.",
    "verbund": "Drei Regionen mit dichten inneren Verbindungen und wenigen Leitungen dazwischen (einstellbar).",
}
KIND_REGLER = {
    "geometric": "Wirksam: Standorte, Zufalls-Seed.",
    "grid": "Wirksam: Standorte (gerundet auf ein Rechteck). Zufalls-Seed, Grad und Leitungen wirken nicht auf das Netz (der Seed wirkt auf die Anordnungen beim Teilen und auf die Keime).",
    "ring": "Wirksam: Standorte, Zufalls-Seed.",
    "scalefree": "Wirksam: Standorte, Zufalls-Seed.",
    "random": "Wirksam: Standorte, mittlerer Grad, Zufalls-Seed.",
    "verbund": "Wirksam: Standorte, mittlerer Grad (in den Regionen), Leitungen zwischen den Regionen, Zufalls-Seed.",
}

N_MIN, N_MAX, DEFAULT_N = 24, 300, 256
DEG_MIN, DEG_MAX, DEFAULT_DEG = 2.0, 10.0, 4.0
LINKS_MIN, LINKS_MAX, DEFAULT_LINKS = 1, 8, 2
SEED_MAX, DEFAULT_SEED = 999999, 7
DEFAULT_KIND = "geometric"
REGIONS = 3
RING_NEIGHBOURS, RING_REWIRE = 4, 0.1
SCALEFREE_M = 2

K_CHOICES = (2, 4, 8)                    # Zahl der Gebiete (Zweierpotenzen: rekursives Halbieren geht auf)
DEFAULT_K = 4
DELTA_CHOICES = (5, 10, 20)              # erlaubte Abweichung der Gebietsgröße vom Ideal n / k in Prozent
DEFAULT_DELTA = 10
BISECT_EPS = 3                           # Spielraum jeder einzelnen Halbierung in Prozent
DEFAULT_EPS = BISECT_EPS
MAX_PASSES = 8                           # Durchläufe von FM je Halbierung (höchstens)
START_BUDGET = 3                         # Zugbudget je Halbierung: so viele Züge je Standort, dann ist der letzte Start fertig
POLISH_PASSES = 6                        # Durchläufe des zusammenhangswahrenden Verbesserns (höchstens)

SWEEP_SEEDS = tuple(range(100000, 100004))   # feste Netze für alle Experimente: nie ein einzelner Zufalls-Seed als Befund
EX_N = 256
EX_KINDS = (("geometric", 0.0), ("grid", 0.0), ("ring", 0.0), ("scalefree", 0.0), ("random", 4.0), ("verbund", 5.0))
EX_KS = (2, 4, 8)
EX_EXACT_N = 16                          # Standorte für die Aufzählung aller Teilungen bei k = 2 (Quadratzahl: das Gitter hat dieselbe Größe)
EX_EXACT_SEEDS = tuple(range(100000, 100006))

COLOR_PARTS = ("#2F6B65", "#4c78a8", "#e8a33d", "#8d6cab", "#d1495b", "#5aa05a", "#9c7a50", "#3aa6b9")
COLOR_ISLAND = "#111111"
COLOR_CUT = "#d1495b"
COLOR_EDGE = "rgba(150,150,150,0.45)"
COLOR_BAR = "#4c78a8"
COLOR_BAR2 = "#e8a33d"
COLOR_BAR3 = "#2F6B65"

PRESETS = {
    "Kartennetz: Bisektion lässt Inseln": {"kind": "geometric", "n": 256, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 7, "k": 4, "delta": 10},
    "Verbundnetz: Reparatur gelingt": {"kind": "verbund", "n": 256, "deg": 5.0, "links": 2, "seed": 7, "k": 4, "delta": 10},
    "Gitter: nichts zu reparieren": {"kind": "grid", "n": 256, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 7, "k": 4, "delta": 10},
    "Zufallsnetz: kaum Probleme": {"kind": "random", "n": 256, "deg": 4.0, "links": DEFAULT_LINKS, "seed": 7, "k": 4, "delta": 10},
    "Acht Gebiete im Kartennetz": {"kind": "geometric", "n": 256, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 7, "k": 8, "delta": 10},
    "Zwei Gebiete: ein Gebiet zerfällt": {"kind": "geometric", "n": 256, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 7, "k": 2, "delta": 10},
    "Weite Grenze (20 %): nur Wachstum schafft es": {"kind": "geometric", "n": 256, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 7, "k": 4, "delta": 20},
}
PRESET_HELP = {
    "Kartennetz: Bisektion lässt Inseln": "256 Standorte, 4 Gebiete: Die Bisektion (Schnitt 17) lässt 2 Gebiete zerfallen (72 Standorte in Inseln). Das Umhängen der Inseln gibt Schnitt 7, aber ein Gebiet mit dem 1,81-Fachen des Ideals; der Ausgleich erreicht die Grenze nicht.",
    "Verbundnetz: Reparatur gelingt": "Zwei Gebiete zerfallen (18 Standorte in Inseln). Das Umhängen macht ein Gebiet zu groß (1,33-Faches), der Ausgleich erreicht die Grenze: Schnitt 105 gegen 106 der Bisektion (die nicht zusammenhängt).",
    "Gitter: nichts zu reparieren": "Vier Quadrate, alle zusammenhängend, Schnitt 32 (das Optimum); das Bezirkswachstum kommt auf Schnitt 65.",
    "Zufallsnetz: kaum Probleme": "Kein Gebiet zerfällt (Schnitt 158); das Bezirkswachstum kommt auf Schnitt 173.",
    "Acht Gebiete im Kartennetz": "7 von 8 Gebieten zerfallen (80 Standorte in Inseln). Weder Reparatur noch Bezirkswachstum erreicht die Grenze (größtes Gebiet das 1,50- bzw. 1,31-Fache des Ideals).",
    "Zwei Gebiete: ein Gebiet zerfällt": "Die Bisektion findet Schnitt 9, aber ein Gebiet besteht aus zwei Stücken (53 Standorte in einer Insel). Nur das ausgeglichene Bezirkswachstum erreicht Grenze und Zusammenhang (Schnitt 12).",
    "Weite Grenze (20 %): nur Wachstum schafft es": "Mit 20 % Spielraum erreicht nur das ausgeglichene Bezirkswachstum beides (Schnitt 14); Bisektion mit Reparatur bleibt beim 1,48-Fachen des Ideals.",
}
