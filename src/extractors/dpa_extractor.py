"""
DPA Extractor — División Político-Administrativa de Argentina.

Fuente: Derivada de los datos del Censo 2022 vía censoargentino.
Estrategia: Extraer códigos y etiquetas únicos de provincia y departamento
desde data/normalized/censo_poblacion.parquet.

Produce:
  - data/staging/dpa.csv
  - data/staging/dpa.metadata.json
"""

import polars as pl

from extractors.base import BaseExtractor


class DPAExtractor(BaseExtractor):
    """Extrae y normaliza la DPA desde los datos del Censo 2022."""

    DATASET_NAME = "dpa"
    SOURCE_DATASET = "censo_poblacion"

    def run(self) -> None:
        """Ejecuta la extracción completa."""
        # 1. Leer datos del censo desde normalized/
        censo_path = self.root / "data" / "normalized" / f"{self.SOURCE_DATASET}.parquet"

        if not censo_path.exists():
            raise SystemExit(
                f"No se encontró {censo_path}. Ejecutá primero el extractor del censo y build."
            )

        df_censo = pl.read_parquet(censo_path)

        # 2. Extraer pares únicos provincia-departamento
        df_dpa = (
            df_censo
            .select([
                "valor_provincia",
                "etiqueta_provincia",
                "valor_departamento",
                "etiqueta_departamento",
            ])
            .unique()
            .sort(["valor_provincia", "valor_departamento"])
        )

        # 3. Renombrar a columnas canónicas
        df_dpa = df_dpa.rename({
            "valor_provincia": "codigo_provincia",
            "etiqueta_provincia": "nombre_provincia",
            "valor_departamento": "codigo_departamento",
            "etiqueta_departamento": "nombre_departamento",
        })

        # 4. Asegurar códigos como string (invariante #1)
        df_dpa = df_dpa.with_columns([
            pl.col("codigo_provincia").cast(pl.Utf8).str.zfill(2),
            pl.col("codigo_departamento").cast(pl.Utf8).str.zfill(5),
        ])

        # 5. Generar nombre_localidad_clean desde nombre_departamento (invariante #4)
        df_dpa = df_dpa.with_columns(
            pl.col("nombre_departamento")
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

        # 6. Guardar en staging
        self._guardar_csv(df_dpa, self.DATASET_NAME)
        self._guardar_metadata(
            self.DATASET_NAME,
            source_name="INDEC — Censo Nacional 2022 (vía censoargentino)",
            source_url="https://huggingface.co/datasets/pedroorden/censoargentino",
            source_mode="live",
            source_detail="DPA derivada de censo_poblacion.parquet (códigos INDEC únicos)",
            record_count=len(df_dpa),
            fields=df_dpa.columns,
            reuse_policy={
                "status": "open-attribution",
                "license": "CC-BY",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "attribution_required": True,
                "redistribution_ok": True,
                "summary": "Datos públicos del INDEC. Ley 27.275.",
            },
        )
        print(f"DPA generada: {len(df_dpa)} departamentos únicos")
