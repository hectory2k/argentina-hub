# Censo 2022

**Fuente:** INDEC (vía censoargentino, DuckDB + Parquet en Hugging Face)
**Licencia:** CC-BY (Ley 27.275)
**Actualización:** Puntual (datos del Censo 2022)

## Descripción

Microdatos del Censo Nacional 2022 en formato tidy.

## Sub-tablas

| Dataset | Contenido |
|---|---|
| censo_poblacion | Datos de personas (sexo, escolaridad, actividad) |
| censo_hogares | Datos de hogares (clima educativo, materiales) |
| censo_viviendas | Datos de viviendas (tipo, ocupación, hogares) |

## Schema común

| Columna | Tipo | Descripción |
|---|---|---|
| id_geo | string | Identificador geográfico |
| valor_provincia | string | Código de provincia |
| etiqueta_provincia | string | Nombre de provincia |
| codigo_variable | string | Código de la variable censal |
| etiqueta_categoria | string | Etiqueta legible |
| conteo | int | Cantidad de casos |

## Ejemplo

```python
from argentina_hub import ArgentinaHub
hub = ArgentinaHub()
df = hub.cargar("censo_poblacion")
