import pandas as pd
import numpy as np

rng = np.random.default_rng(42)

projectmanagers = [
    "Anna de Vries", "Bob Janssen", "Carla Smit", "David Bakker", "Eva Meijer",
    "Frank Visser", "Grace Mulder", "Hans Peters", "Iris van Dam", "Jan Hoekstra",
    "Karin Linden", "Lars Brouwer", "Mia Hendriks", "Niels Kuiper", "Olivia Groot"
]

directeuren = [
    "Sophie van den Berg", "Thomas Dijkstra", "Yvonne Kok", "Ruben Vermeer"
]

opdrachtgevers = [
    "Pieter Wolff", "Sandra Bosman", "Ahmed El Idrissi", "Lotte Verhoeven",
    "Mark Timmers", "Esther de Jong", "Wouter Bos", "Fatima Oulad"
]

types = ["uren", "regulier", "subsidie", "grondexploitatie"]

n = 250

projectnummers = [f"P-{i:04d}" for i in range(1, n + 1)]
projectnamen   = [f"Project {i}" for i in range(1, n + 1)]

start_timestamps = pd.to_datetime(
    rng.integers(
        pd.Timestamp("2020-01-01").value,
        pd.Timestamp("2028-12-31").value,
        n
    )
).normalize()

eind_timestamps = []
max_date = pd.Timestamp("2030-12-31")
for s in start_timestamps:
    delta = pd.Timedelta(days=int(rng.integers(30, 731)))
    eind_timestamps.append(min(s + delta, max_date))
eind_timestamps = pd.DatetimeIndex(eind_timestamps)

# --- Parquet 1: projecten ---
df = pd.DataFrame({
    "projectnummer":             projectnummers,
    "projectnaam":               projectnamen,
    "startdatum":                start_timestamps.date,
    "einddatum":                 [d.date() for d in eind_timestamps],
    "projectmanager":            rng.choice(projectmanagers, n),
    "type":                      rng.choice(types, n),
    "verantwoordelijke directeur": rng.choice(directeuren, n),
    "ambtelijk opdrachtgever":   rng.choice(opdrachtgevers, n),
})

df.to_parquet("projecten.parquet", index=False)
print(f"Aangemaakt: projecten.parquet ({len(df)} rijen, {len(df.columns)} kolommen)")

