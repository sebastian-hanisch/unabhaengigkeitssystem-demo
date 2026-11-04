# Unabhängigkeitssysteme: wo Greedy scheitert und wie schlimm – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-unabhaengigkeitssystem-demo.streamlit.app/)** -->

Zweites Stück der Reihe **Matroide und Submodularität** (Bereich Kombinatorik) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Ein **Unabhängigkeitssystem** ist eine Familie zulässiger Mengen, die mit jeder Menge auch alle Teilmengen enthält: Wälder, Paarungen, Auswahlen innerhalb eines Budgets, Standorte ohne Nachbarn. **Greedy** nimmt die Elemente nach Gewicht absteigend und jedes, das zulässig bleibt; es endet in einer **maximalen** Menge; dass es für alle Gewichte in einer größten und besten endet, gilt genau bei Matroiden. Wie schlimm es sonst höchstens wird, misst der **Rangquotient** q: Greedy erreicht mindestens q mal das Optimum, und die Schranke ist scharf.

**Einordnung in die Reihe:** Nachfolger von [greedy-austausch-demo](../greedy-austausch-demo) (Stück 1: warum Kruskal gewinnt und dass Greedy mit einer Gradschranke kippt). Dieses Stück hebt die Frage auf alle Systeme. Vorgriff: Stück 3 (das Matroid als Struktur, bei der q = 1 gilt) und Stück 5 (Greedy genau dann optimal für alle Gewichte, wenn Matroid). Nachbarn: [greedy-matching-demo](../greedy-matching-demo) (Greedy-Paarung als Einzelfall mit Beweisskizze der Hälfte), [constrained-mst-demo](../constrained-mst-demo) und [cmst-demo](../cmst-demo) (gradbeschränkte und kapazitierte Spannbäume mit Lösungsverfahren).

## Warum dieses Problem

Stück 1 hat gezeigt, dass dieselbe Greedy-Regel auf dem Spannbaum optimal ist und mit einer Gradschranke nicht mehr. Hier die allgemeine Frage: **Wie schlimm kann es werden, und woran sieht man es?** Die Antwort ist eine Zahl, die man aus dem System allein ausrechnen kann: für jede Teilmenge F der Grundmenge das Verhältnis der kleinsten maximalen zulässigen Teilmenge (lr) zur größten zulässigen Teilmenge (ur); der kleinste Wert über alle F ist der Rangquotient q. Im Schnitt liegt Greedy meist weit besser als q, im schlimmsten Fall genau bei q; und q kann beliebig klein werden.

## Befunde und Korrekturen gegenüber dem Plan

- **Hook präzisiert:** Der Plan (`PLAN-02-unabhaengigkeitssysteme.md` im Planungsordner der Linie) sprach vom „Quotienten kleinster zu größter maximaler Menge“. Der Rangquotient ist das Minimum über **alle Teilmengen** F, nicht nur über die ganze Grundmenge: Beim Wald mit höchstens 3 Leitungen je Standort haben alle 152 maximalen Mengen sechs Leitungen, und q ist trotzdem 0,6.
- **Vier Experimente plus Hauptansicht:** Die fünf geplanten Prüfungen (Greedy gegen Optimum mit den Gewichtsarten, Rangquotient, Schnitt gegen schlimmsten Fall, maximal gegen größtmöglich, Skalierung) stehen als Hauptansicht „Greedy gegen Optimum“ und vier nummerierte Experimente. Die Gewichte „von Hand“ stehen in der Spielwiese.
- **Spielwiese als Tabelle:** Die Gewichte werden in einer Tabelle (`st.data_editor`) gesetzt. Die Auswertung ist als reine Funktion getestet; die Tabelle selbst ist mit dem Test-Rahmen der Oberfläche nicht ansprechbar (nicht mit echter Eingabe getestet).
- **Paarung und Standorte:** Greedy-Paarung hat `greedy-matching-demo` schon mit Beweisskizze der Hälfte; hier ist die Paarung eines von sieben Systemen; ihr Rangquotient ist 1/2.

