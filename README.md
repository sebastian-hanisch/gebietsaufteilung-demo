# Gebiete aufteilen: ausgewogen und zusammenhängend – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-gebietsaufteilung-demo.streamlit.app/)** -->

Achtes (optionales) Stück der Reihe **Schnitte und Zusammenhang** (Arbeitstitel der Linie `schnitte-zusammenhang`) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, Bereich Graphentheorie. Vehikel: ein **Verbindungsnetz zwischen Standorten** (Depots, Umschlagpunkte, Werke), synthetisch und mit festem Zufalls-Seed, 24 bis 300 Standorte. Die Demo fragt: **Wie teilt man ein Netz in k Gebiete, die gleich groß sind und jeweils zusammenhängen?** Eine gute Zweiteilung nach Schnitt (`bisektion-demo`, `multilevel-partitionierung-demo`) sorgt für wenige Leitungen zwischen den Teilen und für Gleichgewicht, aber nicht für den **Zusammenhang** jedes Teils. Die Demo teilt mit **rekursiver Bisektion** (FM mit zufälligen Neustarts) in 2, 4 oder 8 Gebiete, **prüft** den Zusammenhang, **repariert** (Inseln umhängen, dann zusammenhangswahrend ausgleichen und verbessern) und stellt das **Bezirkswachstum** (Region Growing) daneben.

Nachbarn: das Halbieren selbst zeigen `bisektion-demo` und `multilevel-partitionierung-demo`, mehr als zwei Teile `multiway-cut-demo`, die Zusammenhangsfrage für Brücken `zusammenhang-verstaerken-demo`; Gebiete mit Kapazitäten gehören in die Standortplanung (`kapazitierte-standortplanung-demo`), hier nur mit der Zusammenhangsbedingung.

## Warum dieses Problem

Eine Teilung, die den Schnitt klein hält, kümmert sich nicht darum, ob jedes Gebiet in einem Stück liegt: Ein Gebiet kann aus zwei Stücken bestehen, die nur über andere Gebiete zusammenhängen. Für Vertriebs- oder Liefergebiete ist das unbrauchbar. Die Demo zeigt, **wie oft das passiert** (bei vier Gebieten in 14 von 24 Netzen, bei acht in 20 von 24), **auf welchen Netzen** (Kartennetz und Verbundnetz: viele Standorte in Inseln), **was die einfache Reparatur kostet** (das Umhängen senkt den Schnitt stark, macht aber ein Gebiet zu groß: im Mittel das 1,27-Fache des Ideals gegen 1,06 vor der Reparatur) und **dass das Bezirkswachstum auf Kartennetzen die zuverlässigere Antwort ist**, auf allen anderen aber einen viel größeren Schnitt hat.

## Befunde und Korrekturen gegenüber dem Plan

- **Der Plan erwartete „Zusammenhang kostet fast nichts“** (1 von 59 Instanzen bei exakter Rechnung, Vormessung mit 16 Standorten). Bei **zwei** Gebieten bestätigt die Demo das knapp: Bei 16 Standorten kostet der Zusammenhang in **4 von 36** Netzen etwas (insgesamt 6 Leitungen mehr, 204 gegen 210). Bei **vier und acht** Gebieten zerfallen aber in 14 und 20 von 24 Netzen Gebiete, und eine einfache Reparatur erreicht Grenze und Zusammenhang nicht immer: Der Befund hängt an der Zahl der Gebiete und am Netztyp.
- **Der Plan nannte „Bezirkswachstum gegen rekursive Bisektion“ als offene Frage.** Antwort der Demo: auf Kartennetzen schneidet das Bezirkswachstum mit Ausgleich **besser** ab (Schnitt 34 gegen 58 auf den drei Netzen, in denen beide die Grenze einhalten) **und** hält die Grenze in allen acht Netzen ein, Bisektion mit Reparatur in drei; auf Gittern, Ringen, skalenfreien und Zufallsnetzen ist die Bisektion mit Reparatur klar besser (z. B. Gitter: 137 gegen 270 bei vier Gebieten).
- **Der Preis des Zusammenhangs hat zwei Seiten:** Das Umhängen **senkt** den Schnitt (auf Kartennetzen von 71 auf 23 Leitungen bei vier Gebieten, Summe über vier Netze), weil die Inseln dort gerade die teure Grenze waren, aber auf Kosten der Ausgewogenheit; der Schnitt allein täuscht (Experiment 4).
- **Vormessungszahlen nicht übernommen:** Die Zahlen des Plans (Mehrstufig-Bisektion, 20 Läufe, n ≈ 300) stammen aus Wegwerfskripten. Die Demo halbiert mit FM und zufälligen Neustarts (ohne Vergröbern) und misst neu: Netze mit zerfallenen Gebieten bei k = 4 und 8 sind beim Gitter 1 und 2 von 4 (Plan: 8 und 10 von 20), beim Verbundnetz 4 und 4 von 4 (Plan: 15 und 18 von 20); die Größenordnung stimmt, die Zahlen sind andere.
- **Kompaktheit nicht gebaut:** Der Plan nannte Kompaktheit als Gütemaß; die Demo misst Schnitt, Ausgewogenheit und Zusammenhang.

