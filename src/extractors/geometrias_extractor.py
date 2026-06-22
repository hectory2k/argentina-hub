"""
Geometrías Extractor — Geometrías oficiales de Argentina desde el IGN.

Fuente: Instituto Geográfico Nacional vía WFS (argentina.geo.shapes).
Estrategia: Descargar shapes de provincias y departamentos, guardar como GeoJSON.

Produce:
  - data/staging/geometrias_provincias.geojson
  - data/staging/geometrias_departamentos.geojson
  - data/staging/geometrias_departamentos.csv (sin geometry, para CSV)
"""

import polars as pl
from argentina.geo.shapes import provincias, departamentos

from extractors.base import BaseExtractor


class GeometriasExtractor(BaseExtractor):
    """Extrae geometrías del IGN."""

    DATASET_NAME = "geometrias"

    def run(self) -> None:
        """Descarga y guarda geometrías de provincias y departamentos."""
        
        # Provincias
        print("Descargando provincias...")
        gdf_prov = provincias()
        gdf_prov = gdf_prov.rename(columns={
            "entidad": "tipo",
            "fna": "nombre_oficial",
            "gna": "nombre_geografico",
            "nam": "nombre",
            "in1": "codigo_indec",
            "fdc": "fuente",
            "sag": "organismo",
        })
        gdf_prov.to_file(self.staging_dir / "geometrias_provincias.geojson", driver="GeoJSON")
        print(f"  → {len(gdf_prov)} provincias")

        # Departamentos
        print("Descargando departamentos...")
        gdf_deptos = departamentos()
        gdf_deptos = gdf_deptos.rename(columns={
            "objeto": "tipo",
            "fna": "nombre_oficial",
            "gna": "nombre_geografico",
            "nam": "nombre",
            "in1": "codigo_indec",
            "fdc": "fuente",
            "sag": "organismo",
        })
        gdf_deptos.to_file(self.staging_dir / "geometrias_departamentos.geojson", driver="GeoJSON")
        
        # Versión CSV (sin geometría)
        df = pl.from_pandas(gdf_deptos.drop(columns=["geometry"]))
        self._guardar_csv(df, "geometrias_departamentos")
        print(f"  → {len(gdf_deptos)} departamentos")

        # Metadata
        self._guardar_metadata(
            self.DATASET_NAME,
            source_name="Instituto Geográfico Nacional (IGN)",
            source_url="https://wms.ign.gob.ar/geoserver/ign/ows",
            source_mode="live",
            record_count=len(gdf_deptos),
            fields=df.columns,
            formatos=["geojson", "csv"],
            reuse_policy={
                "status": "open-attribution",
                "license": "CC-BY",
                "license_url": "https://www.ign.gob.ar/descargas/terminos",
                "attribution_required": True,
                "redistribution_ok": True,
                "summary": "Geometrías oficiales del IGN.",
            },
        )
        print(f"🎉 Geometrías → staging: provincias + departamentos")
