# Argentina Hub

[![PyPI version](https://badge.fury.io/py/argentinahub.svg)](https://pypi.org/project/argentinahub/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20788569.svg)](https://doi.org/10.5281/zenodo.20788569)

Capa de datos públicos argentinos curados y reproducibles. Datos del INDEC, BCRA y Ministerio de Salud, consumibles en una línea de código.

Inspirado en [Chile Hub](https://github.com/tuusuario/chile-hub).

## Instalación

` bash
pip install argentinahub `


## USO 

from argentina_hub import ArgentinaHub
hub = ArgentinaHub()

# Ver datasets disponibles

print(hub.resumen())

# Cargar uno

df = hub.cargar("censo_poblacion")
df = hub.cargar("dpa", codigo_provincia="02")  # Solo CABA
df = hub.cargar("timeseries")

## Datasets

Dataset	Fuente	Registros	Descripción
dpa	INDEC (Censo 2022)	527	Provincias y departamentos con códigos INDEC
censo_poblacion	INDEC (censoargentino)	1,552,241	Sexo, escolaridad, actividad económica
censo_hogares	INDEC (censoargentino)	1,127,000	Material de pisos, clima educativo
censo_viviendas	INDEC (censoargentino)	510,538	Tipo de vivienda, ocupación
indicadores	BCRA	34,636	Dólar, inflación, UVA, reservas
timeseries	BCRA + Min. Salud	35,428	Series temporales: 8 indicadores BCRA + consultas ambulatorias
datos_sheets	Google Sheets	523	DPA desde planillas públicas

## Licencia

Código: AGPL v3. Si usás este código en un servidor o servicio web, debés publicar tus modificaciones.

Datos: CC-BY 4.0 (Ley 27.275 de Acceso a la Información Pública).

## Citar

López, H. R. (2026). Argentina Hub v1.0.0 [Data set]. Zenodo. https://doi.org/10.5281/zenodo.20788569
