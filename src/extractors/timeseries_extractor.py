"""
Timeseries Extractor — Series temporales desde múltiples fuentes.

Formato canónico: fecha | valor | indicador | unidad | frecuencia
Soporta: BCRA, Google Sheets, CSV local.

Produce:
  - data/staging/timeseries.csv
  - data/staging/timeseries.metadata.json
"""

import os
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import polars as pl
import requests
from dotenv import load_dotenv

from extractors.base import BaseExtractor

load_dotenv()


class TimeseriesExtractor(BaseExtractor):
    """Extrae series temporales de múltiples fuentes y las normaliza."""

    DATASET_NAME = "timeseries"

    def run(self) -> None:
        """Combina todas las fuentes configuradas."""
        frames = []

        # 1. BCRA
        bcra = self._from_bcra()
        if bcra is not None:
            frames.append(bcra)

        # 2. CSV local (si existe)
        csv_path = self.staging_dir / "timeseries_manual.csv"
        if csv_path.exists():
            csv_df = self._from_csv(csv_path)
            frames.append(csv_df)

        # 3. Google Sheets (si está configurado)
        if os.getenv("SPREADSHEET_ID"):
            sheets = self._from_sheets()
            if sheets is not None:
                frames.append(sheets)

        if not frames:
            raise SystemExit("❌ No hay series temporales disponibles.")

        df = pl.concat(frames)
        self._guardar_csv(df, self.DATASET_NAME)
        self._guardar_metadata(
            self.DATASET_NAME,
            source_name="Series temporales consolidadas",
            source_url="Múltiples fuentes",
            source_mode="live",
            record_count=len(df),
            fields=df.columns,
            indicadores=df["indicador"].unique().to_list(),
            reuse_policy={
                "status": "public-api-review-terms",
                "license": "Verificar por fuente",
                "license_url": "",
                "attribution_required": True,
                "redistribution_ok": True,
                "summary": "Series temporales consolidadas de múltiples fuentes públicas argentinas.",
            },
        )
        print(f"🎉 Timeseries → staging: {len(df)} registros, {len(df['indicador'].unique())} indicadores")

    # =========================================================================
    # Fuente 1: BCRA
    # =========================================================================
    BCRA_INDICADORES = {
        "dolar_oficial":    {"endpoint": "usd_of",                    "unidad": "ARS",        "frecuencia": "diaria",  "descripcion": "USD oficial minorista"},
        "dolar_blue":       {"endpoint": "usd",                       "unidad": "ARS",        "frecuencia": "diaria",  "descripcion": "USD libre"},
        "inflacion_mensual": {"endpoint": "inflacion_mensual_oficial","unidad": "porcentaje",  "frecuencia": "mensual", "descripcion": "Inflación mensual oficial"},
        "inflacion_interanual": {"endpoint": "inflacion_interanual_oficial", "unidad": "porcentaje", "frecuencia": "mensual", "descripcion": "Inflación interanual oficial"},
        "uva":              {"endpoint": "uva",                       "unidad": "ARS",        "frecuencia": "diaria",  "descripcion": "Unidad de Valor Adquisitivo"},
        "reservas":         {"endpoint": "reservas",                  "unidad": "USD",        "frecuencia": "diaria",  "descripcion": "Reservas internacionales"},
        "tasa_badlar":      {"endpoint": "tasa_badlar",               "unidad": "porcentaje",  "frecuencia": "diaria",  "descripcion": "Tasa BADLAR"},
        "merval":           {"endpoint": "merval",                    "unidad": "ARS",        "frecuencia": "diaria",  "descripcion": "Índice MERVAL"},
    }

    def _from_bcra(self) -> pl.DataFrame | None:
        """Extrae indicadores del BCRA."""
        token = os.getenv("BCRA_API_KEY")
        if not token:
            print("⚠️ BCRA_API_KEY no configurada, salteando BCRA.")
            return None

        headers = {"Authorization": f"Bearer {token}"}
        base_url = "https://api.estadisticasbcra.com"
        frames = []

        for nombre, info in self.BCRA_INDICADORES.items():
            try:
                r = requests.get(f"{base_url}/{info['endpoint']}", headers=headers, timeout=30)
                r.raise_for_status()
                data = r.json()
                if data:
                    df = pl.DataFrame(data).rename({"d": "fecha", "v": "valor"})
                    df = df.with_columns([
                        pl.lit(nombre).alias("indicador"),
                        pl.lit(info["unidad"]).alias("unidad"),
                        pl.lit(info["frecuencia"]).alias("frecuencia"),
                        pl.col("valor").cast(pl.Float64),
                    ])
                    frames.append(df)
                    print(f"  ✅ BCRA {nombre}: {len(df)} registros")
            except Exception as e:
                print(f"  ⚠️ BCRA {nombre}: {e}")

        return pl.concat(frames) if frames else None

    # =========================================================================
    # Fuente 2: CSV local
    # =========================================================================
    def _from_csv(self, path: Path, indicador: str = "manual", unidad: str = "") -> pl.DataFrame | None:
        """
        Lee un CSV con columnas: fecha, valor.
        Opcional: indicador, unidad.
        """
        try:
            df = pl.read_csv(path)
            # Forzar valor a Float64
            df = df.with_columns(pl.col("valor").cast(pl.Float64, strict=False))
            if "fecha" not in df.columns or "valor" not in df.columns:
                print(f"⚠️ {path}: falta columna 'fecha' o 'valor'")
                return None

            if "indicador" not in df.columns:
                df = df.with_columns(pl.lit(indicador).alias("indicador"))
            if "unidad" not in df.columns:
                df = df.with_columns(pl.lit(unidad).alias("unidad"))
            if "frecuencia" not in df.columns:
                df = df.with_columns(pl.lit("").alias("frecuencia"))

            print(f"  ✅ CSV {path.name}: {len(df)} registros")
            return df.select(["fecha", "valor", "indicador", "unidad", "frecuencia"])
        except Exception as e:
            print(f"  ⚠️ CSV {path}: {e}")
            return None

    # =========================================================================
    # Fuente 3: Google Sheets
    # =========================================================================
    def _from_sheets(self, indicador: str = "sheets", unidad: str = "") -> pl.DataFrame | None:
        """Lee una planilla con columnas fecha, valor."""
        try:
            import gspread

            creds = self.root / "credenciales.json"
            if not creds.exists():
                print("⚠️ credenciales.json no encontrado, salteando Sheets.")
                return None

            gc = gspread.service_account(filename=str(creds))
            doc = gc.open_by_key(os.getenv("SPREADSHEET_ID"))
            hoja = doc.sheet1
            df = pd.DataFrame(hoja.get_all_records())

            # Normalizar columnas
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
            if "fecha" not in df.columns or "valor" not in df.columns:
                print("⚠️ Sheets: falta columna 'fecha' o 'valor'")
                return None

            df = pl.from_pandas(df)
            if "indicador" not in df.columns:
                df = df.with_columns(pl.lit(indicador).alias("indicador"))
            if "unidad" not in df.columns:
                df = df.with_columns(pl.lit(unidad).alias("unidad"))
            if "frecuencia" not in df.columns:
                df = df.with_columns(pl.lit("").alias("frecuencia"))

            print(f"  ✅ Sheets: {len(df)} registros")
            return df.select(["fecha", "valor", "indicador", "unidad", "frecuencia"])
        except Exception as e:
            print(f"  ⚠️ Sheets: {e}")
            return None
