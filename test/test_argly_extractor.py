"""
Test del extractor Argly — solo verifica que los endpoints respondan.
No extrae datos completos, solo valida conectividad.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
import requests


class TestArglyEndpoints:
    """Verifica que los endpoints de Argly respondan OK."""

    BASE = "https://api.argly.com.ar/v1"

    @pytest.mark.parametrize("endpoint", [
        "icl", "cer", "uva", "uvi", "smvm", "ipc", "riesgo-pais",
    ])
    def test_endpoint_responde(self, endpoint):
        r = requests.get(f"{self.BASE}/{endpoint}", timeout=10)
        assert r.status_code == 200
        assert "data" in r.json()

    def test_combustibles_chaco(self):
        r = requests.get(f"{self.BASE}/combustibles?provincia=chaco", timeout=10)
        assert r.status_code == 200
        assert len(r.json()["data"]) > 0

    def test_combustibles_promedio(self):
        r = requests.get(f"{self.BASE}/combustibles/promedio?provincia=chaco&combustible=Nafta Súper", timeout=10)
        assert r.status_code == 200
        assert "precio_promedio" in r.json()["data"]

    class TestArglyExtractor:
        """Verifica que el extractor funcione."""

        def test_init(self):
            from extractors.argly_extractor import ArglyExtractor
            e = ArglyExtractor()
            assert e.DATASET_NAME == "argly"
            assert len(e.INDICADORES_SIMPLES) == 7

        def test_run_no_crash(self):
            from extractors.argly_extractor import ArglyExtractor
            e = ArglyExtractor()
            e.run()  # No debe lanzar excepción