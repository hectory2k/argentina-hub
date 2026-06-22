# Consultas Ambulatorias

**Fuente:** Datos Abiertos del Ministerio de Salud
**Licencia:** CC-BY (Ley 27.275)
**Actualización:** Puntual (2013-2021)

## Descripción

Consultas médicas ambulatorias por unidad operativa. 99 especialidades × 8 años.

## Schema

Incluido en el dataset `timeseries` con indicador `consultas_ambulatorias`.

## Ejemplo

from argentina_hub import ArgentinaHub
hub = ArgentinaHub()
df = hub.cargar("timeseries")
consultas = df.filter(pl.col("indicador") == "consultas_ambulatorias")

## Nota

Este dataset no se usa en VigiSalud. Ver razonamiento en GitHub Issues.
