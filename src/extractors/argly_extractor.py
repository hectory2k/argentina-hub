"""
Argly Extractor — Consume la API de Argly y guarda en staging.
Fuente: https://api.argly.com.ar (William López)
Produce: data/staging/argly.csv + metadata.json
"""

import requests
import polars as pl
from extractors.base import BaseExtractor


class ArglyExtractor(BaseExtractor):
    DATASET_NAME = "argly"
    BASE_URL = "https://api.argly.com.ar/v1"

    INDICADORES_SIMPLES = ["icl", "cer", "uva", "uvi", "smvm", "ipc", "riesgo-pais"]

    PROVINCIAS = ["chaco", "formosa", "corrientes", "misiones", "buenos-aires",
                  "cordoba", "santa-fe", "mendoza", "tucuman", "salta"]
    COMBUSTIBLES = ["Nafta Súper", "Nafta Premium", "Gasoil Grado 2", "Gasoil Grado 3"]

    def run(self):
        frames = []

        for nombre in self.INDICADORES_SIMPLES:
            print(f"Extrayendo {nombre}...")
            df = self._fetch_simple(nombre)
            if df is not None:
                frames.append(df)

        print("Extrayendo combustibles...")
        df_comb = self._fetch_combustibles()
        if df_comb is not None:
            frames.append(df_comb)

        print("Extrayendo combustibles promedio...")
        df_prom = self._fetch_combustibles_promedio()
        if df_prom is not None:
            frames.append(df_prom)

        if not frames:
            print("⚠ No se extrajo ningún dato")
            return

        df = pl.concat(frames, how="diagonal")
        self._guardar_csv(df, self.DATASET_NAME)
        self._guardar_metadata(
            self.DATASET_NAME,
            source_name="Argly API — William López",
            source_url="https://api.argly.com.ar",
            source_mode="live",
            record_count=len(df),
            fields=df.columns,
            reuse_policy={
                "status": "open-attribution",
                "license": "MIT",
                "license_url": "https://github.com/William10101995/argly",
                "attribution_required": True,
                "redistribution_ok": True,
                "summary": "Datos públicos argentinos vía Argly API.",
            },
        )
        print(f"\n✅ Argly → staging: {len(df)} registros")

    def _fetch_simple(self, nombre: str) -> pl.DataFrame | None:
        try:
            r = requests.get(f"{self.BASE_URL}/{nombre}", timeout=10)
            r.raise_for_status()
            data = r.json().get("data", {})
            if isinstance(data, dict):
                df = pl.DataFrame([data])
                return df.with_columns(pl.lit(nombre).alias("indicador"))
        except Exception as e:
            print(f"  ❌ {nombre}: {e}")
        return None

    def _fetch_combustibles(self) -> pl.DataFrame | None:
        frames = []
        for prov in self.PROVINCIAS:
            try:
                r = requests.get(f"{self.BASE_URL}/combustibles?provincia={prov}", timeout=10)
                r.raise_for_status()
                data = r.json().get("data", [])
                if data:
                    df = pl.DataFrame(data)
                    if "precios" in df.columns:
                        df = df.with_columns([
                            pl.col("precios").struct.field("día").alias("precio_dia"),
                            pl.col("precios").struct.field("noche").alias("precio_noche"),
                        ]).drop("precios")
                    frames.append(df)
                    print(f"  ✅ {prov}: {len(data)} estaciones")
            except Exception as e:
                print(f"  ❌ {prov}: {e}")
        return pl.concat(frames) if frames else None

    def _fetch_combustibles_promedio(self) -> pl.DataFrame | None:
        frames = []
        for prov in self.PROVINCIAS:
            for comb in self.COMBUSTIBLES:
                try:
                    r = requests.get(
                        f"{self.BASE_URL}/combustibles/promedio",
                        params={"provincia": prov, "combustible": comb},
                        timeout=10,
                    )
                    r.raise_for_status()
                    data = r.json().get("data", {})
                    if data:
                        frames.append(pl.DataFrame([data]))
                except Exception:
                    pass
        return pl.concat(frames) if frames else None


if __name__ == "__main__":
    ArglyExtractor().run()