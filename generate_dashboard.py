import duckdb
import json

conn = duckdb.connect("scripts/argentina_hub.duckdb")

data = {
    "provincias": conn.execute("""
        SELECT provincia_residencia, SUM(CAST(cantidad AS DOUBLE)) as total
        FROM dengue WHERE provincia_residencia != 'desconocida'
        GROUP BY provincia_residencia ORDER BY total DESC LIMIT 5
    """).fetchdf().to_dict(orient="records"),

    "formosa": conn.execute("""
        SELECT departamento_residencia, SUM(CAST(cantidad AS DOUBLE)) as total
        FROM dengue WHERE provincia_residencia = 'Formosa'
        GROUP BY departamento_residencia ORDER BY total DESC LIMIT 5
    """).fetchdf().to_dict(orient="records"),

    "anual": conn.execute("""
        SELECT anio_min, SUM(CAST(cantidad AS DOUBLE)) as total
        FROM dengue WHERE anio_min NOT LIKE '%desconocido%'
        GROUP BY anio_min ORDER BY anio_min
    """).fetchdf().to_dict(orient="records"),
}

with open("data_dengue.json", "w") as f:
    json.dump(data, f)

print("✅ data_dengue.json generado")