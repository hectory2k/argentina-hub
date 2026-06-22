# SOURCE_OF_TRUTH.md — Índice Maestro

Lee esto primero. Luego sigue los punteros. No leas archivos completos en frío.

---

## Qué es este repositorio

`argentina-hub` es una capa de datos reproducible y curada sobre datasets públicos oficiales de Argentina. Pipeline: extracción → construcción → validación → publicación. Artefactos: Parquet, DuckDB, JSON, ZIP + landing page + CLI/API Python (`ArgentinaHub`).

---

## Document ownership

| Documento | Cuándo leerlo |
|---|---|
| **`SOURCE_OF_TRUTH.md`** ← estás aquí | Siempre primero |
| **`AGENTS.md`** | Al agregar dataset, depurar pipeline, preguntas legales |

---

## 5 invariantes no negociables

1. Códigos INDEC siempre string: `"02"`, `"02007"`, `"02007001"`. Nunca int.
2. Fallar con estridencia: `raise SystemExit(...)`, nunca warnings.
3. `data/raw/` solo append, nunca modificar.
4. `nombre_localidad_clean` siempre presente: minúsculas, sin tildes, sin ñ.
5. Rutas siempre relativas a `__file__`, nunca a CWD.

---

## Mapa de archivos

src/extractors/ → base.py, dpa_extractor.py, censo_extractor.py, indicadores_extractor.py
src/validation.py → validate_*()
src/build_dev_db.py → staging/ → normalized/
src/argentina_hub/ → core.py (API), cli.py
data/raw/ → snapshots inmutables
data/staging/ → CSV + metadata.json
data/normalized/ → Parquet, JSON (regenerable)

---

## Tareas comunes

| Tarea | Ir a |
|---|---|
| Pipeline completo | `make refresh` |
| Agregar dataset | `AGENTS.md §5` |
| API pública | `src/argentina_hub/core.py` |
| Contrato extractors | `src/extractors/base.py` |

---

## Flujo
make extract → staging/
make build → normalized/
make verify → integridad
make test → pytest (14 tests)
make refresh → todo junto

---

## MVP: 3 datasets

## Datasets actuales

| Dataset | Fuente | Extractor |
|---|---|---|
| DPA | INDEC / Google Sheets | `dpa_extractor.py` / `google_sheets_extractor.py` |
| Censo 2022 | INDEC vía censoargentino | `censo_extractor.py` |
| Indicadores BCRA | api.estadisticasbcra.com | `indicadores_extractor.py` / `timeseries_extractor.py` |
| Timeseries | BCRA + Datos Abiertos Salud | `timeseries_extractor.py` |
| Google Sheets | Planillas públicas | `google_sheets_extractor.py` |
