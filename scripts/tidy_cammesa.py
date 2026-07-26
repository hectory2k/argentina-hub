"""
Convierte el CSV de Evolución anual de CAMMESA a formato tidy.
Entrada: tablas_limpias/Evolución_anual_tabla_1.csv
Salida: data/staging/cammesa_tidy.csv
"""

import polars as pl
from pathlib import Path

CSV_IN = Path("C:/Users/eliba02/argentina-hub/tablas_limpias/Evolución_anual_tabla_1.csv")
CSV_OUT = Path("data/staging/cammesa_tidy.csv")

df = pl.read_csv(CSV_IN, ignore_errors=True, truncate_ragged_lines=True)

cols_fijas = df.columns[:4]
cols_anios = [c for c in df.columns[4:] if c not in ("", " ", None)]

df_tidy = df.unpivot(
    index=cols_fijas,
    on=cols_anios,
    variable_name="anio",
    value_name="valor",
)

df_tidy = df_tidy.filter(
    pl.col("anio").str.contains(r"^\d{4}")
).with_columns(
    pl.col("valor").cast(pl.Float64, strict=False),
    pl.col("anio").cast(pl.Float64, strict=False).cast(pl.Int64),
)

CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
df_tidy.write_csv(CSV_OUT)
print(f"✅ Tidy: {len(df_tidy)} registros → {CSV_OUT}")
print(df_tidy.head(5))