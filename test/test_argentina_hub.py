import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
from argentina_hub import ArgentinaHub


class TestArgentinaHubAPI:
    @pytest.fixture
    def hub(self):
        return ArgentinaHub()

    def test_resumen_retorna_dict(self, hub):
        resumen = hub.resumen()
        assert isinstance(resumen, dict)
        assert len(resumen) > 0

    def test_cargar_dpa_retorna_dataframe(self, hub):
        df = hub.cargar("dpa")
        assert not df.is_empty()
        assert "codigo_departamento" in df.columns

    def test_cargar_dataset_inexistente_falla(self, hub):
        with pytest.raises(FileNotFoundError):
            hub.cargar("no_existe")

    def test_cargar_con_filtro_provincia(self, hub):
        df = hub.cargar("dpa", codigo_provincia="02")
        if "codigo_provincia" in df.columns:
            provincias = df["codigo_provincia"].unique().to_list()
            assert all(p == "02" for p in provincias)

    def test_todos_los_datasets_cargan(self, hub):
        for nombre in hub.resumen():
            df = hub.cargar(nombre)
            assert not df.is_empty()
