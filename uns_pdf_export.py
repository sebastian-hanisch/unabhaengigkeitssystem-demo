"""PDF-Export des aktuellen Systems (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

import uns_constants as C
from uns_evaluation import Analysis, Settings, de, gewicht, names, prozent, rank_text, verdict_greedy

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "×": "x", "≈": "~"}


def _s(text) -> str:
    out = str(text).replace("**", "")
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis, settings: Settings) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Unabhängigkeitssystem: Greedy gegen Optimum"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0, 5,
        _s(f"{C.SYSTEM_NAMES[settings.system]}; {a.inst.n} Standorte, Plan-Seed {settings.seed}; Gewichte: {C.WEIGHT_NAMES[settings.gewichte]}, Seed {settings.wseed}. {a.n_independent} zulässige Mengen."),
        new_x="LMARGIN", new_y="NEXT",
    )
    pdf.ln(2)
    pdf.multi_cell(0, 5, _s(verdict_greedy(a)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, _s(f"Greedy: {names(a, a.greedy_mask)} (Gewicht {gewicht(a.greedy_value)})"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, _s(f"Optimum: {names(a, a.opt_mask)} (Gewicht {gewicht(a.opt_value)}), Greedy erreicht {prozent(a.ratio)} %"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, _s(f"Rangquotient q = {de(a.q, 3)}. " + rank_text(a)), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    widths = (50, 30)
    for head, w in zip(("Element", "Gewicht"), widths):
        pdf.cell(w, 6, _s(head), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    for e in range(a.m):
        pdf.cell(widths[0], 5.5, _s(a.labels[e]), border=1)
        pdf.cell(widths[1], 5.5, _s(gewicht(a.weights[e])), border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Quelle: unabhaengigkeitssystem-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
