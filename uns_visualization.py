"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import uns_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _lines(inst, edge_ids):
    xs, ys = [], []
    for e in edge_ids:
        u, v, _ = inst.edges[e]
        xs += [inst.points[u][0], inst.points[v][0], None]
        ys += [inst.points[u][1], inst.points[v][1], None]
    return xs, ys


def build_plan(inst, kind, groups, texts=None, height=430):
    """Plan der Standorte. kind: "kanten" (Elemente sind Leitungen) oder "knoten" (Elemente sind Standorte).
    groups: Liste (Name, Elemente, Farbe) in Zeichenreihenfolge; Elemente einer Gruppe werden hervorgehoben (Leitungen dick, Standorte groß).
    texts: Beschriftung je Element (Gewicht) als Annotation mit hellem Hintergrund (keine Text-Spur)."""
    fig = go.Figure()
    marked = {e for _, ids, _ in groups for e in ids}
    if kind == "kanten":
        rest = [e for e in range(inst.m) if e not in marked]
        xs, ys = _lines(inst, rest)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_OTHER, width=1.5), name="mögliche Leitung", hoverinfo="skip"))
        for name, ids, color in groups:
            if ids:
                xs, ys = _lines(inst, ids)
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=6), name=name, hoverinfo="skip"))
    colors, sizes = [], []
    for v in range(inst.n):
        colors.append(C.COLOR_DEPOT if v == 0 else C.COLOR_NODE)
        sizes.append(16)
    if kind == "knoten":
        for name, ids, color in groups:
            for v in ids:
                colors[v] = color
                sizes[v] = 26
    fig.add_trace(go.Scatter(
        x=[p[0] for p in inst.points], y=[p[1] for p in inst.points], mode="markers+text", text=[inst.name(v) for v in range(inst.n)],
        textposition="top center", textfont=dict(size=14), marker=dict(size=sizes, color=colors, line=dict(color="white", width=1.5)),
        name="Standort", hovertemplate="%{text}<extra></extra>", showlegend=False,
    ))
    if kind == "knoten":
        for name, ids, color in groups:
            if ids:
                fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(size=14, color=color), name=name))
    fig.add_trace(go.Scatter(x=[-0.05, 1.05], y=[-0.05, 1.05], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False))
    if texts:
        for e, text in enumerate(texts):
            if kind == "kanten":
                u, v, _ = inst.edges[e]
                x, y = (inst.points[u][0] + inst.points[v][0]) / 2, (inst.points[u][1] + inst.points[v][1]) / 2
            else:
                x, y = inst.points[e][0] + 0.045, inst.points[e][1] - 0.045
            fig.add_annotation(x=x, y=y, text=text, showarrow=False, bgcolor="rgba(255,255,255,0.88)", font=dict(size=11, color="#222"), borderpad=1)
    fig.update_xaxes(visible=False, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False)
    return _base(fig, height)


def build_ratio_histogram(d):
    """Verteilung des Verhältnisses Greedy / Optimum; Linien für den Rangquotienten q und den Mittelwert."""
    fig = go.Figure(go.Histogram(x=list(d["ratios"]), xbins=dict(start=0, end=1.0001, size=0.02), marker_color=C.COLOR_LINE, name="Läufe",
                                 hovertemplate="Verhältnis %{x}: %{y} Läufe<extra></extra>"))
    fig.add_vline(x=d["q"], line=dict(color=C.COLOR_OPT, dash="dash", width=3), annotation_text="Rangquotient q", annotation_position="top left")
    fig.add_vline(x=d["mean"], line=dict(color=C.COLOR_GREEDY, dash="dot", width=2), annotation_text="Mittel", annotation_position="top right")
    fig.update_xaxes(title_text="Greedy / Optimum", range=[0, 1.02])
    fig.update_yaxes(title_text="Läufe")
    return _base(fig, 320)


def build_maximal_chart(sizes):
    """Zahl der maximalen zulässigen Mengen je Größe."""
    fig = go.Figure(go.Bar(x=[str(s) for s in sizes], y=list(sizes.values()), marker_color=[C.COLOR_HIGH if s == max(sizes) else C.COLOR_LOW for s in sizes],
                           hovertemplate="Größe %{x}: %{y} Mengen<extra></extra>"))
    fig.update_xaxes(title_text="Größe der maximalen Menge", type="category")
    fig.update_yaxes(title_text="Zahl der maximalen Mengen")
    return _base(fig, 300)


def build_scaling_chart(rows):
    fig = go.Figure()
    families = []
    for r in rows:
        if r["family"] not in families:
            families.append(r["family"])
    colors = [C.COLOR_LINE, C.COLOR_LINE2, C.COLOR_HIGH]
    for family, color in zip(families, colors):
        sub = [r for r in rows if r["family"] == family]
        fig.add_trace(go.Scatter(x=[r["size"] for r in sub], y=[r["q"] for r in sub], mode="lines+markers", name=family, line=dict(color=color, width=3),
                                 hovertemplate="Größe %{x}: q = %{y:.3f}<extra></extra>"))
    fig.update_xaxes(title_text="Größe (Blätter, Kanten, kleine Gegenstände)", dtick=1)
    fig.update_yaxes(title_text="Rangquotient q", range=[0, 1.05])
    return _base(fig, 320)
