"""Unabhängigkeitssysteme: wo Greedy scheitert und wie schlimm - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 2 der Reihe „Matroide und Submodularität“ (Bereich Kombinatorik). Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import uns_constants as C
from uns_algorithm import elements
from uns_evaluation import (
    Settings,
    analyse,
    de,
    gewicht,
    maximal_stats,
    names,
    play_result,
    prozent,
    rank_text,
    ratio_distribution,
    scaling_rows,
    verdict_distribution,
    verdict_greedy,
    verdict_maximal,
    verdict_play,
    verdict_scaling,
)
from uns_layout import dunkles_design, kopf_css
from uns_pdf_export import build_pdf
from uns_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    randomize_wseed,
    sidebar_presets,
    sync_query_params,
)
from uns_systems import budget_cap
from uns_visualization import build_maximal_chart, build_plan, build_ratio_histogram, build_scaling_chart

st.set_page_config(page_title="Unabhängigkeitssysteme – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner="Alle zulässigen Mengen aufzählen …")
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _distribution(settings):
    return ratio_distribution(settings)


@st.cache_data(show_spinner=False)
def _maximal(settings):
    return maximal_stats(settings)


@st.cache_data(show_spinner="Rangquotienten kleiner Systeme berechnen …")
def _scaling():
    return scaling_rows()


def _kind(system):
    return "knoten" if system == "standorte" else "kanten"


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in uns_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧱 Unabhängigkeitssysteme: wo Greedy scheitert und wie schlimm")
st.markdown(
    """
Ein **Unabhängigkeitssystem** ist eine Familie zulässiger Mengen, die mit jeder Menge auch alle ihre Teilmengen enthält: Wälder, Paarungen, Auswahlen innerhalb eines Budgets, Standorte ohne Nachbarn. **Greedy** nimmt die Elemente nach Gewicht absteigend und jedes, das zulässig bleibt. Es endet immer in einer **maximalen** Menge; dass es für alle Gewichte in einer **größten und besten** endet, gilt genau bei Matroiden. Wie schlimm es bei den anderen höchstens wird, misst eine Zahl, der **Rangquotient** q: Greedy erreicht mindestens q mal das Optimum, und das ist scharf.

