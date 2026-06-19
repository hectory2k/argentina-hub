"""
BaseExtractor — Contrato abstracto para todos los extractores de argentina-hub.

Todo extractor debe heredar de esta clase e implementar run().
El contrato garantiza que cada extractor produce:
  - data/staging/{dataset}.csv
  - data/staging/{dataset}.metadata.json
  - data/raw/{source}_{timestamp}.json (cuando aplica)

Las rutas son siempre relativas a __file__, nunca a CWD.
"""

import json
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime, timezone


class BaseExtractor(ABC):
    """Clase base abstracta para todos los extractores del pipeline."""

    def __init__(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.staging_dir = self.root / "data" / "staging"
        self.raw_dir = self.root / "data" / "raw"
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def run(self) -> None:
        """
        Ejecuta la extracción completa.

        Debe:
          1. Obtener datos de la fuente (live o fallback).
          2. Guardar snapshot en data/raw/ (cuando la fuente es externa).
          3. Normalizar y guardar CSV en data/staging/.
          4. Guardar metadata.json en data/staging/.
        """
        ...

    def _guardar_csv(self, df, dataset_name: str) -> Path:
        """Guarda un DataFrame como CSV en staging/ y retorna la ruta."""
        path = self.staging_dir / f"{dataset_name}.csv"
        df.write_csv(path)
        return path

    def _guardar_metadata(self, dataset_name: str, **kwargs) -> Path:
        """Guarda metadata.json en staging/ y retorna la ruta."""
        path = self.staging_dir / f"{dataset_name}.metadata.json"
        metadata = {
            "dataset": dataset_name,
            "refreshed_at_utc": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
        path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))
        return path

    def _guardar_raw(self, source_name: str, data: dict | list) -> Path:
        """Guarda snapshot crudo en data/raw/ con timestamp."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.raw_dir / f"{source_name}_{timestamp}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return path
