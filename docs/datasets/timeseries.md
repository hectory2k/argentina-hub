# Timeseries — Series temporales

**Fuente:** BCRA + Datos Abiertos Salud
**Licencia:** CC-BY (Ley 27.275)
**Actualización:** Bajo demanda

## Descripción

Series temporales consolidadas en formato canónico (fecha, valor, indicador, unidad, frecuencia).

## Indicadores

| Indicador | Fuente | Unidad | Frecuencia | Registros |
|---|---|---|---|---|
| dolar_oficial | BCRA | ARS | diaria | 5,423 |
| dolar_blue | BCRA | ARS | diaria | 6,074 |
| inflacion_mensual | BCRA | % | mensual | 410 |
| inflacion_interanual | BCRA | % | mensual | 410 |
| uva | BCRA | ARS | diaria | 2,933 |
| reservas | BCRA | USD | diaria | 6,967 |
| tasa_badlar | BCRA | % | diaria | 6,174 |
| merval | BCRA | ARS | diaria | 6,245 |
| consultas_ambulatorias | Min. Salud | consultas | anual | 792 |

## Schema

| Columna | Tipo | Descripción |
|---|---|---|
| fecha | str | YYYY-MM-DD |
| valor | float | Valor del indicador |
| indicador | str | Nombre del indicador |
| unidad | str | Unidad de medida |
| frecuencia | str | diaria, mensual, anual |

## Ejemplo

from argentina_hub import ArgentinaHub
hub = ArgentinaHub()
df = hub.cargar("timeseries")
dolar = df.filter(pl.col("indicador") == "dolar_oficial")