## Modell

Ein einfaches, **zusammenhängendes** Netz mit n Standorten (Zufallsnetz: Zufallsbaum plus Leitungen bis zum mittleren Grad; Gitter als Rechteck; Ring mit Abkürzungen; skalenfreies Netz nach bevorzugter Anbindung; Verbundnetz aus drei Regionen mit einstellbar vielen Leitungen dazwischen; Kartennetz aus zufälligen Punkten, jeder mit seinen drei nächsten Nachbarn verbunden). Jeder Standort zählt eins. Eine Zerlegung in k **Gebiete** ist **zulässig**, wenn jedes Gebiet höchstens ⌈(1 + δ/100) · n / k⌉ Standorte hat (δ: 5, 10 oder 20 %; die **Grenze**) und **zusammenhängt**. Der **Schnitt** ist die Zahl der Leitungen zwischen verschiedenen Gebieten. Eine **Insel** ist ein Standort außerhalb der größten Zusammenhangskomponente seines Gebiets. Der Zufall kommt nur aus `random.Random` (plattformstabil). Formeln: Expander „📐 Mathematische Formulierung“ in der App.

## Methodik

- **Rekursive Bisektion:** jede Halbierung mit FM (Fiduccia–Mattheyses, Spielraum 3 % je Halbierung) und zufälligen Neustarts, bis das Budget von drei Zügen je Standort erreicht ist (der letzte Start wird zu Ende geführt); k = 2, 4, 8.
- **Prüfen:** Zusammenhangskomponenten je Gebiet; Inseln = alles außerhalb der größten Komponente (bei Gleichstand die mit dem kleinsten Standort).
- **Inseln umhängen:** jede Insel als Ganzes an das Nachbargebiet mit den meisten Leitungen zur Insel (bei Gleichstand das kleinere), bis jedes Gebiet zusammenhängt; jeder Schritt verbindet die Insel mit einer Komponente des Ziels, die Zahl aller Komponenten sinkt also bei jedem Schritt und das Verfahren endet.
- **Ausgleichen und Verbessern:** zu große Gebiete verkleinern, indem der Randstandort mit dem größten Gewinn in ein Nachbargebiet wechselt, das danach höchstens die Grenze hat und nur, wenn das Quellgebiet **nichtleer und zusammenhängend bleibt**; danach alle Züge mit positivem Gewinn nach derselben Regel (höchstens sechs Durchläufe). Es kann sein, dass kein erlaubter Zug bleibt: dann bleibt das Ergebnis außerhalb der Grenze.
- **Bezirkswachstum:** k Keime (der erste zufällig, jeder weitere am weitesten von den bisherigen entfernt, in Leitungen gemessen); das kleinste Gebiet (bei Gleichstand die kleinere Nummer) nimmt den freien Nachbarn mit den meisten Leitungen zum Gebiet; danach derselbe Ausgleich.
- **Exakt:** für k = 2 und 16 Standorte alle ausgewogenen Zweiteilungen aufgezählt, einmal ohne, einmal mit der Bedingung, dass beide Hälften zusammenhängen.
- **Unabhängige Prüfer:** Die App prüft jedes Ergebnis vor der Anzeige (alle Standorte einem Gebiet zugeordnet, kein Gebiet leer, Schnitt und Größen gleich der Nachzählung, nach dem Umhängen, dem Ausgleich und beim Bezirkswachstum jedes Gebiet zusammenhängend, Zahl der zerfallenen Gebiete und Grenzmeldung gleich der Nachzählung).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`; Zähler über feste Netze (je Netztyp vier Netze mit 256 Standorten, Abweichung 10 %; bei der Aufzählung sechs Netze mit 16 Standorten), nie ein einzelner Zufalls-Seed. Netztypen: Kartennetz, Gitter, Ring mit Abkürzungen, skalenfreies Netz, Zufallsnetz (Grad 4), Verbundnetz (Grad 5, eine Leitung zwischen je zwei Regionen).

| Frage | Befund |
|---|---|
| Stimmt die Rechnung auf allen Netzen? | Alle **72** Analysen (18 Netztyp-k-Paare mit je vier Netzen) bestehen die Prüfung, Abweichungen: **0**. |
| Was kostet der Zusammenhang bei zwei Gebieten (exakt)? | Bei 16 Standorten kostet er in **4 von 36** Netzen etwas: Kartennetz 2, skalenfrei 1, Zufallsnetz 1, Gitter, Ring und Verbundnetz 0; insgesamt **6** Leitungen mehr (**204** gegen **210**). |
| Wie oft zerfallen Gebiete der Bisektion? | Netze mit mindestens einem zerfallenen Gebiet: k = 2 **8 von 24**, k = 4 **14 von 24**, k = 8 **20 von 24**; zerfallene Gebiete 12 von 48, 27 von 96, 56 von 192. Bei k = 4 je Netztyp: Kartennetz 4 von 4, Verbundnetz 4, Ring 2, skalenfrei 2, Gitter 1, Zufallsnetz 1. |
| Wie groß sind die Inseln? | Standorte in Inseln bei k = 4 (Summe über vier Netze): Kartennetz **332**, Verbundnetz **126**, Ring 35, Gitter 24, skalenfrei 4, Zufallsnetz 3. |
| Was kostet das Umhängen und der Ausgleich? | Größtes Gebiet im Mittel (48 Netze bei k = 4 und 8): **1,06**-faches Ideal (Bisektion), **1,27** nach dem Umhängen, **1,15** nach dem Ausgleich. Kartennetz bei k = 4: 1,04 → **1,59** → 1,16, Schnitt 71 → **23** → 65 (Summe über vier Netze); Verbundnetz 1,06 → 1,33 → 1,15, Schnitt 414 → 230 → 374. |
| Wie oft gelingt Grenze **und** Zusammenhang? | Nach dem Umhängen in **19 von 48** Netzen, nach dem Ausgleich in **39 von 48**; Kartennetz und Verbundnetz am schwersten (Ausgleich bei k = 4: 2 von 4 beide, bei k = 8: Kartennetz 1 von 4, Verbundnetz 2 von 4). |
| Bezirkswachstum gegen Bisektion mit Reparatur? | Mit Ausgleich erreicht das Bezirkswachstum Grenze und Zusammenhang in **43 von 48** Netzen, die Reparatur in **39**. Auf den **36** Netzen, in denen beide es schaffen, ist der Schnitt **4.035** (Reparatur) gegen **4.743** (Bezirkswachstum); auf den drei Kartennetzen darunter **58** gegen **34**, auf den vier Gittern bei k = 4 **137** gegen **270**. |
| Wo wächst es nicht? | Bei k = 8 erreicht das Bezirkswachstum die Grenze auf dem Gitter in 2 von 4, im Verbundnetz in 1 von 4 Netzen (Reparatur: 4 und 2). |
| Die Presets? | Jedes Preset in `tests/test_claims.py` (z. B. Kartennetz: Bisektion 17, 2 Gebiete zerfallen, 72 Standorte in Inseln, nach dem Umhängen Schnitt 7 mit dem 1,81-Fachen des Ideals; „Weite Grenze (20 %)“: nur das Bezirkswachstum erreicht beides, Schnitt 14). |
| Ist die Rechnung korrekt? | Komponenten gleich `networkx.connected_components` auf Teilmengen, Schnitt gleich `networkx.cut_size`, Inseln gleich der Definition über networkx-Komponenten, jedes umgehängte, ausgeglichene, verbesserte und gewachsene Gebiet `networkx.is_connected` (18 Netze, k = 2, 4, 8), die exakte Aufzählung gleich einer networkx-Aufzählung auf Netzen mit 10 und 11 Standorten, die Grenze gleich der Bruchrechnung (`tests/test_oracle_gebiete.py`). |

## Ehrliche Grenzen

- **Einfache Heuristiken.** Teilen in ausgewogene, zusammenhängende Gebiete ist NP-schwer (Dyer, Frieze 1985); Umhängen, Ausgleichen und Bezirkswachstum sind einfache Regeln ohne Gütegarantie. Dass die Reparatur die Grenze oft verfehlt, sagt etwas über **diese** Reparatur, nicht über das Problem: ein Verfahren mit Zusammenhangsprüfung in jedem FM-Zug oder mit Flüssen erreicht beides vermutlich öfter, das ist nicht gemessen.
- **Gleich schwere Standorte, gleich lange Leitungen.** Echte Gebiete (Vertriebsbezirke, Liefergebiete) haben Lasten, Zeiten und Kapazitäten; die Grenze hängt dort an einer Summe von Bedarfen.
- **Zusammenhang im Netz heißt Leitungen.** Fahrzeit, Kompaktheit der Form und Verwaltungsgrenzen sind nicht modelliert.
- **k nur 2, 4, 8.** Die rekursive Bisektion halbiert immer.
- **Wenige feste Netze.** Je Netztyp vier Netze (bei der Aufzählung sechs mit 16 Standorten): Die Zähler sind Zähler, keine Tests; einzelne Zellen (z. B. „1 von 4“) tragen keinen Befund allein.
- **Das Bezirkswachstum hängt an den Keimen.** Die Keime (zufälliger erster, dann am weitesten entfernt) bestimmen die Gebiete stark; andere Keime würden anders ausfallen.

## Tests

Das Verzeichnis `tests/` enthält zurzeit 117 Tests (Laufzeit etwa eine Minute auf dem Entwicklungsrechner):

- **Kern** (`test_algorithm.py`): jede Einheit an von Hand gerechneten Mini-Netzen: Grenze, Teilnetz, Komponenten, Inseln, Umhängen (auch Gleichstände), Ausgleich (auch der Fall ohne erlaubten Zug), Verbessern, Keime, Bezirkswachstum, rekursive Bisektion auf dem Pfad.
- **Szenarien** (`test_scenario.py`): einfach, zusammenhängend, deterministisch für jeden Netztyp.
- **Orakel** (`test_oracle_gebiete.py`): networkx (Komponenten, Schnitt, Zusammenhang), Aufzählung aller Zweiteilungen, Bruchrechnung der Grenze.
- **Randfälle** (`test_edge_cases.py`): kleinste Netze und größtes k, Stern ohne erlaubten Zug, jede Art von Prüffehler an verfälschten Analysen, Grenzen der Regler.
- **Zweige, Verdikte, Befunde** (`test_branches.py`, `test_verdicts.py`, `test_claims.py`): jedes Preset prüft sauber und jede Abbildung rendert (auch jeder Schritt); jedes Verdikt an handgesetzten Zeilen; jede Zahl dieses README.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum), Layout (Schnellstart oben, aktives Preset hervorgehoben), Footer, Laufzeit-Importe.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Karte je Schritt, Vergleich der Schritte, fünf Experimente |
| `geb_algorithm.py` | Kern: FM, rekursive Bisektion, Komponenten, Inseln, Umhängen, Ausgleichen, Verbessern, Keime, Bezirkswachstum |
| `geb_constants.py` | Regler-Grenzen, Netztypen, Raster der Experimente, Farben, Presets |
| `geb_evaluation.py` | Analyse, Qualität je Schritt, Prüfung vor der Anzeige, Verdikte |
| `geb_experiments.py` | Experimente über feste Netze, exakte Aufzählung |
| `geb_layout.py` | Fester Kopf (Stylesheet) |
| `geb_presets.py` | Permalink, Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `geb_scenario.py` | Netze: Zufallsnetz, Gitter, Ring, skalenfreies Netz, Verbundnetz, Kartennetz |
| `geb_visualization.py` | Plotly-Abbildungen (Karte mit Inseln und Keimen, Schnitt und Größe je Schritt, Experimente) |
| `requirements-dev.txt` | Laufzeit plus pytest und networkx (Gegenproben) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Netze, Orakel, Randfälle, Zweige, Verdikte, Befunde, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Kompaktheit, Fahrzeiten, Kapazitäten, Lasten:** nur als Einordnung in den Grenzen.
- **Andere k als Zweierpotenzen, direktes k-Teilen:** die Demo halbiert rekursiv.
- **Bessere Reparatur** (Zusammenhangsprüfung im FM-Zug, Flüsse, exakte Lösung für größere Netze): nicht gebaut.
- **Echte Netze oder Dateiimport:** die Netze sind synthetisch.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, pandas und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
