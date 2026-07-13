"""
create_duckdb.py — Base de datos unificada de Argentina Hub.
"""

import duckdb
from pathlib import Path

DB_PATH = Path("argentina_hub.duckdb")

if DB_PATH.exists():
    DB_PATH.unlink()

conn = duckdb.connect(str(DB_PATH))
print("Creando argentina_hub.duckdb...\n")

# 1. Dengue
conn.execute("""
        CREATE TABLE dengue AS 
        SELECT * FROM read_csv('C:/Users/eliba02/vigisalud-dengue/dengue_historico.csv',
            all_varchar=true,
            header=true
        )
    """)
count: object = conn.execute("SELECT COUNT(*) FROM dengue").fetchone()[0]
print(f"  ✅ dengue: {count:,} registros")

# 2. REFES
refes = Path.home() / "argentina-hub" / "data" / "staging" / "refes.csv"
if refes.exists():
    conn.execute(f"CREATE TABLE refes AS SELECT * FROM '{refes}'")
    count = conn.execute("SELECT COUNT(*) FROM refes").fetchone()[0]
    print(f"  ✅ refes: {count:,} registros")

# 3. DPA
dpa = Path.home() / "argentina-hub" / "data" / "normalized" / "dpa.parquet"
if dpa.exists():
    conn.execute(f"CREATE TABLE dpa AS SELECT * FROM '{dpa}'")
    count = conn.execute("SELECT COUNT(*) FROM dpa").fetchone()[0]
    print(f"  ✅ dpa: {count:,} registros")

# 4. Localidades
loc = Path.home() / "argentina-hub" / "data" / "staging" / "localidades.csv"
if loc.exists():
    conn.execute(f"CREATE TABLE localidades AS SELECT * FROM '{loc}'")
    count = conn.execute("SELECT COUNT(*) FROM localidades").fetchone()[0]
    print(f"  ✅ localidades: {count:,} registros")

print(f"\n🎉 {DB_PATH} — {DB_PATH.stat().st_size / 1024 / 1024:.1f} MB")

# Demo
print("\n📊 Top 5 provincias por dengue:")
print(conn.execute("""
    SELECT provincia_residencia, SUM(CAST(cantidad AS DOUBLE)) as total
    FROM dengue
    WHERE provincia_residencia != 'desconocida'
    GROUP BY provincia_residencia
    ORDER BY total DESC
    LIMIT 5
""").fetchdf())

conn.close()