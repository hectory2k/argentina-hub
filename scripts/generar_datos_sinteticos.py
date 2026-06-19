"""
generar_datos_sinteticos.py — Datos sintéticos para desarrollo y tests.

Genera CSVs de prueba en data/staging/ con la estructura esperada.
Ejecutar antes de build_dev_db.py cuando no hay fuentes reales disponibles.

Uso:
  python scripts/generar_datos_sinteticos.py
"""

from pathlib import Path
from datetime import datetime, timezone
import json

import polars as pl

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "data" / "staging"
STAGING.mkdir(parents=True, exist_ok=True)


def generar_dpa():
    """Genera una DPA sintética con 3 provincias."""
    df = pl.DataFrame({
        "codigo_provincia": ["02", "02", "06", "06", "10", "10"],
        "nombre_provincia": [
            "Ciudad Autónoma de Buenos Aires",
            "Ciudad Autónoma de Buenos Aires",
            "Buenos Aires",
            "Buenos Aires",
            "Córdoba",
            "Córdoba",
        ],
        "codigo_departamento": ["02007", "02007", "06028", "06028", "10014", "10014"],
        "nombre_departamento": [
            "Comuna 7",
            "Comuna 7",
            "La Plata",
            "La Plata",
            "Capital",
            "Capital",
        ],
        "codigo_radio": ["02007001", "02007002", "06028001", "06028002", "10014001", "10014002"],
        "nombre_localidad": [
            "Palermo",
            "Recoleta",
            "La Plata",
            "Tolosa",
            "Nueva Córdoba",
            "Alberdi",
        ],
    })

    # Generar nombre_localidad_clean
    df = df.with_columns(
        pl.col("nombre_localidad")
        .str.to_lowercase()
        .str.replace_all("á", "a")
        .str.replace_all("é", "e")
        .str.replace_all("í", "i")
        .str.replace_all("ó", "o")
        .str.replace_all("ú", "u")
        .str.replace_all("ü", "u")
        .str.replace_all("ñ", "n")
        .alias("nombre_localidad_clean")
    )

    path = STAGING / "dpa.csv"
    df.write_csv(path)

    metadata = {
        "dataset": "dpa",
        "source_name": "Datos sintéticos para desarrollo",
        "source_url": "generado localmente",
        "source_mode": "fallback",
        "refreshed_at_utc": datetime.now(timezone.utc).isoformat(),
        "record_count": len(df),
        "fields": df.columns,
        "reuse_policy": {
            "status": "open-attribution",
            "license": "CC0",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "attribution_required": False,
            "redistribution_ok": True,
            "summary": "Datos sintéticos para desarrollo.",
        },
    }
    (STAGING / "dpa.metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False))
    print(f"DPA sintética: {path} ({len(df)} registros)")


def generar_censo(tabla: str):
    """Genera datos sintéticos para una sub-tabla del censo."""
    df = pl.DataFrame({
        "codigo_provincia": ["02", "02", "06", "06", "10", "10"],
        "codigo_departamento": ["02007", "02007", "06028", "06028", "10014", "10014"],
        "total": [15000, 12000, 45000, 38000, 32000, 28000],
    })

    if tabla == "poblacion":
        df = df.with_columns([
            pl.Series("varones", [7200, 5800, 21800, 18400, 15500, 13500]),
            pl.Series("mujeres", [7800, 6200, 23200, 19600, 16500, 14500]),
        ])
    elif tabla == "hogares":
        df = df.with_columns([
            pl.Series("hogares_con_jefatura_femenina", [3200, 2800, 9800, 8200, 7100, 6200]),
        ])
    elif tabla == "viviendas":
        df = df.with_columns([
            pl.Series("viviendas_con_internet", [4100, 3500, 12100, 10200, 8900, 7600]),
            pl.Series("viviendas_con_gas_red", [4400, 3800, 13100, 11100, 9600, 8200]),
        ])

    dataset_name = f"censo_{tabla}"
    path = STAGING / f"{dataset_name}.csv"
    df.write_csv(path)

    metadata = {
        "dataset": dataset_name,
        "source_name": "Datos sintéticos para desarrollo",
        "source_url": "generado localmente",
        "source_mode": "fallback",
        "refreshed_at_utc": datetime.now(timezone.utc).isoformat(),
        "record_count": len(df),
        "fields": df.columns,
        "reuse_policy": {
            "status": "open-attribution",
            "license": "CC0",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "attribution_required": False,
            "redistribution_ok": True,
            "summary": "Datos sintéticos para desarrollo.",
        },
    }
    (STAGING / f"{dataset_name}.metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False)
    )
    print(f"Censo {tabla} sintético: {path} ({len(df)} registros)")


def generar_indicadores():
    """Genera indicadores económicos sintéticos."""
    fechas = [f"2024-{m:02d}-01" for m in range(1, 7)]
    df = pl.DataFrame({
        "fecha": fechas * 2,
        "indicador": ["dolar_oficial"] * 6 + ["inflacion"] * 6,
        "valor": [800.0, 820.0, 850.0, 880.0, 900.0, 920.0]
        + [20.0, 18.0, 15.0, 12.0, 10.0, 8.0],
    })

    path = STAGING / "indicadores.csv"
    df.write_csv(path)

    metadata = {
        "dataset": "indicadores",
        "source_name": "Datos sintéticos para desarrollo",
        "source_url": "generado localmente",
        "source_mode": "fallback",
        "refreshed_at_utc": datetime.now(timezone.utc).isoformat(),
        "record_count": len(df),
        "fields": df.columns,
        "reuse_policy": {
            "status": "open-attribution",
            "license": "CC0",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "attribution_required": False,
            "redistribution_ok": True,
            "summary": "Datos sintéticos para desarrollo.",
        },
    }
    (STAGING / "indicadores.metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False)
    )
    print(f"Indicadores sintéticos: {path} ({len(df)} registros)")


if __name__ == "__main__":
    print("Generando datos sintéticos...")
    generar_dpa()
    generar_censo("poblacion")
    generar_censo("hogares")
    generar_censo("viviendas")
    generar_indicadores()
    print("Listo. Ejecutá: python -m src.build_dev_db")