## Modell

Die Systeme stehen auf einem **Leitungsnetz** wie in Stück 1: n Standorte (Knoten A ist das Depot in der Mitte, die übrigen liegen zufällig) und min(n(n − 1)/2, 2n − 2) mögliche Leitungen; die Kosten einer Leitung sind ihre Länge mal 100, auf ganze Zahlen gerundet. Sieben Systeme:

- **Wald:** Leitungen ohne Kreis (Matroid).
- **Wald mit höchstens 3 oder 2 Leitungen je Standort.**
- **Paarung:** höchstens eine Leitung je Standort.
- **Budget-Auswahl:** Leitungen, die zusammen höchstens 40 % der Kosten aller Leitungen kosten (ein Rucksack; die Gewichte sind der Nutzen, die Kosten die Größe).
- **Standorte ohne Nachbarn:** Grundmenge sind die Standorte; zwei durch eine mögliche Leitung verbundene Standorte dürfen nicht beide gewählt werden.
- **Höchstens 4 Leitungen** (uniformes Matroid, Kontrolle).

Gewichte: zufällig zwischen 0 und 1, ganze Zahlen 1 bis 3 (mit Gleichständen) oder **scharf**: aus der schlimmsten Teilmenge F gebaut (1,001 auf einer kleinsten maximalen Teilmenge von F, 1 auf dem Rest von F, 0 sonst). Die Aufgabe ist die **Maximierung** des Gesamtgewichts. Formeln stehen im 📐-Expander der App.

## Methodik

