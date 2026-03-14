import pandas as pd
import numpy as np
from datetime import date

rng = np.random.default_rng(42)

projectmanagers = [
    "Anna de Vries", "Bob Janssen", "Carla Smit", "David Bakker", "Eva Meijer",
    "Frank Visser", "Grace Mulder", "Hans Peters", "Iris van Dam", "Jan Hoekstra",
    "Karin Linden", "Lars Brouwer", "Mia Hendriks", "Niels Kuiper", "Olivia Groot"
]

types = ["uren", "regulier", "subsidie", "grondexploitatie"]

n = 250

# Projectnummers: P-0001 t/m P-0250
projectnummers = [f"P-{i:04d}" for i in range(1, n + 1)]

# Projectnamen
projectnamen = [f"Project {i}" for i in range(1, n + 1)]

# Startdatum: willekeurig in 2020-2028
start_timestamps = pd.to_datetime(
    rng.integers(
        pd.Timestamp("2020-01-01").value,
        pd.Timestamp("2028-12-31").value,
        n
    )
).normalize()

# Einddatum: 30-730 dagen na startdatum, maar uiterlijk 2030-12-31
eind_timestamps = []
max_date = pd.Timestamp("2030-12-31")
for s in start_timestamps:
    delta = pd.Timedelta(days=int(rng.integers(30, 731)))
    e = s + delta
    eind_timestamps.append(min(e, max_date))
eind_timestamps = pd.DatetimeIndex(eind_timestamps)

df = pd.DataFrame({
    "projectnummer": projectnummers,
    "projectnaam": projectnamen,
    "startdatum": start_timestamps.date,
    "einddatum": [d.date() for d in eind_timestamps],
    "projectmanager": rng.choice(projectmanagers, n),
    "type": rng.choice(types, n),
})

df.to_parquet("projecten.parquet", index=False)
print(f"Aangemaakt: projecten.parquet ({len(df)} rijen, {len(df.columns)} kolommen)")
print(df.head())
