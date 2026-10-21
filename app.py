"""Gebiete aufteilen: ausgewogen und zusammenhängend - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Achtes Stück der Reihe „Schnitte und Zusammenhang“: Wie teilt man ein Netz in ausgewogene, zusammenhängende Gebiete? Rekursive Bisektion, Prüfung, Reparatur und Bezirkswachstum im Vergleich.

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import geb_algorithm as A
import geb_constants as C
import geb_evaluation as ev
import geb_experiments as ex
from geb_layout import dunkles_design, kopf_css
from geb_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from geb_visualization import (
    build_cuts,
    build_exact,
    build_grow,
    build_map,
    build_ratios,
    build_repair,
    build_split,
)

st.set_page_config(page_title="Gebiete aufteilen: ausgewogen und zusammenhängend – Sebastian Hanisch", layout="wide")

_i, _dec = ev._i, ev._dec


def _show(verdict):
    kind, text = verdict
    {"success": st.success, "info": st.info, "warning": st.warning}[kind](text)


@st.cache_data(show_spinner=False, max_entries=6)
def _analysis(settings):
    return ev.analyse(settings)


@st.cache_data(show_spinner=False)
def _checks():
    return ex.checks_rows()


@st.cache_data(show_spinner=False)
def _exact():
    return ex.exact_rows()


@st.cache_data(show_spinner=False)
def _split():
    return ex.split_rows()


@st.cache_data(show_spinner=False)
def _repair():
    return ex.repair_rows()


@st.cache_data(show_spinner=False)
def _grow():
    return ex.grow_rows()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in geb_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🗺️ Gebiete aufteilen: ausgewogen und zusammenhängend")
st.markdown(
    """
**Wie teilt man ein Netz in Gebiete, die gleich groß sind und jeweils in einem Stück zusammenhängen?** Eine gute Teilung nach Schnitt (**bisektion-demo**, **multilevel-partitionierung-demo**) sorgt für wenige Leitungen zwischen den Teilen
und für Gleichgewicht, aber **nicht dafür, dass jeder Teil zusammenhängt**: Ein Gebiet kann aus zwei Stücken bestehen, die nur über andere Gebiete verbunden sind. Die Demo teilt ein Netz mit **rekursiver Bisektion** in k Gebiete, **prüft** den Zusammenhang,
**repariert** (Inseln umhängen, dann zusammenhangswahrend ausgleichen) und stellt das **Bezirkswachstum** daneben, das von Anfang an zusammenhängt.

Auffällig: Auf **Kartennetzen** und **Verbundnetzen** zerfällt bei vier und acht Gebieten in jedem gemessenen Netz mindestens ein Gebiet, und viele Standorte liegen in Inseln; das Umhängen der Inseln macht ein Gebiet **zu groß**, und der Ausgleich schafft die Grenze nicht immer. Bei den anderen Netztypen sind die Inseln klein, bei acht Gebieten zerfällt aber auch dort oft ein Gebiet.
Ehrlich: Die Reparatur ist eine einfache Heuristik; ob ein besseres Verfahren öfter Grenze **und** Zusammenhang erreicht, misst die Demo nicht.

