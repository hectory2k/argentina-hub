"""
Arsénico Extractor — Datos de arsénico en agua de Argentina.

Fuente: Mapa de Arsénico (Firebase Firestore público).
Estrategia: Leer documento data2 de la colección arsenic-map.

Produce:
  - data/staging/arsenico.csv
  - data/staging/arsenico.metadata.json
"""

import os
import requests
import polars as pl

from extractors.base import BaseExtractor
from dotenv import load_dotenv
load_dotenv()

class ArsenicoExtractor(BaseExtractor):
    """Extrae datos de arsénico en agua."""

    DATASET_NAME = "arsenico"
    URL = "https://firestore.googleapis.com/v1/projects/mapa-de-arsenico/databases/(default)/documents/arsenic-map/data2"
    API_KEY = os.getenv("FIREBASE_API_KEY")

    def run(self) -> None:
        """Ejecuta la extracción."""
        if not self.API_KEY:
            raise SystemExit("FIREBASE_API_KEY no encontrada. Agregala en .env")

        print("Descargando datos de arsénico...")
        r = requests.get(f"{self.URL}?key={self.API_KEY}", timeout=30)
        r.raise_for_status()
        data = r.json()

        fields = data.get("fields", {})
        puntos = []

        for idx, value in fields.items():
            f = value.get("mapValue", {}).get("fields", {})
            punto = {
                "id": idx,
                "nombre": f.get("nombre", {}).get("stringValue", ""),
                "tipo": f.get("tipo", {}).get("stringValue", ""),
                "latitud": f.get("ubicacion", {}).get("geoPointValue", {}).get("latitude"),
                "longitud": f.get("ubicacion", {}).get("geoPointValue", {}).get("longitude"),
                "concentracion": f.get("concentracion", {}).get("doubleValue") 
                    or f.get("concentracion", {}).get("integerValue"),
                "profundidad": f.get("profundidad", {}).get("integerValue"),
                "fecha": f.get("fecha", {}).get("timestampValue", ""),
            }
            puntos.append(punto)

        df = pl.DataFrame(puntos)
        self._guardar_csv(df, self.DATASET_NAME)
        self._guardar_metadata(
            self.DATASET_NAME,
            source_name="Mapa de Arsénico en Argentina",
            source_url="https://mapa-de-arsenico.web.app/",
            source_mode="live",
            record_count=len(df),
            fields=df.columns,
            reuse_policy={
                "status": "public-api-review-terms",
                "license": "Datos públicos del Mapa de Arsénico",
                "license_url": "https://mapa-de-arsenico.web.app/",
                "attribution_required": True,
                "redistribution_ok": True,
                "summary": "Mediciones de arsénico en agua de toda Argentina.",
            },
        )
        print(f"🎉 Arsénico → staging: {len(df)} puntos")
