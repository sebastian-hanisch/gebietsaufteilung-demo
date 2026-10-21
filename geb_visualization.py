"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import geb_algorithm as A
import geb_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _map_layout(fig, xy, height=470):
    xs, ys = xy[:, 0], xy[:, 1]
    pad = 0.25 * max(float(xs.max() - xs.min()), float(ys.max() - ys.min()), 1.0)
    fig.update_xaxes(visible=False, range=[float(xs.min()) - pad, float(xs.max()) + pad])
    fig.update_yaxes(visible=False, range=[float(ys.min()) - pad, float(ys.max()) + pad])
    return _base(fig, height)


def build_map(inst, g, label, k, seeds=(), height=470):
    """Karte: Farbe = Gebiet, rot gestrichelt die Leitungen zwischen den Gebieten, schwarz umrandete Rauten = Inseln (Standorte außerhalb der größten Komponente ihres Gebiets), Sterne = Keime."""
    xy = inst.xy
    fig = go.Figure()
    inner, cut = ([], []), ([], [])
    for u in range(g.n):
        for v, _w in g.adj[u]:
            if u < v:
                xs, ys = cut if label[u] != label[v] else inner
                xs += [float(xy[u, 0]), float(xy[v, 0]), None]
                ys += [float(xy[u, 1]), float(xy[v, 1]), None]
    fig.add_trace(go.Scatter(x=inner[0], y=inner[1], mode="lines", line=dict(color=C.COLOR_EDGE, width=1.2), hoverinfo="skip", showlegend=False))
    if cut[0]:
        fig.add_trace(go.Scatter(x=cut[0], y=cut[1], mode="lines", line=dict(color=C.COLOR_CUT, width=1.8, dash="dot"), hoverinfo="skip", name=f"Leitungen zwischen den Gebieten ({len(cut[0]) // 3})"))
    isl = set(A.islands(g, label, k))
    sizes = A.sizes(label, k)
    for i in range(k):
        nodes = [v for v in range(g.n) if label[v] == i and v not in isl]
        fig.add_trace(go.Scatter(x=[float(xy[v, 0]) for v in nodes], y=[float(xy[v, 1]) for v in nodes], mode="markers", marker=dict(size=7, color=C.COLOR_PARTS[i % len(C.COLOR_PARTS)], line=dict(color="white", width=0.8)),
                                 hovertext=[f"Standort {inst.name(v)}, Gebiet {i + 1}" for v in nodes], hoverinfo="text", name=f"Gebiet {i + 1} ({sizes[i]})"))
    if isl:
        nodes = sorted(isl)
        fig.add_trace(go.Scatter(x=[float(xy[v, 0]) for v in nodes], y=[float(xy[v, 1]) for v in nodes], mode="markers",
                                 marker=dict(size=9, symbol="diamond", color=[C.COLOR_PARTS[label[v] % len(C.COLOR_PARTS)] for v in nodes], line=dict(color=C.COLOR_ISLAND, width=2)),
                                 hovertext=[f"Standort {inst.name(v)}, Gebiet {label[v] + 1} (Insel)" for v in nodes], hoverinfo="text", name=f"Inseln ({len(nodes)} Standorte)"))
    if seeds:
        fig.add_trace(go.Scatter(x=[float(xy[v, 0]) for v in seeds], y=[float(xy[v, 1]) for v in seeds], mode="markers", marker=dict(size=14, symbol="star", color="#ffffff", line=dict(color=C.COLOR_ISLAND, width=1.5)),
                                 hovertext=[f"Keim von Gebiet {i + 1}" for i in range(len(seeds))], hoverinfo="text", name="Keime"))
    return _map_layout(fig, xy, height)


def build_cuts(a, keys, names):
    fig = go.Figure(go.Bar(x=names, y=[a.quality[key].cut for key in keys], marker_color=C.COLOR_BAR, showlegend=False, hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.update_yaxes(title_text="Leitungen zwischen den Gebieten", rangemode="tozero")
    return _base(fig, 320)


def build_ratios(a, keys, names):
    fig = go.Figure(go.Bar(x=names, y=[round(a.quality[key].ratio, 3) for key in keys], marker_color=C.COLOR_BAR2, showlegend=False, hovertemplate="%{x}: %{y}<extra></extra>"))
    limit_ratio = a.limit * a.settings.k / a.n
    fig.add_hline(y=limit_ratio, line=dict(color=C.COLOR_CUT, dash="dash", width=1.5), annotation_text=f"Grenze {limit_ratio:.2f}".replace(".", ","), annotation_position="top left")
    fig.update_yaxes(title_text="Größtes Gebiet / Ideal n / k", range=[0, max(1.1, max(a.quality[key].ratio for key in keys) * 1.1, limit_ratio * 1.05)])
    return _base(fig, 320)


# --- Experimente ---------------------------------------------------------------------------------------------------------------------------------


def build_exact(rows):
    labels = [r["label"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=[r["sum_opt"] / r["nets"] for r in rows], name="beste ausgewogene Zweiteilung", marker_color=C.COLOR_BAR3, hovertemplate="%{x}: %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Bar(x=labels, y=[r["sum_conn"] / r["nets"] for r in rows], name="beste mit zwei zusammenhängenden Hälften", marker_color=C.COLOR_BAR2, hovertemplate="%{x}: %{y:.2f}<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Schnitt (Mittel über die Netze)", rangemode="tozero")
    return _base(fig, 360)


def build_split(rows):
    fig = go.Figure()
    labels = list(dict.fromkeys(r["label"] for r in rows))
    for k, color in zip(sorted({r["k"] for r in rows}), (C.COLOR_BAR, C.COLOR_BAR2, C.COLOR_BAR3)):
        sel = {r["label"]: r for r in rows if r["k"] == k}
        fig.add_trace(go.Bar(x=labels, y=[round(100 * sel[lab]["parts_split"] / sel[lab]["parts"], 1) for lab in labels], name=f"k = {k}", marker_color=color, hovertemplate="%{x}: %{y} %<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Zerfallene Gebiete (%)", range=[0, 100])
    return _base(fig, 380)


def build_repair(rows):
    xs = [f"{r['label']}, k = {r['k']}" for r in rows]
    fig = go.Figure()
    for key, name, color in (("rb", "Bisektion", C.COLOR_BAR), ("rep", "Inseln umgehängt", C.COLOR_BAR2), ("bal", "und ausgeglichen", C.COLOR_BAR3)):
        fig.add_trace(go.Bar(x=xs, y=[round(r[f"sum_ratio_{key}"] / r["nets"], 3) for r in rows], name=name, marker_color=color, hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.add_hline(y=1.0 + C.DEFAULT_DELTA / 100.0, line=dict(color=C.COLOR_CUT, dash="dash", width=1.5), annotation_text="Grenze", annotation_position="top left")
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Größtes Gebiet / Ideal (Mittel über die Netze)", range=[0.9, 2.0])
    return _base(fig, 420)


def build_grow(rows):
    xs = [f"{r['label']}, k = {r['k']}" for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=xs, y=[r["ok_bal"] for r in rows], name="Bisektion, repariert und ausgeglichen", marker_color=C.COLOR_BAR3, hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.add_trace(go.Bar(x=xs, y=[r["ok_growbal"] for r in rows], name="Bezirkswachstum, ausgeglichen", marker_color=C.COLOR_BAR2, hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Netze mit Grenze und Zusammenhang", range=[0, max(r["nets"] for r in rows)], dtick=1)
    return _base(fig, 420)