# --- Parquet 2: financiën ---
def rand_budget(low, high, size):
    # Round to nearest 5000
    return (rng.integers(low // 5000, high // 5000, size) * 5000).astype(float)

kostenbudget     = rand_budget(50_000, 2_000_000, n)
kosten           = kostenbudget * rng.uniform(0.5, 1.3, n)
opbrengstenbudget = rand_budget(10_000, 1_500_000, n)
opbrengsten      = opbrengstenbudget * rng.uniform(0.4, 1.2, n)

df2 = pd.DataFrame({
    "projectnummer":      projectnummers,
    "kostenbudget":       kostenbudget.round(2),
    "kosten":             kosten.round(2),
    "opbrengstenbudget":  opbrengstenbudget.round(2),
    "opbrengsten":        opbrengsten.round(2),
})

df2.to_parquet("financien.parquet", index=False)
print(f"Aangemaakt: financien.parquet ({len(df2)} rijen, {len(df2.columns)} kolommen)")

# --- Parquet 3: kostendragers ---
kostendragers = [
    "KD-001 Personeelskosten",
    "KD-002 Huisvesting",
    "KD-003 ICT & Licenties",
    "KD-004 Inhuur extern",
    "KD-005 Communicatie",
    "KD-006 Subsidies verstrekt",
    "KD-007 Grondaankopen",
    "KD-008 Bouw & Infra",
    "KD-009 Onderzoek",
    "KD-010 Juridische kosten",
    "KD-011 Opleidingen",
    "KD-012 Evenementen",
    "KD-013 Beheer openbare ruimte",
    "KD-014 Milieu & Duurzaamheid",
    "KD-015 Overige kosten",
]

budgethouders = [
    "Annemiek Prins", "Bas van Leeuwen", "Claudia Dekker",
    "Dennis Hofman", "Esther Nooij", "Floris Berger"
]

rng3 = np.random.default_rng(7)

def rand_amount(low, high, size):
    return (rng3.integers(low // 1000, high // 1000, size) * 1000).astype(float)

df3 = pd.DataFrame({
    "kostendrager":  kostendragers,
    "budgethouder":  rng3.choice(budgethouders, 15),
    "baten_2026":    rand_amount(0, 500_000, 15).round(2),
    "lasten_2026":   rand_amount(10_000, 1_500_000, 15).round(2),
})

df3.to_parquet("kostendragers.parquet", index=False)
print(f"Aangemaakt: kostendragers.parquet ({len(df3)} rijen, {len(df3.columns)} kolommen)")

# --- Parquet 4: kostendrager_projecten (koppeltabel) ---
# Elk project krijgt 1-3 kostendragers; alle 15 kostendragers komen voor.
rng4 = np.random.default_rng(99)

rows = []
# Zorg eerst dat elke kostendrager minstens één project heeft (round-robin)
shuffled = rng4.permutation(projectnummers)
for i, kd in enumerate(kostendragers):
    rows.append((kd, shuffled[i]))

# Voeg daarna willekeurige extra koppelingen toe zodat elk project
# gemiddeld 1-3 kostendragers heeft (totaal ~400-500 rijen)
for pnr in projectnummers:
    extra = int(rng4.integers(0, 3))  # 0, 1 of 2 extra kostendragers
    if extra:
        for kd in rng4.choice(kostendragers, extra, replace=False):
            rows.append((kd, pnr))

df4 = pd.DataFrame(rows, columns=["kostendrager", "projectnummer"])
df4 = df4.drop_duplicates().sort_values(["kostendrager", "projectnummer"]).reset_index(drop=True)

df4.to_parquet("kostendrager_projecten.parquet", index=False)
print(f"Aangemaakt: kostendrager_projecten.parquet ({len(df4)} rijen, {len(df4.columns)} kolommen)")

# --- Parquet 5: tijdschrijven ---
# 100 werknemers, weeknummers 2024-W01 t/m 2025-W52
# Elke werknemer schrijft op 1-6 projecten; max 36 uur/week totaal.
rng5 = np.random.default_rng(17)

werknemers = [f"W-{i:03d}" for i in range(1, 101)]

# Voornamen + achternamen voor leesbaarheid
voornamen = ["Emma","Liam","Olivia","Noah","Ava","Elijah","Sophia","Lucas","Isabella","Mason",
             "Mia","Ethan","Amelia","Aiden","Luna","Caden","Aria","Grayson","Chloe","Jackson",
             "Layla","Sebastian","Riley","Mateo","Zoey","Jack","Nora","Owen","Lily","Wyatt",
             "Eleanor","John","Hannah","David","Lillian","Joseph","Addison","Samuel","Aubrey",
             "Carter","Ellie","Luke","Stella","Julian","Natalie","Levi","Zoe","Isaac","Leah",
             "Anthony","Hazel","Dylan","Violet","Lincoln","Aurora","Jaxon","Savannah","Asher",
             "Audrey","Christopher","Brooklyn","Joshua","Bella","Andrew","Claire","Theodore",
             "Skylar","Caleb","Lucy","Ryan","Paisley","Nathan","Everly","Aaron","Anna","Isaiah",
             "Caroline","Thomas","Nova","Charles","Genesis","Josiah","Emilia","Christian","Kennedy",
             "Hunter","Samantha","Eli","Maya","Jonathan","Willow","Connor","Kinsley","Landon","Naomi"]
achternamen = ["Jansen","de Vries","van den Berg","van Dijk","Bakker","Janssen","Visser","Smit",
               "Meijer","de Boer","Mulder","de Groot","Bos","Vos","Peters","Hendriks","van Leeuwen",
               "Dekker","Brouwer","de Wit","Dijkstra","Smits","Jacobs","de Jong","van der Meer"]

werknemer_namen = {}
for i, w in enumerate(werknemers):
    vn = voornamen[i % len(voornamen)]
    an = achternamen[rng5.integers(0, len(achternamen))]
    werknemer_namen[w] = f"{vn} {an}"

# Wijs per werknemer 1-6 projecten toe
werknemer_projecten = {}
for w in werknemers:
    k = int(rng5.integers(1, 7))
    werknemer_projecten[w] = list(rng5.choice(projectnummers, k, replace=False))

# Genereer weeknummers: 2024-W01 t/m 2026-W52
import datetime
weeknummers = []
for jaar in [2024, 2025, 2026]:
    for wk in range(1, 53):
        weeknummers.append(f"{jaar}-W{wk:02d}")

# Bouw tijdschrijven-rijen
ts_rows = []
for w in werknemers:
    projecten_w = werknemer_projecten[w]
    np_w = len(projecten_w)
    for week in weeknummers:
        # ~75% kans dat er uren worden geschreven in deze week
        if rng5.random() > 0.75:
            continue
        # Totaal uren deze week: 8-36
        totaal = int(rng5.integers(8, 37))
        # Verdeel over projecten (Dirichlet-achtig via uniforme verdeling)
        cuts = sorted(rng5.integers(0, totaal + 1, np_w - 1).tolist()) if np_w > 1 else []
        grenzen = [0] + cuts + [totaal]
        uren_per_project = [grenzen[i+1] - grenzen[i] for i in range(np_w)]
        for pnr, uren in zip(projecten_w, uren_per_project):
            if uren > 0:
                ts_rows.append((w, werknemer_namen[w], week, pnr, uren))

df5 = pd.DataFrame(ts_rows, columns=["werknemer_id", "werknemer", "weeknummer", "projectnummer", "uren"])
df5 = df5.sort_values(["weeknummer", "werknemer_id", "projectnummer"]).reset_index(drop=True)

df5.to_parquet("tijdschrijven.parquet", index=False)
print(f"Aangemaakt: tijdschrijven.parquet ({len(df5)} rijen, {len(df5.columns)} kolommen)")
