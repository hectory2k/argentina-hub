"""
test_pipeline_logic.py — Tests de validación y lógica de pipeline.
No requiere datos normalizados.
"""

import sys
from pathlib import Path

import polars as pl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


class TestValidateDPA:
    """Tests para validate_dpa."""

    def test_dpa_vacio_falla(self):
        from validation import validate_dpa

        df = pl.DataFrame(schema={"codigo_radio": pl.Utf8})
        with pytest.raises(SystemExit):
            validate_dpa(df, {})

    def test_dpa_sin_clean_falla(self):
        from validation import validate_dpa

        df = pl.DataFrame({"codigo_radio": ["02007001"]})
        with pytest.raises(SystemExit):
            validate_dpa(df, {})

    def test_dpa_valido_pasa(self):
        from validation import validate_dpa

        df = pl.DataFrame({
            "codigo_radio": ["02007001"],
            "codigo_provincia": ["02"],
            "codigo_departamento": ["02007"],
            "nombre_localidad_clean": ["palermo"],
        })
        validate_dpa(df, {})  # No debe lanzar excepción


class TestValidateCenso:
    """Tests para validate_censo."""

    def test_censo_vacio_falla(self):
        from validation import validate_censo

        df = pl.DataFrame(schema={"codigo_provincia": pl.Utf8})
        with pytest.raises(SystemExit):
            validate_censo(df, {"dataset": "censo_poblacion"})

    def test_censo_sin_geografia_falla(self):
        from validation import validate_censo

        df = pl.DataFrame({"edad": [25, 30]})
        with pytest.raises(SystemExit):
            validate_censo(df, {"dataset": "censo_poblacion"})

    def test_censo_valido_pasa(self):
        from validation import validate_censo

        df = pl.DataFrame({"valor_provincia": ["02", "02"]})
        validate_censo(df, {"dataset": "censo_poblacion"})  # No debe lanzar


class TestValidateIndicadores:
    """Tests para validate_indicadores."""

    def test_indicadores_vacio_falla(self):
        from validation import validate_indicadores

        df = pl.DataFrame(schema={"fecha": pl.Utf8})
        with pytest.raises(SystemExit):
            validate_indicadores(df, {})

    def test_indicadores_sin_fecha_falla(self):
        from validation import validate_indicadores

        df = pl.DataFrame({"valor": [100.0], "indicador": ["dolar"]})
        with pytest.raises(SystemExit):
            validate_indicadores(df, {})

    def test_indicadores_validos_pasa(self):
        from validation import validate_indicadores

        df = pl.DataFrame({
            "fecha": ["2024-01-01"],
            "valor": [100.0],
            "indicador": ["dolar_oficial"],
        })
        validate_indicadores(df, {})  # No debe lanzar