Das ist das achte (optionale) Stück der Reihe **Schnitte und Zusammenhang**; das Teilen in zwei Hälften zeigen **bisektion-demo** und **multilevel-partitionierung-demo**, mehr als zwei Teile **multiway-cut-demo**. Weiter unten: die Experimente **🔬**,
**🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So arbeiten die Schritte", expanded=True):
    st.markdown(
        """
1. **Rekursive Bisektion:** Das Netz wird mit FM (Fiduccia–Mattheyses, zufällige Neustarts) halbiert, jede Hälfte wieder, bis k Gebiete entstehen.
2. **Prüfen:** Je Gebiet die Zusammenhangskomponenten zählen. Alles außerhalb der größten Komponente eines Gebiets heißt **Insel**.
3. **Inseln umhängen:** Jede Insel kommt als Ganzes an das Nachbargebiet, zu dem die meisten Leitungen führen. Das macht jedes Gebiet zusammenhängend, aber das Zielgebiet kann zu groß werden.
4. **Ausgleichen:** Aus zu großen Gebieten wird der Randstandort mit dem größten Gewinn in ein Nachbargebiet verschoben, nur wenn das Quellgebiet **zusammenhängend bleibt**; danach verbessern solche Züge den Schnitt (jeder Zug mit Gewinn, wenn die Grenze hält).
5. **Bezirkswachstum:** k Keime (der erste zufällig, jeder weitere am weitesten von den bisherigen entfernt); das kleinste Gebiet nimmt jeweils den freien Nachbarn mit den meisten Leitungen. Jedes Gebiet bleibt zusammenhängend, weil es nur um Nachbarn wächst. Danach derselbe Ausgleich wie in Schritt 4.

| Begriff | Bedeutung |
|---|---|
| **Gebiet** | eine der k Gruppen von Standorten |
| **Insel** | Teil eines Gebiets, der nicht zur größten Komponente seines Gebiets gehört |
| **Schnitt** | Zahl der Leitungen zwischen verschiedenen Gebieten |
| **Grenze** | größtes erlaubtes Gebiet ⌈(1 + δ) n / k⌉ mit der Abweichung δ vom Ideal |
| **Ideal** | n / k Standorte |
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Netz**")
    kind = st.selectbox("Art des Netzes", list(C.KINDS), format_func=C.KIND_NAMES.get, key="kind_select", help=C.KIND_HELP.get(st.session_state.get("kind_select", C.DEFAULT_KIND), ""))
    n = st.slider("Standorte n", *bounds("n_slider"), key="n_slider", help="Wie viele Standorte das Netz hat (das Gitter rundet auf ein Rechteck).")
    deg = st.slider("Mittlerer Grad", *bounds("deg_slider"), key="deg_slider", step=0.5, help="Leitungen je Standort im Mittel; wirkt beim Zufallsnetz und innerhalb der Regionen des Verbundnetzes.")
    links = st.slider("Leitungen zwischen je zwei Regionen", *bounds("links_slider"), key="links_slider", help="Wirkt nur beim Verbundnetz.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Legt das Netz, die Anordnungen beim Halbieren und die Keime des Bezirkswachstums fest.")
    st.button("🎲 Neues Netz erzeugen", width="stretch", on_click=randomize_seed)
    st.caption(C.KIND_REGLER[kind])
    st.markdown("**Gebiete**")
    k = st.selectbox("Zahl der Gebiete k", list(C.K_CHOICES), key="k_select", help="Zweierpotenzen, weil die rekursive Bisektion immer halbiert.")
    delta = st.selectbox("Abweichung δ vom Ideal (%)", list(C.DELTA_CHOICES), key="delta_select", help="Jedes Gebiet darf höchstens ⌈(1 + δ) · n / k⌉ Standorte haben.")

sync_query_params({"kind_select": kind, "n_slider": int(n), "deg_slider": float(deg), "links_slider": int(links), "seed_input": int(seed), "k_select": int(k), "delta_select": int(delta)})

settings = ev.Settings(kind, int(n), float(deg), int(links), int(seed), int(k), int(delta))
with st.spinner("Teile das Netz und prüfe die Gebiete..."):
    a = _analysis(settings)
problems = ev.validate(a)
for p in problems:
    st.error(f"Prüfung fehlgeschlagen: {p}")
signature = f"{settings.kind}_{settings.n}_{settings.deg}_{settings.links}_{settings.seed}_{settings.k}_{settings.delta}"
inst = a.inst
g = a.graph
Q = a.quality

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
st.caption(f"{C.KIND_NAMES[kind]} mit {_i(a.n)} Standorten und {_i(a.m)} Leitungen, {k} Gebiete; Grenze {_i(a.limit)} Standorte je Gebiet (Ideal {_dec(a.n / k)}, Abweichung {_i(delta)} %).")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Bisektion: Schnitt", _i(Q["rb"].cut), delta=f"größtes Gebiet {_dec(Q['rb'].ratio, 2)} × Ideal", delta_color="off")
m2.metric("Zerfallene Gebiete", f"{_i(Q['rb'].split_parts)} von {_i(k)}", delta=f"{_i(Q['rb'].island_nodes)} Standorte in Inseln", delta_color="off")
m3.metric("Reparatur mit Ausgleich: Schnitt", _i(Q["bal"].cut), delta=("Grenze erreicht" if Q["bal"].balanced else f"Grenze verfehlt: {_dec(Q['bal'].ratio, 2)} × Ideal"), delta_color="off")
m4.metric("Bezirkswachstum mit Ausgleich: Schnitt", _i(Q["growbal"].cut), delta=("Grenze erreicht" if Q["growbal"].balanced else f"Grenze verfehlt: {_dec(Q['growbal'].ratio, 2)} × Ideal"), delta_color="off")
_show(ev.verdict_run(a))

tab_map, tab_cmp = st.tabs(["🗺️ Karte", "📊 Vergleich der Schritte"])

keys = [key for key, _name in ev.STAGES]
long_names = [ev.STAGE_LONG[key] for key in keys]

# --- Tab 1: Karte -----------------------------------------------------------------------------------------------------------------------------

with tab_map:
    stage = st.radio("Schritt", keys, format_func=ev.STAGE_LONG.get, horizontal=True, key=f"stage_{signature}", help="Welche Teilung auf der Karte gezeigt wird.")
    q = Q[stage]
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(f"**{ev.STAGE_LONG[stage]}**")
        st.plotly_chart(build_map(inst, g, a.labels[stage], k, seeds=a.seeds if stage.startswith("grow") else (), height=470), width="stretch", key=f"map_{signature}_{stage}")
        st.caption("Farbe: Gebiet; rot gestrichelt: Leitungen zwischen den Gebieten; schwarz umrandete Rauten: Inseln (Standorte außerhalb der größten Komponente ihres Gebiets); Sterne: Keime des Bezirkswachstums.")
    with c2:
        parts = A.members(a.labels[stage], k)
        st.dataframe(pd.DataFrame({"Gebiet": [str(i + 1) for i in range(k)], "Standorte": [_i(x) for x in q.sizes], "Stücke": [_i(len(A.components(g, part))) for part in parts]}), hide_index=True, width="stretch")
        st.caption(f"Schnitt {_i(q.cut)}; größtes Gebiet {_i(max(q.sizes))} Standorte (Grenze {_i(a.limit)}): {'innerhalb' if q.balanced else 'außerhalb'}; "
                   + ("jedes Gebiet zusammenhängend." if q.connected else f"{_i(q.split_parts)} von {_i(k)} Gebieten bestehen aus mehreren Stücken ({_i(q.island_nodes)} Standorte in Inseln)."))
        if stage == "rep":
            st.caption(f"Beim Umhängen wurden {_i(a.moved)} Standorte bewegt.")

# --- Tab 2: Vergleich der Schritte --------------------------------------------------------------------------------------------------------

with tab_cmp:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Schnitt**")
        st.plotly_chart(build_cuts(a, keys, long_names), width="stretch", key=f"cuts_{signature}")
    with c2:
        st.markdown("**Größtes Gebiet im Verhältnis zum Ideal**")
        st.plotly_chart(build_ratios(a, keys, long_names), width="stretch", key=f"ratios_{signature}")
    st.caption("Der Schnitt allein täuscht: Das Umhängen senkt ihn meist stark, aber auf Kosten der Ausgewogenheit (rechts; gestrichelt die Grenze).")
    rows = [{"Schritt": ev.STAGE_LONG[key], "Schnitt": _i(Q[key].cut), "Größtes Gebiet": _i(max(Q[key].sizes)), "× Ideal": _dec(Q[key].ratio, 2), "Zerfallene Gebiete": _i(Q[key].split_parts),
             "Standorte in Inseln": _i(Q[key].island_nodes), "Grenze erreicht": "ja" if Q[key].balanced else "nein", "Zusammenhängend": "ja" if Q[key].connected else "nein"} for key in keys]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🔬 Experimente über feste Netze")
st.caption(f"Je Netztyp {len(C.SWEEP_SEEDS)} feste Netze mit {C.EX_N} Standorten, Abweichung {C.DEFAULT_DELTA} %, k = {', '.join(str(x) for x in C.EX_KS)}; nie ein einzelner Zufalls-Seed als Befund.")

st.subheader("🔬 Experiment 1: Stimmen Größen, Schnitte und Zusammenhang überein?")
with st.spinner("Rechne die Experimente..."):
    rows_c = _checks()
_show(ev.verdict_checks(rows_c))

st.subheader("🔬 Experiment 2: Was kostet der Zusammenhang bei zwei Gebieten (exakt)?")
rows_e = _exact()
st.caption(f"Alle ausgewogenen Zweiteilungen von Netzen mit {C.EX_EXACT_N} Standorten (je Netztyp {len(C.EX_EXACT_SEEDS)} Netze) aufgezählt: der kleinste Schnitt gegen den kleinsten Schnitt mit zwei zusammenhängenden Hälften.")
st.plotly_chart(build_exact(rows_e), width="stretch", key="ex_exact")
_show(ev.verdict_exact(rows_e))

st.subheader("🔬 Experiment 3: Wie oft zerfallen Gebiete der Bisektion?")
rows_s = _split()
st.caption("Anteil der Gebiete der rekursiven Bisektion, die aus mehreren Stücken bestehen, je Netztyp und Zahl der Gebiete.")
st.plotly_chart(build_split(rows_s), width="stretch", key="ex_split")
_show(ev.verdict_split(rows_s))

st.subheader("🔬 Experiment 4: Was kostet die Reparatur?")
rows_r = _repair()
st.caption("Größtes Gebiet im Verhältnis zum Ideal (Mittel über die Netze) roh, nach dem Umhängen der Inseln und nach dem Ausgleich; die gestrichelte Linie ist die Grenze.")
st.plotly_chart(build_repair(rows_r), width="stretch", key="ex_repair")
_show(ev.verdict_repair(rows_r))

st.subheader("🔬 Experiment 5: Bezirkswachstum gegen Bisektion mit Reparatur")
rows_g = _grow()
st.caption("Zahl der Netze, in denen ein Verfahren Grenze und Zusammenhang gleichzeitig erreicht.")
st.plotly_chart(build_grow(rows_g), width="stretch", key="ex_grow")
_show(ev.verdict_grow(rows_g))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Einfache Heuristiken** | Teilen in ausgewogene, zusammenhängende Gebiete ist NP-schwer; Umhängen, Ausgleichen und Bezirkswachstum sind einfache Regeln ohne Gütegarantie. Ein besseres Verfahren (etwa mit Flüssen oder mit Zusammenhangsprüfung in jedem FM-Zug) erreicht Grenze und Zusammenhang vermutlich öfter; das ist nicht gemessen. | - |
| **Gleich schwere Standorte** | Alle Standorte zählen eins; echte Gebiete (Vertriebsbezirke, Liefergebiete) haben Lasten, Zeiten und Kapazitäten, und ihre Grenze hängt an einer Summe von Bedarfen. | kapazitierte-standortplanung-demo |
| **Zusammenhang im Netz** | Zusammenhängend heißt hier: über Leitungen des Netzes verbunden. Fahrzeit, Kompaktheit der Form und Grenzen von Verwaltungsgebieten sind nicht modelliert. | - |
| **k ist eine Zweierpotenz** | Die rekursive Bisektion halbiert immer; andere k brauchen ungleiche Teilungen. | multiway-cut-demo |
| **Wenige feste Netze** | Je Netztyp vier Netze mit 256 Standorten: Die Zähler sind Zähler, keine Tests. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** ein ungerichteter, zusammenhängender Graph $G = (V, E)$ mit $n$ Standorten, eine Zahl $k$ von Gebieten und eine Abweichung $\delta \ge 0$. Gesucht ist eine Zerlegung $V = V_1 \cup \dots \cup V_k$ in paarweise disjunkte, nichtleere Gebiete mit

$$|V_i| \;\le\; \Bigl\lceil (1 + \delta)\,\frac{n}{k} \Bigr\rceil, \qquad G[V_i] \text{ zusammenhängend} \quad (i = 1, \dots, k),$$

und kleinstem **Schnitt** $\bigl|\{\{u, v\} \in E : u \in V_i,\; v \in V_j,\; i \ne j\}\bigr|$. Ohne die Zusammenhangsbedingung ist das die Graphpartitionierung (NP-schwer); mit ihr bleibt es NP-schwer (Dyer, Frieze 1985).

**Insel.** Hat $G[V_i]$ die Zusammenhangskomponenten $K_1, K_2, \dots$ mit $|K_1| \ge |K_2| \ge \dots$, so heißen die Standorte in $K_2, K_3, \dots$ Inseln von $V_i$.

**Umhängen.** Eine Insel $K$ von $V_i$ geht ganz an das Gebiet $V_j$ ($j \ne i$), für das $|E(K, V_j)|$ am größten ist (bei Gleichstand das kleinere $j$). Jeder solche Schritt verbindet $K$ mit mindestens einer Komponente von $V_j$ und trennt $V_i$ nicht weiter; die Zahl aller Komponenten aller Gebiete sinkt also, und das Verfahren endet mit lauter zusammenhängenden Gebieten. Das Gebiet $V_j$ kann dabei über die Grenze wachsen.

**Ausgleichen und Verbessern.** Der Gewinn eines Standorts $v \in V_i$ beim Wechsel in $V_j$ ist $g_j(v) = |E(v, V_j)| - |E(v, V_i)|$; der Schnitt sinkt um $g_j(v)$. Ein Zug ist erlaubt, wenn $|V_j| + 1$ höchstens die Grenze ist und $G[V_i \setminus \{v\}]$ nichtleer und zusammenhängend bleibt. Zuerst werden Züge aus zu großen Gebieten mit größtem Gewinn gemacht, bis keines mehr zu groß ist (oder kein erlaubter Zug bleibt), danach alle Züge mit positivem Gewinn.

**Bezirkswachstum.** Keime $s_1, \dots, s_k$; solange es freie Standorte gibt, nimmt das kleinste Gebiet $V_i$ (bei Gleichstand das mit der kleineren Nummer) den freien Nachbarn $u$ mit größtem $|E(u, V_i)|$ (bei Gleichstand den kleineren). Weil $V_i$ nur um einen Nachbarn wächst, bleibt es zusammenhängend.

**Literatur.** M. E. Dyer, A. M. Frieze: *On the complexity of partitioning graphs into connected subgraphs*, Discrete Applied Mathematics 10 (2), 1985, S. 139–153. C. M. Fiduccia, R. M. Mattheyses: *A linear-time heuristic for improving network partitions*, 19th Design Automation Conference, 1982, S. 175–181.
Die Demo rechnet FM in der einfachsten Form (ohne Gewinn-Fächer) und erhebt nicht den Anspruch, Systeme zur Gebietsplanung zu ersetzen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
