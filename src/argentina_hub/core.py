"""
core.py — Clase ArgentinaHub y API pública.

Superficie de consumo principal de argentina-hub.
Todos los métodos devuelven Polars DataFrames.
"""

from pathlib import Path

import polars as pl


class ArgentinaHub:
    """API pública de argentina-hub. Cargá datasets curados en una línea."""

    def __init__(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.normalized = self.root / "data" / "normalized"

    def cargar(self, dataset: str, **filtros) -> pl.DataFrame:
        """
        Carga un dataset desde normalized/.

        Args:
            dataset: Nombre del dataset (dpa, censo_poblacion, censo_hogares,
                     censo_viviendas, indicadores).
            **filtros: Filtros por columna (ej: provincia="02").

        Returns:
            Polars DataFrame con los datos solicitados.
        """
        path = self.normalized / f"{dataset}.parquet"

        if not path.exists():
            disponibles = self._listar_datasets()
            raise FileNotFoundError(
                f"Dataset '{dataset}' no encontrado. Disponibles: {disponibles}"
            )

        df = pl.read_parquet(path)

        # Aplicar filtros si los hay
        for col, valor in filtros.items():
            if col in df.columns:
                df = df.filter(pl.col(col) == valor)

        return df

    def resumen(self) -> dict:
        """
        Devuelve un catálogo de datasets disponibles con nombre, registros y columnas.

        Returns:
            Dict con información de cada dataset.
        """
        datasets = {}
        for path in sorted(self.normalized.glob("*.parquet")):
            name = path.stem
            df = pl.read_parquet(path)
            datasets[name] = {
                "registros": len(df),
                "columnas": df.columns,
            }
        return datasets

    def _listar_datasets(self) -> list[str]:
        """Lista los nombres de datasets disponibles."""
        return sorted([p.stem for p in self.normalized.glob("*.parquet")])
