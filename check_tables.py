import sqlite3

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()

# Obtener todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("✅ Base de datos creada exitosamente!")
print("📋 Tablas creadas:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()
