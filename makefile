.PHONY: extract build verify test refresh clean

# Pipeline completo
refresh: extract build verify test
	@echo "Pipeline completo ejecutado exitosamente."

# Paso 1: Extraer todos los datasets
extract:
	@echo "Extrayendo DPA..."
	python -m src.extractors.dpa_extractor
	@echo "Extrayendo Censo 2022..."
	python -m src.extractors.censo_extractor
	@echo "Extrayendo Indicadores Económicos..."
	python -m src.extractors.indicadores_extractor
	@echo "Extracción completada."

# Paso 2: Construir artefactos normalizados
build:
	@echo "Construyendo artefactos..."
	python -m src.build_dev_db
	@echo "Build completado."

# Paso 3: Verificar integridad
verify:
	@echo "Verificando integridad..."
	python scripts/verify_pipeline.py
	@echo "Verificación completada."

# Paso 4: Correr tests
test:
	@echo "Ejecutando tests..."
	pytest -v
	@echo "Tests completados."

# Limpiar datos generados (no toca raw/)
clean:
	rm -rf data/staging/*
	rm -rf data/normalized/*
	@echo "Staging y normalized limpios. Raw preservado."
