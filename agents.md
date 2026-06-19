# AGENTS.md — Argentina Hub

Guía de trabajo para agentes de IA en `argentina-hub`. Leer completo antes de modificar cualquier archivo.

---

## 1. Propósito

Capa de datos curada sobre datasets públicos argentinos. **3 datasets. Limpios, validados, consumibles en una línea.**

| Dataset | Fuente | Sub-tablas |
|---|---|---|
| **DPA** | Portal Geoestadístico INDEC | — |
| **Censo 2022** | INDEC vía `censoargentino` | `censo_poblacion`, `censo_hogares`, `censo_viviendas` |
| **Indicadores Económicos** | BCRA / ArgentinaDatos | — |

---

## 2. Estructura

src/extractors/ → base.py, dpa_extractor.py, censo_extractor.py, indicadores_extractor.py
src/validation.py → validate_*()
src/build_dev_db.py → staging/ → normalized/
src/argentina_hub/ → core.py (API), cli.py
data/raw/ → snapshots inmutables
data/staging/ → CSV + metadata.json
data/normalized/ → Parquet, JSON, DuckDB (nunca editar a mano)

## 3. Pipeline

make extract → staging/
make build → normalized/
make verify → integridad
make test → pytest
make refresh → todo junto


---

## 4. Invariantes

1. **Códigos INDEC siempre string:** `"02"`, `"02007"`, `"02007001"`. Nunca int.
2. **Fallar fuerte:** `raise SystemExit(...)`, nunca `warnings.warn()`.
3. **`data/raw/` solo append.**
4. **`nombre_localidad_clean`:** minúsculas, sin tildes, sin ñ.
5. **Rutas relativas a `__file__`**, nunca a CWD.

---

## 5. Nuevo dataset (6 pasos)

1. **Evaluar fuente:** licencia (Ley 27.275), API/dump estático, estabilidad 12 meses.
2. **Extractor:** `src/extractors/{nombre}_extractor.py` → fetch, guardar raw, staging CSV + metadata.json.
3. **Registrar** en `build_dev_db.py`.
4. **Validar:** `validate_{nombre}()` en `validation.py` (no vacío, PK única, FK con DPA si aplica).
5. **Testear:** `test_extractors.py` + `test_pipeline_logic.py`.
6. **Documentar:** `docs/datasets/{nombre}.md`.

---

## 6. Legal

| Color | Estado | Acción |
|---|---|---|
| 🟢 `open-attribution` | CC-BY | Publicar |
| 🟡 `public-api-review-terms` | API pública sin licencia | Solo si origen es redistribuible |
| 🔴 `restricted` | Datos personales (Ley 25.326) | Excluir |

Duda → no redistribuir. Publicar solo metadata + link.

---

## 7. Convenciones

- `snake_case` en español: `codigo_provincia`, `nombre_localidad_clean`.
- Credenciales en `.env` (no commiteado): `os.getenv("BCRA_API_KEY")`.
- `censoargentino` ya normaliza, etiqueta y filtra. No reimplementar.

---

## 8. API pública

```python
from argentina_hub import ArgentinaHub
hub = ArgentinaHub()
df = hub.cargar("censo_poblacion")
df = hub.cargar("dpa", provincia="02")
resumen = hub.resumen()

argentina-hub resumen
argentina-hub censo-poblacion --provincia 02

9. CI/CD
No implementado. make refresh manual. Se agregará con 5+ datasets o múltiples colaboradores.

10. Antipatrones
❌ Editar normalized/ a mano

❌ warnings.warn() para errores de datos

❌ Códigos INDEC como enteros

❌ Datasets sin validación

❌ Reimplementar censoargentino

❌ Dependencias sin justificación

