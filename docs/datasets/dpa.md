# DPA — División Político-Administrativa

**Fuente:** INDEC — Censo Nacional 2022 (vía censoargentino)
**Licencia:** CC-BY (Ley 27.275)
**Actualización:** Puntual (datos del Censo 2022)

## Descripción

División Político-Administrativa de Argentina: provincias y departamentos con códigos INDEC oficiales.

## Schema

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_provincia | string (2) | Código INDEC de provincia |
| nombre_provincia | string | Nombre de la provincia |
| codigo_departamento | string (5) | Código INDEC de departamento |
| nombre_departamento | string | Nombre del departamento |
| nombre_localidad_clean | string | Nombre normalizado (minúsculas, sin tildes, sin ñ) |

## Ejemplo

```python
from argentina_hub import ArgentinaHub
hub = ArgentinaHub()
df = hub.cargar("dpa")
df = hub.cargar("dpa", codigo_provincia="02")
