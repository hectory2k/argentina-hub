import duckdb
import json

conn = duckdb.connect("scripts/argentina_hub.duckdb")

rango_nacional = conn.execute("""
    SELECT MIN(anio_min) as desde, MAX(anio_min) as hasta
    FROM dengue WHERE anio_min NOT LIKE '%desconocido%'
""").fetchdf().to_dict(orient="records")[0]

rango_formosa = f"{conn.execute('''SELECT MIN(anio_min) FROM dengue WHERE provincia_residencia = 'Formosa' AND anio_min NOT LIKE '%desconocido%' ''').fetchone()[0]}-{conn.execute('''SELECT MAX(anio_min) FROM dengue WHERE provincia_residencia = 'Formosa' AND anio_min NOT LIKE '%desconocido%' ''').fetchone()[0]}"

data = {
    "rango_anios": f"{rango_nacional['desde']}-{rango_nacional['hasta']}",
    "rango_formosa": rango_formosa,
    "provincias": conn.execute("""
        SELECT provincia_residencia, SUM(CAST(cantidad AS DOUBLE)) as total
        FROM dengue WHERE provincia_residencia != 'desconocida'
        GROUP BY provincia_residencia ORDER BY total DESC LIMIT 5
    """).fetchdf().to_dict(orient="records"),
    "anual_nacional": conn.execute("""
        SELECT anio_min, SUM(CAST(cantidad AS DOUBLE)) as total
        FROM dengue WHERE anio_min NOT LIKE '%desconocido%'
        GROUP BY anio_min ORDER BY anio_min
    """).fetchdf().to_dict(orient="records"),
    "formosa": conn.execute("""
        SELECT departamento_residencia, SUM(CAST(cantidad AS DOUBLE)) as total
        FROM dengue WHERE provincia_residencia = 'Formosa'
        GROUP BY departamento_residencia ORDER BY total DESC LIMIT 5
    """).fetchdf().to_dict(orient="records"),
}

with open("data_dengue.json", "w") as f:
    json.dump(data, f)

print("✅ data_dengue.json generado")
print(f"   Nacional: {data['rango_anios']}")
print(f"   Formosa: {data['rango_formosa']}")