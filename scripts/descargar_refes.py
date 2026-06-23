"""
Descarga REFES 2026 de Datos Abiertos Salud → CSV para Argentina Hub.
"""

import requests
import urllib3
import pandas as pd
from pathlib import Path

urllib3.disable_warnings()

URL ="https://datos.salud.gob.ar/dataset/336cf4d9-447a-44c4-8e34-0ba1fc293d55/resource/d91c27de-e440-4cd8-8f4c-0b8a8fd8dfa6/download/establecimientos-asistenciales-asentados-registro-federal-refes-20260114.xlsx"

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "data" / "staging"
OUTPUT = STAGING / "refes.csv"

STAGING.mkdir(parents=True, exist_ok=True)

print("Descargando REFES 2026...")
r = requests.get(URL, verify=False, timeout=60)

if r.status_code != 200:
    print(f"Error {r.status_code}")
    print("Bajalo de https://datos.salud.gob.ar/dataset/listado-establecimientos-de-salud-asentados-en-el-registro-federal-refes")
    exit(1)

tmp = STAGING / "refes_temp.xlsx"
tmp.write_bytes(r.content)

df = pd.read_excel(tmp)
print(f"Columnas: {df.columns.tolist()}")
print(f"Filas: {len(df)}")

# Guardar CSV limpio
df.to_csv(OUTPUT, index=False)
tmp.unlink()
print(f"✅ REFES → {OUTPUT} ({len(df)} registros)")
