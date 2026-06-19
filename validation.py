"""
validation.py — Validadores del pipeline argentina-hub.

Cada validador recibe un DataFrame y un dict de metadata.
Si encuentra errores, levanta SystemExit (nunca warnings).
"""

import polars as pl


def validate_dpa(df: pl.DataFrame, metadata: dict) -> None:
    """Valida la División Político-Administrativa."""
    errors = []

    # No vacío
    if df.is_empty():
        errors.append("DPA: DataFrame vacío.")

    # PK única
    if "codigo_radio" in df.columns:
        duplicados = df.group_by("codigo_radio").len().filter(pl.col("len") > 1)
        if not duplicados.is_empty():
            errors.append(f"DPA: codigo_radio duplicado ({len(duplicados)} casos).")

    # Códigos como string
    for col in ["codigo_provincia", "codigo_departamento", "codigo_radio"]:
        if col in df.columns:
            if df[col].dtype != pl.Utf8:
                errors.append(f"DPA: {col} no es string.")

    # nombre_localidad_clean presente
    if "nombre_localidad_clean" not in df.columns:
        errors.append("DPA: falta columna nombre_localidad_clean.")

    if errors:
        raise SystemExit(f"Validación DPA fallida:\n" + "\n".join(errors))


def validate_censo(df: pl.DataFrame, metadata: dict) -> None:
    """Valida sub-tablas del Censo 2022."""
    errors = []

    # No vacío
    if df.is_empty():
        errors.append(f"Censo ({metadata.get('dataset', '?')}): DataFrame vacío.")

    # Tiene al menos un código geográfico
    geo_cols = ["codigo_provincia", "codigo_departamento", "codigo_radio"]
    if not any(c in df.columns for c in geo_cols):
        errors.append(f"Censo ({metadata.get('dataset', '?')}): sin columnas geográficas.")

    if errors:
        raise SystemExit(f"Validación Censo fallida:\n" + "\n".join(errors))


def validate_indicadores(df: pl.DataFrame, metadata: dict) -> None:
    """Valida indicadores económicos."""
    errors = []

    # No vacío
    if df.is_empty():
        errors.append("Indicadores: DataFrame vacío.")

    # Columnas esperadas
    for col in ["fecha", "valor", "indicador"]:
        if col not in df.columns:
            errors.append(f"Indicadores: falta columna {col}.")

    if errors:
        raise SystemExit(f"Validación Indicadores fallida:\n" + "\n".join(errors))