Dies ist das **zweite Stück** der Reihe „Matroide und Submodularität“; Stück 1 hat gezeigt, dass Greedy mit einer Gradschranke kippt, dieses Stück fragt, wie schlimm das allgemein werden kann. Weiter unten: vier Experimente (🔬), eine **Spielwiese** mit eigenen Gewichten, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert Greedy auf einem System", expanded=True):
    st.markdown(
        """
1. **Zulässig** ist eine Menge, wenn sie zum System gehört. Das System ist nach unten abgeschlossen: Lässt man aus einer zulässigen Menge Elemente weg, bleibt sie zulässig.
2. **Greedy:** Elemente nach Gewicht ordnen (bei Gleichstand gewinnt die kleinere Nummer). Der Reihe nach jedes Element nehmen, das mit den schon genommenen zulässig bleibt. Das Ergebnis ist **maximal**: Kein weiteres Element passt mehr dazu.
3. **Maximal ist nicht größtmöglich.** Es kann kleinere maximale Mengen geben als die größte zulässige. Greedy kann in einer kleinen landen und dabei etwas Schweres gewählt haben, das mehrere gute blockiert.
4. **Rangquotient:** Für jede Teilmenge F der Grundmenge zählt, wie klein eine maximale zulässige Teilmenge von F sein kann (lr) gegen wie groß eine zulässige Teilmenge von F sein kann (ur). Der kleinste Wert von lr / ur über alle F ist q. Bei Matroiden ist q = 1.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Plan**")
    n = st.slider("Standorte (mit Depot A)", *bounds("n_slider"), key="n_slider", help="Wie viele Standorte der Plan hat. Bis 9 (16 mögliche Leitungen), damit alle zulässigen Mengen aufzählbar bleiben.")
    seed = st.number_input("Zufalls-Seed des Plans", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neuen Plan generieren", width="stretch", on_click=randomize_seed)
    st.markdown("**System**")
    system = st.selectbox("Zulässige Mengen", C.SYSTEMS, key="system_select", format_func=lambda k: C.SYSTEM_NAMES[k],
                          help="Was zulässig ist. Wald und das uniforme Matroid sind Matroide, die anderen nicht.")
    st.markdown("**Gewichte**")
    gewichte = st.selectbox("Gewichte der Elemente", C.WEIGHTS, key="gewichte_select", format_func=lambda k: C.WEIGHT_NAMES[k],
                            help="Zufall und ganze Zahlen ziehen die Gewichte aus dem Seed; scharf baut sie aus dem Rangquotienten, sodass Greedy so schlecht wie möglich abschneidet.")
    wseed = st.number_input("Zufalls-Seed der Gewichte", *bounds("wseed_input"), key="wseed_input", step=1, disabled=(gewichte == "scharf"),
                            help="Bei scharfen Gewichten ohne Wirkung: sie hängen nur vom System ab.")
    st.button("🎲 Neue Gewichte ziehen", width="stretch", on_click=randomize_wseed, disabled=(gewichte == "scharf"))

sync_query_params({"n_slider": int(n), "seed_input": int(seed), "system_select": system, "gewichte_select": gewichte, "wseed_input": int(wseed)})

settings = Settings(int(n), int(seed), system, gewichte, int(wseed))
a = _analysis(settings)
inst = a.inst
kind = _kind(system)
if system == "budget":
    texts = [f"{gewicht(w)} | Kosten {int(inst.edges[e][2])}" for e, w in enumerate(a.weights)]
else:
    texts = [gewicht(w) for w in a.weights]

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Greedy gegen Optimum")
st.caption(f"{C.SYSTEM_NAMES[system]}, {a.n_independent} zulässige Mengen aufgezählt. Zahlen an den {'Standorten' if kind == 'knoten' else 'Leitungen'}: Gewichte"
           + (f" und Kosten; Budget {budget_cap(inst)} (40 % der Kosten aller Leitungen)." if system == "budget" else "."))
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Greedy**")
    st.plotly_chart(build_plan(inst, kind, [("Greedy wählt", elements(a.greedy_mask, a.m), C.COLOR_GREEDY)], texts), width="stretch", key="map_greedy")
with col_b:
    st.markdown("**Optimum (alle zulässigen Mengen aufgezählt)**")
    st.plotly_chart(build_plan(inst, kind, [("Optimum wählt", elements(a.opt_mask, a.m), C.COLOR_OPT)], texts), width="stretch", key="map_opt")
st.caption(f"Greedy wählt: {names(a, a.greedy_mask)}. Optimum wählt: {names(a, a.opt_mask)}.")

m1, m2, m3 = st.columns(3)
# Delta immer als „mein Wert minus Referenz“. Hier wird maximiert: weniger Gewicht ist schlecht, also delta_color="normal" (negativ = rot).
if a.greedy_value >= a.opt_value - 1e-9:
    m1.metric("Gewicht von Greedy", gewicht(a.greedy_value), delta="so viel wie das Optimum", delta_color="off")
else:
    m1.metric("Gewicht von Greedy", gewicht(a.greedy_value), delta=f"{a.greedy_value - a.opt_value:+.3f} gegen das Optimum".replace(".", ","), delta_color="normal")
m2.metric("Gewicht des Optimums", gewicht(a.opt_value), delta=f"Greedy erreicht {prozent(a.ratio)} %", delta_color="off")
m3.metric("Rangquotient q", de(a.q, 3), delta="Garantie: Greedy ≥ q · Optimum", delta_color="off")

if st.button("📄 PDF des aktuellen Systems erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a, settings))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="unabhaengigkeitssystem.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie schlimm kann Greedy auf diesem System werden?")
kind_v, text_v = verdict_greedy(a)
getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Die schlimmste Teilmenge und der Rangquotient")
st.caption("Für jede Teilmenge F der Grundmenge: Wie klein kann eine maximale zulässige Teilmenge sein (lr), wie groß eine zulässige (ur)? Alle Teilmengen sind aufgezählt.")
st.markdown(rank_text(a))
if a.q < 1 - 1e-9:
    cl, cr = st.columns(2)
    f_list = elements(a.f_star, a.m)
    with cl:
        st.markdown(f"**Kleinste maximale Menge in F** ({a.lr} Elemente)")
        st.plotly_chart(build_plan(inst, kind, [("F", f_list, C.COLOR_F), ("kleinste maximale Menge", elements(a.low_mask, a.m), C.COLOR_LOW)], texts), width="stretch", key="map_low")
    with cr:
        st.markdown(f"**Größte zulässige Menge in F** ({a.ur} Elemente)")
        st.plotly_chart(build_plan(inst, kind, [("F", f_list, C.COLOR_F), ("größte zulässige Menge", elements(a.high_mask, a.m), C.COLOR_HIGH)], texts), width="stretch", key="map_high")
    st.caption("Blau: die Teilmenge F. Orange: die kleinste maximale zulässige Teilmenge von F (Greedy kann hier hängen bleiben). Grün: eine größte zulässige Teilmenge von F.")

st.subheader("🔬 Experiment 2: Im Schnitt harmlos, im schlimmsten Fall bei q")
st.caption(
    f"{C.DISTRIBUTION_RUNS} zufällige Gewichtsvektoren (bei „ganze Zahlen“ aus 1 bis 3, sonst zwischen 0 und 1) auf diesem System; für jeden Greedy gegen das aufgezählte Optimum."
)
dist = _distribution(settings)
st.plotly_chart(build_ratio_histogram(dist), width="stretch", key="hist_chart")
kind_v, text_v = verdict_distribution(dist)
getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 3: Maximal heißt nicht größtmöglich")
st.caption("Alle maximalen zulässigen Mengen nach Größe. Für jede gibt es Gewichte, bei denen Greedy genau diese Menge liefert.")
mx = _maximal(settings)
st.plotly_chart(build_maximal_chart(mx["sizes"]), width="stretch", key="maximal_chart")
kind_v, text_v = verdict_maximal(mx)
getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 4: Wie klein kann der Rangquotient werden?")
st.caption("Drei kleine Systemfamilien, deren Rangquotient aus allen Teilmengen berechnet wird: der Stern (unabhängige Menge), die Paarung auf einem Pfad und ein Rucksack mit einem großen Gegenstand.")
if st.button("📊 Rangquotienten berechnen", key="scaling_run"):
    st.session_state["scaling_done"] = True
if st.session_state.get("scaling_done"):
    rows = _scaling()
    st.plotly_chart(build_scaling_chart(rows), width="stretch", key="scaling_chart")
    st.dataframe(
        [{"Familie": r["family"], "Größe": r["size"], "q": de(r["q"], 3), "lr": r["lr"], "ur": r["ur"]} for r in rows],
        hide_index=True, width="stretch",
    )
    kind_v, text_v = verdict_scaling(rows)
    getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🛠️ Spielwiese: eigene Gewichte")
st.caption(f"Setzen Sie die Gewichte der {'Standorte' if kind == 'knoten' else 'Leitungen'} selbst (Startwerte: die Gewichte oben). Greedy und Optimum werden sofort neu bestimmt.")
play_key = f"play_edit_{system}_{settings.n}_{settings.seed}_{gewichte}_{settings.wseed}"
table = [{"Element": a.labels[e], "Gewicht": round(float(a.weights[e]), 3)} for e in range(a.m)]
edited = st.data_editor(
    table, key=play_key, hide_index=True, width="stretch", disabled=["Element"], num_rows="fixed",
    column_config={"Gewicht": st.column_config.NumberColumn("Gewicht", min_value=0.0, max_value=1000.0, step=0.001, format="%.3f")},
)
rows_play = edited.to_dict("records") if hasattr(edited, "to_dict") else list(edited)
play_weights = []
for row in rows_play:
    value = row.get("Gewicht")
    play_weights.append(0.0 if value is None or value != value else float(value))
if len(play_weights) == a.m:
    pr = play_result(settings, play_weights)
    st.caption(f"Greedy wählt: {names(a, pr['greedy_mask'])}. Optimum wählt: {names(a, pr['opt_mask'])}.")
    kind_v, text_v = verdict_play(pr)
    getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Grundmenge ist klein (höchstens 16 Elemente)** | Der Rangquotient ist hier durch Aufzählen aller Teilmengen bestimmt, optimale Mengen durch Aufzählen aller zulässigen Mengen. Bei größeren Systemen ist beides ein eigenes Problem (der Quotient ist dann nur noch abschätzbar). | Stück 17 (Verfahrenswahl) |
| **Greedy ist die Regel der Wahl** | Die Garantie q gilt für Greedy. Bessere Verfahren für dasselbe System (Matching, exakte Verfahren) ändern das Bild; Greedy ist hier der Maßstab, nicht das Ziel. | Stück 7 und 8 (Schnitt zweier Matroide) |
| **Gewichte sind nicht negativ und addieren sich** | Mit nichtlinearen Zielen (abnehmender Zusatznutzen) gilt die Garantie nicht, dort gilt eine andere (Submodularität). | Stück 11 |
| **Der Rangquotient ist ein Worst-Case-Wert** | Im Schnitt liegt Greedy meist viel näher am Optimum (Experiment 2), die Garantie sagt nur, dass es nie darunter fällt. | – |
| **Ein Plan, eine Gewichtsart je Lauf** | Die Systeme stehen auf einem zufälligen Leitungsnetz, die Gewichte sind zufällig oder konstruiert; echte Gewichte können anders liegen. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** eine endliche Grundmenge $E$, eine Familie $\mathcal{I} \subseteq 2^E$ mit $\emptyset \in \mathcal{I}$, die mit jeder Menge auch alle Teilmengen enthält, und Gewichte $w_e \ge 0$. **Gesucht** $I \in \mathcal{I}$ mit größtem $w(I) = \sum_{e \in I} w_e$.

| Symbol | Bedeutung |
|---|---|
| $E$ | Grundmenge (Leitungen oder Standorte) |
| $\mathcal{I}$ | zulässige Mengen (Unabhängigkeitssystem) |
| $\operatorname{ur}(F)$ | größte Zahl von Elementen einer zulässigen Teilmenge von $F$ |
| $\operatorname{lr}(F)$ | kleinste Zahl von Elementen einer **maximalen** zulässigen Teilmenge von $F$ |
| $q$ | Rangquotient |

**Greedy.** Ordne $E$ nach $(-w_e, e)$. Nimm $e$, wenn die bisher genommene Menge zusammen mit $e$ in $\mathcal{I}$ liegt.

**Rangquotient.** $q = \min \{ \operatorname{lr}(F) / \operatorname{ur}(F) : F \subseteq E,\ \operatorname{ur}(F) > 0 \}$. Es gilt $q \le 1$, und $q = 1$ genau dann, wenn alle maximalen zulässigen Teilmengen jeder Menge $F$ gleich groß sind (Matroid).

**Garantie.** Für alle Gewichte $w \ge 0$ gilt $w(\text{Greedy}) \ge q \cdot w(\text{OPT})$, und zu jedem System gibt es Gewichte, bei denen das Verhältnis beliebig nahe an $q$ herankommt. Diese Demo rechnet die Aussage an den gezeigten Systemen nach (keine Verletzung, scharfe Gewichte erreichen $q$ bis auf den Vorsprung $0{,}001$); bewiesen wird sie hier nicht.

**Literatur.** Jenkyns, T. A. (1976): *The efficacy of the „greedy“ algorithm*, Proc. 7th Southeastern Conf. on Combinatorics, Graph Theory and Computing, Utilitas Math., Winnipeg, 341–350. Korte, B. und Hausmann, D. (1978): *An analysis of the greedy heuristic for independence systems*, Annals of Discrete Mathematics 2, 65–74.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