- **Greedy:** Elemente nach (Gewicht absteigend, Index aufsteigend), jedes nehmen, das zulässig bleibt (`uns_algorithm.py`, `System.greedy`).
- **Aufzählen:** alle zulässigen Mengen als Bitmasken (höchstens 2^16); daraus das Optimum (`System.opt`) und die maximalen Mengen.
- **Rangquotient:** ur(F) für alle Teilmengen per Rekursion, lr(F) über alle zulässigen Mengen I und die Mengen F mit I ⊆ F und F ohne ein Element, das zu I passt (`System._ranks`); q ist das Minimum von lr/ur.
- **Verteilung:** 1000 zufällige Gewichtsvektoren je Lauf, Greedy gegen das aufgezählte Optimum.
- **Skalierung:** Stern, Paarung auf einem Pfad und Rucksack mit einem großen Gegenstand, jeweils mit dem Rangquotienten aus allen Teilmengen.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py` und werden dort mit den Funktionen der App nachgerechnet. Plan: 7 Standorte, 12 mögliche Leitungen, Seed 8; Gewichte nach Seed 1.

| System | zulässige Mengen | Rangquotient q | scharfe Gewichte: Greedy / Optimum | Zufallsgewichte (1000): Greedy nicht optimal, Mittel, schlechtester Lauf |
|---|---|---|---|---|
| Wald (Matroid) | 1316 | **1** | 1,0000 | 0 von 1000, 100,0 %, 100,0 % |
| Wald, höchstens 3 Leitungen je Standort | 1238 | **0,6** | 0,6005 | 77, 99,7 %, 86,3 % |
| Wald, höchstens 2 Leitungen je Standort | 690 | **0,6** | 0,6004 | 450, 97,1 %, 77,7 % |
| Paarung | 60 | **0,5** | 0,5005 | 389, 95,3 %, 63,6 % |
| Budget-Auswahl (40 % der Kosten) | 1093 | **2/3** | 0,6671 | 401, 97,5 %, 79,0 % |
| Standorte ohne Nachbarn | 19 | **1/3** | 0,3337 | 327, 93,8 %, 37,1 % |
| höchstens 4 Leitungen (uniformes Matroid) | 794 | **1** | 1,0000 | 0 von 1000, 100,0 %, 100,0 % |

| Frage | Befund |
|---|---|
| **Standardfall** (Wald, Zufallsgewichte): Ist Greedy optimal? | Ja: Greedy und Optimum haben beide Gewicht **4,052**; q = 1; alle **180** maximalen Mengen haben 6 Leitungen. |
| **Garantie verletzt?** (7 Systeme × 2 Gewichtsarten × 1000 Vektoren auf dem Plan) | **0 Verletzungen** der Garantie Greedy ≥ q · Optimum. |
| **Schranke scharf?** | Bei den 5 Nicht-Matroiden liegt Greedy / Optimum mit den scharfen Gewichten höchstens 0,0006 über q; bei den beiden Matroiden genau 1. |
| **Preset „Wald, höchstens 3 Leitungen, scharfe Gewichte“** | Greedy erreicht **3,003 von 5,001**, **60,0 %** des Optimums, bei q = 0,6. |
| **Preset „Paarung“** (Zufallsgewichte, Seed 6) | Greedy 1,624 von 2,355: **69,0 %** (Garantie 50 %). |
| **Preset „Standorte ohne Nachbarn“** (Zufallsgewichte, Seed 8) | Greedy 1,084 von 1,914: **56,6 %** (Garantie 33,3 %). |
| **Preset „Budget-Auswahl“** (Zufallsgewichte, Seed 1) | Greedy 3,416 von 3,655: **93,5 %** (Garantie 66,7 %). |
| **Maximal, aber nicht größtmöglich** (Plan, Zahl der maximalen Mengen je Größe) | Wald: 180 mit 6. Wald mit Schranke 3: 152 mit 6. Wald mit Schranke 2: **34 mit 5 und 24 mit 6**. Paarung: 2 mit 2 und 16 mit 3. Budget: 15 mit 4, 128 mit 5, 53 mit 6. Standorte: 4 mit 2 und 2 mit 3. Uniform: 495 mit 4. |
| **Wie klein kann q werden?** (Skalierung) | Stern mit k Blättern: q = **1/k** für k = 3 bis 11. Rucksack mit einem Gegenstand der Größe k und k der Größe 1: q = 1/k für k = 2 bis 10. Paarung auf einem Pfad: q = 1 bei 2 Kanten, **1/2** bei 3 bis 11 Kanten (nach dem bekannten Satz für Paarungen auch darüber hinaus). |

## Ehrliche Grenzen

- **Kleine Grundmengen.** Höchstens 16 Elemente, damit alle Teilmengen und alle zulässigen Mengen aufgezählt werden können. Der Rangquotient ist hier exakt; bei großen Systemen wäre er nur noch abschätzbar.
- **Die Garantie ist als Satz bekannt, hier nur nachgerechnet.** Keine Verletzung in den gemessenen Läufen und Schärfe bis auf den Vorsprung 0,001 beweisen den Satz nicht (Jenkyns 1976, Korte und Hausmann 1978; die Quellen wurden nur über Zusammenfassungen eingesehen).
- **Worst Case gegen Schnitt.** Die Mittelwerte (93,8 % bis 99,7 % bei den Nicht-Matroiden) gelten für diese Gewichtsverteilungen, nicht allgemein. Echte Gewichte können anders liegen, und beim Stern liegt der Mittelwert mit ganzen Zahlen deutlich tiefer (siehe App, Experiment 2).
- **Ein Plan, wenige Systeme.** Die Systeme stehen auf einem zufälligen Leitungsnetz und einer Budget-Regel (40 %). Andere Budgets, andere Pläne und andere Systeme sind nicht gemessen.
- **Greedy ist der Maßstab, nicht das Ziel.** Für Paarung und Wald gibt es exakte Verfahren; sie sind hier nicht gezeigt.
- **Gewichte von Hand:** Die Tabelle der Spielwiese ist mit dem Test-Rahmen der Oberfläche nicht ansprechbar; getestet ist die Auswertung.

## Verifikation

- **Kern:** Greedy, Optimum, Rangquotient und scharfe Gewichte gegen Handrechnung auf vier kleinen Systemen (Paarung auf Pfad, Stern, Rucksack, uniformes Matroid, `tests/conftest.py`); Randfälle: ein Element, ein gesperrtes Element, zwei Elemente, alle Gewichte 0, ungültige Systeme (`tests/test_edge_cases.py`).
- **Orakel** (`tests/test_oracle_unabhaengigkeitssystem.py`): lr, ur und q direkt über alle Paare (F, I) auf 60 zufälligen Systemen; Optimum durch Aufzählen; networkx für größten Spannbaum, maximales Matching und gewichtete Clique im Komplement (unabhängige Standorte); Rucksack-Dynamik für das Budget-System; Garantie und Schärfe auf zufälligen Systemen.
- **Eigenschaften** (`tests/test_properties.py`): Garantie nie verletzt, scharfe Gewichte erreichen q, Greedy ist immer zulässig und maximal, jede maximale Menge ist ein Greedy-Ergebnis für passende Gewichte, q ist unabhängig von der Reihenfolge der Elemente, gleiche Ergebnisse in zwei Prozessen mit verschiedener Hash-Reihenfolge.
- **Verdikte und Presets:** jeder Zweig und jede Zahl der Verdikte an handgesetzten Werten; jedes Preset zeigt den versprochenen Effekt.
- **Zahlen aus dieser README:** `tests/test_claims.py`.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an den Grenzen), Experimente, Permalink, PDF; Layout (Kopf, Schnellstart, Hervorhebung) und Footer.
- **Umfang:** 120 Tests (`pytest --collect-only -q tests`), seriell etwa eine Minute.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Oberfläche: Greedy gegen Optimum, Kernfrage, vier Experimente, Spielwiese, Grenzen, Formeln |
| `uns_constants.py` | Reglergrenzen, Systeme und ihre Namen, Messreihen-Parameter, Farben, Presets |
| `uns_scenario.py` | Plan: Standorte, mögliche Leitungen, Kosten (wie in Stück 1) |
| `uns_algorithm.py` | Kern: Unabhängigkeitssystem auf Bitmasken, Greedy, Optimum, Rangquotient, scharfe Gewichte |
| `uns_systems.py` | die sieben Systeme auf dem Plan, Gewichte, kleine Systeme für die Skalierung |
| `uns_evaluation.py` | Kennzahlen, Verteilung, Skalierung, Spielwiese, Verdikte |
| `uns_visualization.py` | Plan, Histogramm, Balken, Skalierung |
| `uns_presets.py` | Permalink, Presets, Zufalls-Seeds |
| `uns_layout.py` | fester Kopf |
| `uns_pdf_export.py` | PDF des aktuellen Systems |
| `tests/` | Kern, Orakel, Eigenschaften, Verdikte, Presets, Claims, Randfälle, Oberfläche, Layout, Footer, Importe |

## Bewusst nicht umgesetzt

- Der Beweis der Garantie und die Umkehrung „Greedy genau dann optimal, wenn Matroid“ (Stück 5), die Matroid-Axiome (Stück 3).
- Größere Systeme als 16 Elemente und ein Schätzer für den Rangquotienten.
- Gewichte, die sich nicht addieren (abnehmender Zusatznutzen): dafür gilt eine andere Garantie (Stück 11).
- Exakte Verfahren für Paarung und Wald (Stück 7 und 8, Schnitt zweier Matroide).
- Erklärseite „verständlich erklärt“ und Website-Einbindung (erst mit der vollständigen Linie).

## Lokal ausführen

```bash
pip install -r requirements.txt
streamlit run app.py
```

Tests: `pip install -r requirements-dev.txt`, dann `python -m pytest tests -q`. Die CI läuft mit Python 3.12 (`.github/workflows/tests.yml`); die in Streamlit Cloud eingestellte Python-Version ist beim Deploy zu nennen.

Gebaut mit Streamlit, Plotly, numpy und fpdf2.

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Matroide: vom Spannbaum zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-matroide.html).
