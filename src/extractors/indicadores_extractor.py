"""
Indicadores Extractor — Indicadores Económicos de Argentina.

Fuente: api.estadisticasbcra.com.
Estrategia: API REST con token desde variable de entorno BCRA_API_KEY.

Produce:
  - data/staging/indicadores.csv
  - data/staging/indicadores.metadata.json
"""

import os
import polars as pl
import requests

from dotenv import load_dotenv
from extractors.base import BaseExtractor

load_dotenv()


class IndicadoresExtractor(BaseExtractor):
    """Extrae indicadores económicos desde api.estadisticasbcra.com."""

    DATASET_NAME = "indicadores"
    BASE_URL = "https://api.estadisticasbcra.com"

    INDICADORES = {
        "dolar_oficial": "usd_of",
        "dolar_blue": "usd",
        "inflacion_mensual": "inflacion_mensual_oficial",
        "inflacion_interanual": "inflacion_interanual_oficial",
        "uva": "uva",
        "reservas": "reservas",
        "tasa_badlar": "tasa_badlar",
        "merval": "merval",
    }

    def run(self) -> None:
        """Ejecuta la extracción de todos los indicadores."""
        token = os.getenv("BCRA_API_KEY")
        if not token:
            raise SystemExit(
                "BCRA_API_KEY no encontrada. Configurala en .env:\n"
                "  echo 'BCRA_API_KEY=tu_token' >> .env"
            )

        headers = {"Authorization": f"Bearer {token}"}
        frames = []

        for nombre, endpoint in self.INDICADORES.items():
            print(f"Extrayendo {nombre}...")
            df = self._fetch_indicador(nombre, endpoint, headers)
            if df is not None and not df.is_empty():
                frames.append(df)
                print(f"  → {len(df)} registros")

        if not frames:
            raise SystemExit("No se pudo extraer ningún indicador.")

        df = pl.concat(frames)

        self._guardar_csv(df, self.DATASET_NAME)
        self._guardar_metadata(
            self.DATASET_NAME,
            source_name="BCRA — api.estadisticasbcra.com",
            source_url="https://api.estadisticasbcra.com",
            source_mode="live",
            record_count=len(df),
            fields=df.columns,
            reuse_policy={
                "status": "public-api-review-terms",
                "license": "Datos públicos BCRA",
                "license_url": "https://www.bcra.gob.ar",
                "attribution_required": True,
                "redistribution_ok": True,
                "summary": "Datos públicos del BCRA vía api.estadisticasbcra.com.",
            },
        )

    def _fetch_indicador(self, nombre: str, endpoint: str, headers: dict) -> pl.DataFrame | None:
        """Obtiene la serie temporal de un indicador."""
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data:
                return None

            df = pl.DataFrame(data)
            df = df.rename({"d": "fecha", "v": "valor"})
            df = df.with_columns([
                pl.lit(nombre).alias("indicador"),
                pl.col("valor").cast(pl.Float64)
            ])
            return df.select(["fecha", "valor", "indicador"])

        except requests.RequestException as e:
            print(f"Error al obtener {nombre}: {e}")
            return None
