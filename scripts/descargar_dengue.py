"""
Descarga datos de dengue y zika del SNVS 2.0 → CSV para Argentina Hub.
Fuente: https://datos.salud.gob.ar/dataset/vigilancia-de-dengue-y-zika
"""

import requests
import urllib3
import pandas as pd
import io
from pathlib import Path

urllib3.disable_warnings()

URL = "https://datos.salud.gob.ar/dataset/ceaa8e87-297e-4348-84b8-5c643e172500/resource/33e12e9f-1d14-4bc7-b34c-a1f88ab7b990/download/informacion-publica-dengue-zika-nacional-se-1-2025-a-se22-2026-2026-06-15.csv"
ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "data" / "staging"
OUTPUT = STAGING / "dengue.csv"

STAGING.mkdir(parents=True, exist_ok=True)

print("Descargando dengue SNVS 2.0...")
r = requests.get(URL, verify=False, timeout=60)
r.raise_for_status()

df = pd.read_csv(io.StringIO(r.text), sep=';', encoding='latin1', on_bad_lines='skip')
df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
df.to_csv(OUTPUT, index=False)
print(f"✅ Dengue → {OUTPUT} ({len(df)} registros, {df['cantidad'].sum()} casos)")
