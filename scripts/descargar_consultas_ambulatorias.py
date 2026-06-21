"""
Descarga consultas ambulatorias de Datos Abiertos Salud → CSV para TimeseriesExtractor.

Fuente: https://datos.salud.gob.ar/dataset/consultas-medicas-ambulatorias
Uso: python scripts/descargar_consultas_ambulatorias.py
"""

import requests
import urllib3
import pandas as pd
from pathlib import Path

urllib3.disable_warnings()

URL = "https://datos.salud.gob.ar/dataset/0c3cb8db-bc39-466d-a02e-dbb868124d3a/resource/14ee4960-d8bb-428c-b719-8129cabf654d/download/consultas_medicas_unidad_operativa_2013-2015-2017-2021.xlsx"
ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "data" / "staging"
OUTPUT = STAGING / "timeseries_manual.csv"

STAGING.mkdir(parents=True, exist_ok=True)

print("Descargando consultas ambulatorias...")
r = requests.get(URL, verify=False, timeout=60)

if r.status_code != 200:
    print(f"⚠️ Error {r.status_code}")
    print("  Bajalo de https://datos.salud.gob.ar/dataset/consultas-medicas-ambulatorias")
    print(f"  y guardalo como {OUTPUT}")
    exit(1)

tmp = STAGING / "consultas_temp.xlsx"
tmp.write_bytes(r.content)

df = pd.read_excel(tmp)
print(f"Columnas: {df.columns.tolist()}")
print(f"Filas: {len(df)}")
print(df.head(3))

# Convertir a formato tidy: fecha | valor | indicador
if any(str(c).isdigit() for c in df.columns):
    id_cols = [c for c in df.columns if not str(c).isdigit()]
    df = df.melt(id_vars=id_cols, var_name="fecha", value_name="valor")
    df["fecha"] = df["fecha"].astype(str) + "-01-01"  # Asumir 1° de enero del año
    df["indicador"] = "consultas_ambulatorias"

df.to_csv(OUTPUT, index=False)
tmp.unlink()
print(f"✅ Guardado en {OUTPUT} ({len(df)} filas)")

