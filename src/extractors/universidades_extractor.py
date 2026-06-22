"""
Universidades Extractor — Universidades argentinas.

Fuente: Paquete `argentina` (datos estáticos embebidos).
Estrategia: Extraer datos del módulo argentina.universidades.

Produce:
  - data/staging/universidades.csv
  - data/staging/universidades.metadata.json
"""

import polars as pl
from argentina.universidades import listar

from extractors.base import BaseExtractor


class UniversidadesExtractor(BaseExtractor):
    """Extrae datos de universidades argentinas."""

    DATASET_NAME = "universidades"

    def run(self) -> None:
        """Ejecuta la extracción."""
        unis = listar()
        data = [{
            "sigla": u.sigla,
            "nombre": u.nombre,
            "provincia_codigo": u.provincia_codigo,
            "provincia_nombre": u.provincia_nombre,
            "sede": u.sede,
            "anio_fundacion": u.anio_fundacion,
            "tipo": u.tipo,
        } for u in unis]

        df = pl.DataFrame(data)

        self._guardar_csv(df, self.DATASET_NAME)
        self._guardar_metadata(
            self.DATASET_NAME,
            source_name="Paquete argentina (PyPI)",
            source_url="https://pypi.org/project/argentina/",
            source_mode="live",
            record_count=len(df),
            fields=df.columns,
            reuse_policy={
                "status": "open-attribution",
                "license": "CC-BY",
                "license_url": "",
                "attribution_required": True,
                "redistribution_ok": True,
                "summary": "Datos de universidades argentinas.",
            },
        )
        print(f"Universidades → staging: {len(df)} registros")
