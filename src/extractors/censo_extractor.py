"""
Censo Extractor — Censo Nacional 2022 de Argentina.

Fuente: INDEC vía librería censoargentino.
Estrategia: Usar censoargentino.query() para obtener datos en formato tidy.
El extractor guarda los DataFrames ya limpios en staging.

Sub-tablas:
  - censo_poblacion (variables de persona)
  - censo_hogares (variables de hogar)
  - censo_viviendas (variables de vivienda)

Produce:
  - data/staging/censo_poblacion.csv + metadata.json
  - data/staging/censo_hogares.csv + metadata.json
  - data/staging/censo_viviendas.csv + metadata.json
"""

import polars as pl
import censoargentino

from extractors.base import BaseExtractor

class CensoExtractor(BaseExtractor):
    """Extrae datos del Censo 2022 vía censoargentino."""

    DATASET_NAME = "censo"

    # Variables representativas por entidad
    VARIABLES_POBLACION = [
        "PERSONA_P02",      # Sexo registrado al nacer
        "PERSONA_AESC",     # Años de escolaridad
        "PERSONA_CONDACT",  # Condición de actividad económica
    ]

    VARIABLES_HOGARES = [
        "HOGAR_EDUHOG",     # Clima educativo del hogar
        "HOGAR_H10",        # Material de pisos
        "HOGAR_H11",        # Material de cubierta exterior
    ]

    VARIABLES_VIVIENDAS = [
        "VIVIENDA_V01",     # Tipo de vivienda
        "VIVIENDA_V02",     # Condición de ocupación
        "VIVIENDA_V06",     # Cantidad de hogares
    ]

    def run(self) -> None:
        """Ejecuta la extracción para las tres sub-tablas."""

        configs = [
            ("censo_poblacion", self.VARIABLES_POBLACION),
            ("censo_hogares", self.VARIABLES_HOGARES),
            ("censo_viviendas", self.VARIABLES_VIVIENDAS),
        ]

        for dataset_name, variables in configs:
            print(f"Extrayendo {dataset_name} con {len(variables)} variables...")
            df = censoargentino.query(variables=variables)
            df = pl.from_pandas(df)

            self._guardar_csv(df, dataset_name)
            self._guardar_metadata(
                dataset_name,
                source_name="INDEC — Censo Nacional 2022",
                source_url="https://huggingface.co/datasets/pedroorden/censoargentino",
                source_mode="live",
                source_detail="Obtenido vía censoargentino (DuckDB + Parquet en Hugging Face)",
                record_count=len(df),
                fields=df.columns,
                variables=variables,
                reuse_policy={
                    "status": "open-attribution",
                    "license": "CC-BY",
                    "license_url": "https://creativecommons.org/licenses/by/4.0/",
                    "attribution_required": True,
                    "redistribution_ok": True,
                    "summary": "Datos públicos del INDEC. Ley 27.275.",
                },
            )
            print(f"  → {len(df)} registros")
