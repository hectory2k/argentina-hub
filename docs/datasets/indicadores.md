# Indicadores Económicos

**Fuente:** BCRA (vía api.estadisticasbcra.com)
**Licencia:** Datos públicos BCRA
**Actualización:** Bajo demanda

## Descripción

Series temporales de indicadores económicos argentinos.

## Indicadores

| Nombre | Descripción |
|---|---|
| dolar_oficial | USD Oficial |
| dolar_blue | USD |
| inflacion_mensual | Inflación mensual oficial |
| inflacion_interanual | Inflación interanual oficial |
| uva | UVA |
| reservas | Reservas internacionales |
| tasa_badlar | Tasa BADLAR |
| merval | MERVAL |

## Schema

| Columna | Tipo | Descripción |
|---|---|---|
| fecha | string | YYYY-MM-DD |
| valor | float | Valor del indicador |
| indicador | string | Nombre del indicador |

## Ejemplo

```python
from argentina_hub import ArgentinaHub
hub = ArgentinaHub()
df = hub.cargar("indicadores")
