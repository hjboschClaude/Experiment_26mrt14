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
