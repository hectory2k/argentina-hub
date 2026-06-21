"""
Google Sheets Extractor — Ingesta desde Google Sheets a staging.

Fuente: Google Sheets API vía gspread.
Estrategia: Leer múltiples pestañas, consolidar en un solo CSV limpio.

Produce:
  - data/staging/datos_sheets.csv
  - data/staging/datos_sheets.metadata.json

Uso:
  PYTHONPATH=src python -c "
  from extractors.google_sheets_extractor import GoogleSheetsExtractor
  e = GoogleSheetsExtractor(pestanas=['Hoja 1'])
  e.run()
  "
"""

import os
import pandas as pd
import polars as pl
import gspread
from dotenv import load_dotenv

from extractors.base import BaseExtractor

load_dotenv()


class GoogleSheetsExtractor(BaseExtractor):
    """Extrae datos desde Google Sheets y los guarda en staging."""

    DATASET_NAME = "datos_sheets"

    def __init__(self, spreadsheet_id: str = None, pestanas: list = None):
        super().__init__()
        self.spreadsheet_id = spreadsheet_id or os.getenv("SPREADSHEET_ID")
        self.pestanas = pestanas or []
        self.creds_path = self.root / "credenciales.json"

    def run(self) -> None:
        """Ejecuta la extracción completa."""
        if not self.spreadsheet_id:
            raise SystemExit(
                "SPREADSHEET_ID no configurado. Agregalo en .env:\n"
                "  echo 'SPREADSHEET_ID=tu_id' >> .env"
            )
        if not self.creds_path.exists():
            raise SystemExit(
                f"Credenciales no encontradas en {self.creds_path}.\n"
                "Bajá el JSON de service account desde Google Cloud Console."
            )

        # Conectar
        gc = gspread.service_account(filename=str(self.creds_path))
        doc = gc.open_by_key(self.spreadsheet_id)

        # Si no se especificaron pestañas, leer todas
        if not self.pestanas:
            self.pestanas = [ws.title for ws in doc.worksheets()]
            print(f"📋 {len(self.pestanas)} pestañas detectadas: {self.pestanas}")

        # Leer cada pestaña
        frames = []
        for pestana in self.pestanas:
            try:
                hoja = doc.worksheet(pestana)
                df_temp = pd.DataFrame(hoja.get_all_records())
                if not df_temp.empty:
                    df_temp["origen"] = pestana
                    frames.append(df_temp)
                    print(f"✅ {pestana}: {len(df_temp)} filas")
            except gspread.exceptions.WorksheetNotFound:
                print(f"⚠️ Pestaña '{pestana}' no encontrada, se saltea.")

        if not frames:
            raise SystemExit("❌ Ninguna pestaña contenía datos.")

        # Consolidar
        df = self._clean(df)
	df = pl.from_pandas(df)

	# Forzar códigos como string en Polars
	for col in ["prov_id", "depto_id"]:
	    if col in df.columns:
	        df = df.with_columns(pl.col(col).cast(pl.Utf8).str.zfill(5))

        # Guardar
        self._guardar_csv(df, self.DATASET_NAME)
        self._guardar_metadata(
            self.DATASET_NAME,
            source_name="Google Sheets",
            source_url=f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}",
            source_mode="live",
            record_count=len(df),
            fields=df.columns,
            pestanas=self.pestanas,
            reuse_policy={
                "status": "restricted",
                "license": "Verificar con el publicador de la planilla",
                "license_url": "",
                "attribution_required": True,
                "redistribution_ok": False,
                "summary": "Datos extraídos de Google Sheets. Redistribución sujeta a la licencia del publicador.",
            },
        )
        print(f"🎉 Google Sheets → staging: {len(df)} filas, {len(df.columns)} columnas")

            def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpieza KISS: columnas, duplicados, códigos INDEC."""
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
            .str.replace("á", "a", regex=False).str.replace("é", "e", regex=False)
            .str.replace("í", "i", regex=False).str.replace("ó", "o", regex=False)
            .str.replace("ú", "u", regex=False).str.replace("ñ", "n", regex=False)
        )
        df = df.drop_duplicates().reset_index(drop=True)
        for col in ["prov_id", "depto_id", "codigo_provincia", "codigo_departamento", "codigo_radio"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.split(".").str[0].str.strip()
                if "prov" in col or col.startswith("codigo_provincia"):
                    df[col] = df[col].str.zfill(2)
                elif "depto" in col or col.startswith("codigo_departamento"):
                    df[col] = df[col].str.zfill(5)
                df[col] = df[col].replace({"nan": "", "None": ""})
        return df

        # Eliminar duplicados
        df = df.drop_duplicates().reset_index(drop=True)

        # Forzar códigos INDEC como string (invariante 1)
        for col in ["codigo_provincia", "codigo_departamento", "codigo_radio"]:
            if col in df.columns:
                df[col] = (
                    df[col].astype(str)
                    .str.split(".").str[0]
                    .str.strip()
                    .replace({"nan": "", "None": ""})
                )

        return df
