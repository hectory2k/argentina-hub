"""
verify_pipeline.py — Verifica integridad de artefactos en data/normalized/.

Chequea:
  - Que cada dataset esperado tenga su .parquet
  - Que ningún archivo esté vacío (0 registros)
  - Que los metadatos en staging tengan los campos obligatorios

Si algo falla, levanta SystemExit.
"""

import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parent.parent
NORMALIZED = ROOT / "data" / "normalized"
STAGING = ROOT / "data" / "staging"

DATASETS_EXPECTED = [
    "dpa",
    "censo_poblacion",
    "censo_hogares",
    "censo_viviendas",
    "indicadores",
]


def verify() -> None:
    """Ejecuta todas las verificaciones."""
    errors = []

    for name in DATASETS_EXPECTED:
        parquet_path = NORMALIZED / f"{name}.parquet"
        metadata_path = STAGING / f"{name}.metadata.json"

        # 1. El artefacto existe
        if not parquet_path.exists():
            errors.append(f"Falta artefacto: {parquet_path}")
            continue

        # 2. No está vacío
        try:
            df = pl.read_parquet(parquet_path)
            if df.is_empty():
                errors.append(f"Artefacto vacío: {parquet_path}")
        except Exception as e:
            errors.append(f"Error al leer {parquet_path}: {e}")

        # 3. Metadata existe y tiene campos obligatorios
        if metadata_path.exists():
            try:
                metadata = json.loads(metadata_path.read_text())
                required = ["dataset", "source_name", "record_count"]
                for field in required:
                    if field not in metadata:
                        errors.append(f"Metadata {name}: falta campo '{field}'")
            except json.JSONDecodeError as e:
                errors.append(f"Metadata {name}: JSON inválido ({e})")
        else:
            errors.append(f"Falta metadata: {metadata_path}")

    if errors:
        raise SystemExit("Verificación fallida:\n" + "\n".join(errors))

    print("Verificación completada. Todos los artefactos íntegros.")


if __name__ == "__main__":
    verify()
