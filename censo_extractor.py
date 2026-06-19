"""
Censo Extractor — Censo Nacional 2022 de Argentina.

Fuente: INDEC vía librería censoargentino.
Estrategia: Delegar toda la limpieza, normalización y filtrado a censoargentino.
El extractor solo recibe DataFrames ya listos y los guarda en staging.

Sub-tablas:
  - censo_poblacion
  - censo_hogares
  - censo_viviendas

Produce:
  - data/staging/censo_poblacion.csv + metadata.json
  - data/staging/censo_hogares.csv + metadata.json
  - data/staging/censo_viviendas.csv + metadata.json
"""

import polars as pl

from .base import BaseExtractor


class CensoExtractor(BaseExtractor):
    """Extrae datos del Censo 2022 vía censoargentino."""

    DATASET_NAME = "censo"
    SUB_TABLAS = ["poblacion", "hogares", "viviendas"]

    def run(self) -> None:
        """Ejecuta la extracción para las tres sub-tablas."""
        import censoargentino

        for tabla in self.SUB_TABLAS:
            dataset_name = f"censo_{tabla}"

            # censoargentino entrega un DataFrame ya limpio y etiquetado
            df = censoargentino.cargar(tabla)
            df = pl.from_pandas(df) if hasattr(df, "to_pandas") else df

            self._guardar_csv(df, dataset_name)
            self._guardar_metadata(
                dataset_name,
                source_name="INDEC — Censo Nacional 2022",
                source_url="https://censo.gob.ar",
                source_mode="live",
                source_detail="Obtenido vía librería censoargentino (DuckDB + Parquet en Source.Coop)",
                record_count=len(df),
                fields=df.columns,
                reuse_policy={
                    "status": "open-attribution",
                    "license": "CC-BY",
                    "license_url": "https://creativecommons.org/licenses/by/4.0/",
                    "attribution_required": True,
                    "redistribution_ok": True,
                    "summary": "Datos públicos del INDEC. Ley 27.275.",
                },
            )
