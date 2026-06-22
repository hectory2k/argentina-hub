"""
Localidades Extractor — Localidades argentinas con códigos postales.

Fuente: Correo Argentino (API pública de CPA).
Estrategia: POST iterativo por provincia.

Produce:
  - data/staging/localidades.csv
  - data/staging/localidades.metadata.json
"""

import polars as pl
import requests

from extractors.base import BaseExtractor


class LocalidadesExtractor(BaseExtractor):
    """Extrae localidades y códigos postales de Correo Argentino."""

    DATASET_NAME = "localidades"
    URL = "https://www.correoargentino.com.ar/sites/all/modules/custom/ca_forms/api/wsFacade.php"
    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    PROVINCIAS = {
        "02": "C", "06": "B", "10": "K", "14": "X", "18": "W",
        "22": "H", "26": "U", "30": "E", "34": "P", "38": "Y",
        "42": "L", "46": "F", "50": "M", "54": "N", "58": "Q",
        "62": "R", "66": "A", "70": "J", "74": "D", "78": "Z",
        "82": "S", "86": "G", "90": "T", "94": "V",
    }

    def run(self) -> None:
        """Ejecuta la extracción para todas las provincias."""
        todas = []

        for codigo_indec, letra_correo in self.PROVINCIAS.items():
            print(f"Extrayendo provincia {codigo_indec}...")
            data = f"action=localidades&localidad=none&calle=&altura=&provincia={letra_correo}"
            try:
                r = requests.post(self.URL, headers=self.HEADERS, data=data, timeout=30)
                r.raise_for_status()
                r.encoding = "utf-8-sig"
                localidades = r.json()
                if not localidades:
                    print(f"  → 0 localidades")
                    continue
                for loc in localidades:
                    loc["codigo_provincia"] = codigo_indec
                todas.extend(localidades)
                print(f"  → {len(localidades)} localidades")
            except Exception as e:
                print(f"  ⚠ Error: {e}")

        df = pl.DataFrame(todas)
        df = df.rename({
            "id": "id_localidad",
            "nombre": "localidad",
            "partido": "departamento",
            "municipio": "municipio",
            "cp": "codigo_postal",
            "latitud": "latitud",
            "longitud": "longitud",
        })

        self._guardar_csv(df, self.DATASET_NAME)
        self._guardar_metadata(
            self.DATASET_NAME,
            source_name="Correo Argentino — API de CPA",
            source_url="https://www.correoargentino.com.ar/formularios/cpa",
            source_mode="live",
            record_count=len(df),
            fields=df.columns,
            reuse_policy={
                "status": "public-api-review-terms",
                "license": "Datos públicos de Correo Argentino",
                "license_url": "https://www.correoargentino.com.ar",
                "attribution_required": True,
                "redistribution_ok": True,
                "summary": "Localidades argentinas con códigos postales.",
            },
        )
        print(f"🎉 Localidades → staging: {len(df)} registros")
