"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

N_MIN, N_MAX, DEFAULT_N = 6, 9, 7           # Standorte inklusive Depot (Knoten A); bis 9, damit die Mengen aller Leitungen (höchstens 16) aufzählbar bleiben
SEED_MAX, DEFAULT_SEED = 999999, 8
DEFAULT_WSEED = 1                           # Zufallsstrom der Gewichte
HUB_FACTOR = 0.4                            # (nur für den Plan; hier ohne Nabe benutzt) Leitungen am Depot kosten 40 % der Entfernung
COST_SCALE = 100                            # Kosten einer Leitung = Entfernung auf dem Plan mal 100, auf ganze Zahlen gerundet
BUDGET_SHARE = 0.4                          # Budget-System: zulässig ist, was zusammen höchstens 40 % der Kosten aller Leitungen kostet
UNIFORM_K = 4                               # uniformes Matroid: höchstens 4 Leitungen
DELTA = 0.001                               # Vorsprung der scharfen Gewichte
DISTRIBUTION_RUNS = 1000                    # Gewichtsvektoren für die Verteilung des Verhältnisses
SCALING_STAR = tuple(range(3, 12))          # Blätter des Sterns
SCALING_PATH = tuple(range(2, 12))          # Kanten des Pfads (Paarung)
SCALING_KNAPSACK = tuple(range(2, 11))      # kleine Gegenstände neben dem einen großen

SYSTEMS = ("wald", "wald3", "wald2", "paarung", "budget", "standorte", "uniform")
SYSTEM_NAMES = {
    "wald": "Wald (Matroid)",
    "wald3": "Wald, höchstens 3 Leitungen je Standort",
    "wald2": "Wald, höchstens 2 Leitungen je Standort",
    "paarung": "Paarung (höchstens 1 Leitung je Standort)",
    "budget": "Budget-Auswahl (Rucksack auf den Leitungen)",
    "standorte": "Standorte ohne Nachbarn (unabhängige Menge)",
    "uniform": "höchstens 4 Leitungen (uniformes Matroid)",
}
SYSTEM_MATROIDS = ("wald", "uniform")
WEIGHTS = ("zufall", "ganz", "scharf")
WEIGHT_NAMES = {"zufall": "Zufall (zwischen 0 und 1)", "ganz": "ganze Zahlen 1 bis 3 (Gleichstände)", "scharf": "scharf (aus dem Rangquotienten)"}

COLOR_GREEDY = "#2F6B65"
COLOR_OPT = "#d95f02"
COLOR_LOW = "#d95f02"
COLOR_HIGH = "#1b9e77"
COLOR_F = "rgba(76,120,168,0.9)"
COLOR_OTHER = "rgba(150,150,150,0.55)"
COLOR_NODE = "#4c78a8"
COLOR_DEPOT = "#f0a30a"
COLOR_LINE = "#4c78a8"
COLOR_LINE2 = "#d95f02"

PRESETS = {
    "Standardfall (Voreinstellung)": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "wald", "gewichte": "zufall", "wseed": DEFAULT_WSEED},
    "Wald, höchstens 3 Leitungen, scharfe Gewichte": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "wald3", "gewichte": "scharf", "wseed": DEFAULT_WSEED},
    "Paarung": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "paarung", "gewichte": "zufall", "wseed": 6},
    "Standorte ohne Nachbarn": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "standorte", "gewichte": "zufall", "wseed": 8},
    "Budget-Auswahl (Rucksack)": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "budget", "gewichte": "zufall", "wseed": DEFAULT_WSEED},
}
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "Wald mit zufälligen Gewichten: ein Matroid, Greedy ist optimal.",
    "Wald, höchstens 3 Leitungen, scharfe Gewichte": "Dieselbe Regel mit Gradschranke 3 und Gewichten, die aus dem Rangquotienten gebaut sind: Greedy erreicht nur gut die Hälfte.",
    "Paarung": "Höchstens eine Leitung je Standort, zufällige Gewichte: Greedy bleibt hier unter dem Optimum.",
    "Standorte ohne Nachbarn": "Zwei durch eine mögliche Leitung verbundene Standorte dürfen nicht beide gewählt werden; zufällige Gewichte: Greedy bleibt hier unter dem Optimum.",
    "Budget-Auswahl (Rucksack)": "Leitungen, die zusammen höchstens 40 % der Gesamtkosten kosten dürfen: ein Rucksack.",
}
