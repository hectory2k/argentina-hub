"""
build_dev_db.py — Construye la base de datos normalizada.

Lee data/staging/, ejecuta validaciones, escribe artefactos en data/normalized/.
(Nombre heredado de Chile Hub. No implica entorno dev/prod separado.)

Artefactos producidos:
  - data/normalized/{dataset}.parquet
  - data/normalized/{dataset}.json
  - data/normalized/argentina_hub.duckdb
"""

import json
from pathlib import Path

import polars as pl

from validation import validate_dpa, validate_censo, validate_indicadores

# Configuración de datasets
DATASETS = [
    {
        "name": "dpa",
        "pk": "codigo_radio",
        "validator": validate_dpa,
    },
    {
        "name": "censo_poblacion",
        "pk": None,  # Los microdatos pueden no tener PK única simple
        "validator": validate_censo,
    },
    {
        "name": "censo_hogares",
        "pk": None,
        "validator": validate_censo,
    },
    {
        "name": "censo_viviendas",
        "pk": None,
        "validator": validate_censo,
    },
    {
        "name": "indicadores",
        "pk": None,
        "validator": validate_indicadores,
    },
    {
        "name": "datos_sheets",
        "pk": None,
        "validator": None,  # Sin validador por ahora
    },
    {
        "name": "timeseries",
        "pk": None,
        "validator": validate_indicadores,  # Mismo validador (fecha, valor, indicador)
    },
    {
        "name": "localidades",
        "pk": "id_localidad",
        "validator": None,
    },
    {
        "name": "universidades",
        "pk": "sigla",
        "validator": None,
    },
    {
        "name": "refes",
        "pk": "establecimiento_id",
        "validator": None,
    },
]

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "data" / "staging"
NORMALIZED = ROOT / "data" / "normalized"


def build() -> None:
    """Ejecuta el build completo: validar + generar artefactos."""
    NORMALIZED.mkdir(parents=True, exist_ok=True)

    for ds in DATASETS:
        name = ds["name"]
        csv_path = STAGING / f"{name}.csv"
        metadata_path = STAGING / f"{name}.metadata.json"

        if not csv_path.exists():
            print(f"Saltando {name}: no se encontró {csv_path}")
            continue

        print(f"Procesando {name}...")
        # Para datasets del censo, inferir todo como string
        if name.startswith("censo_") or name == "refes":
            df = pl.read_csv(csv_path, infer_schema_length=0)
        else:
            df = pl.read_csv(csv_path, schema_overrides={
                "codigo_provincia": pl.Utf8,
                "codigo_departamento": pl.Utf8,
                "codigo_radio": pl.Utf8,
            })
        metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}

        # Validar
        validator = ds["validator"]
        if validator:
            validator(df, metadata)

        # Escribir artefactos
        parquet_path = NORMALIZED / f"{name}.parquet"
        json_path = NORMALIZED / f"{name}.json"

        df.write_parquet(parquet_path)
        df.write_json(json_path)

        print(f"  → {parquet_path} ({len(df)} registros)")
        print(f"  → {json_path}")

    print("Build completado.")


if __name__ == "__main__":
    build()
