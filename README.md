# Argentina Hub

[![PyPI version](https://badge.fury.io/py/argentinahub.svg)](https://pypi.org/project/argentinahub/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20788569.svg)](https://doi.org/10.5281/zenodo.20788569)

Capa de datos públicos argentinos curados y reproducibles. Datos del INDEC, BCRA y Ministerio de Salud, consumibles en una línea de código.

Inspirado en [Chile Hub](https://github.com/cortega26/chile-hub).

## Instalación

```bash
pip install argentinahub
```

---

## Uso

```markdown
## Uso

```python
from argentina_hub import ArgentinaHub
hub = ArgentinaHub()

print(hub.resumen())
df = hub.cargar("censo_poblacion")
df = hub.cargar("dpa", codigo_provincia="02")
df = hub.cargar("timeseries")
```

---


## Datasets

```markdown
## Datasets

| Dataset | Fuente | Registros | Descripción |
|---|---|---|---|
| dpa | INDEC | 527 | Provincias y departamentos con códigos INDEC |
| censo_poblacion | INDEC | 1,552,241 | Sexo, escolaridad, actividad económica |
| censo_hogares | INDEC | 1,127,000 | Material de pisos, clima educativo |
| censo_viviendas | INDEC | 510,538 | Tipo de vivienda, ocupación |
| indicadores | BCRA | 34,636 | Dólar, inflación, UVA, reservas |
| timeseries | BCRA + Salud | 35,428 | 8 indicadores BCRA + consultas ambulatorias |
| datos_sheets | Sheets | 523 | DPA desde planillas públicas |
```

---

## Licencia

Código: AGPL v3. Si usás este código en un servidor o servicio web, debés publicar tus modificaciones.

Datos: CC-BY 4.0 (Ley 27.275 de Acceso a la Información Pública).

## Citar

López, H. R. (2026). Argentina Hub v1.0.0 [Data set]. Zenodo. https://doi.org/10.5281/zenodo.20788569
