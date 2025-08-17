import sqlite3

db_path = "database.sqlite"  # Cambia si tu archivo tiene otro nombre

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Crear nueva tabla temporal
cursor.execute("""
CREATE TABLE reviews_new (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  reserva_id INTEGER,
  autor_id INTEGER NOT NULL,
  paquete_id INTEGER NOT NULL,
  calificacion INTEGER NOT NULL CHECK(calificacion >= 1 AND calificacion <= 5),
  comentario TEXT,
  fecha_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  organizacion INTEGER CHECK(organizacion >= 1 AND organizacion <= 5),
  comunicacion INTEGER CHECK(comunicacion >= 1 AND comunicacion <= 5),
  actividades INTEGER CHECK(actividades >= 1 AND actividades <= 5),
  guia INTEGER CHECK(guia >= 1 AND guia <= 5),
  seguridad INTEGER CHECK(seguridad >= 1 AND seguridad <= 5),
  valor INTEGER CHECK(valor >= 1 AND valor <= 5),
  FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE CASCADE,
  FOREIGN KEY (autor_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (paquete_id) REFERENCES paquetes_turisticos(id) ON DELETE CASCADE
)
""")

# 2. Copiar los datos
cursor.execute("INSERT INTO reviews_new SELECT * FROM reviews")

# 3. Eliminar la tabla original
cursor.execute("DROP TABLE reviews")

# 4. Renombrar la tabla nueva
cursor.execute("ALTER TABLE reviews_new RENAME TO reviews")

conn.commit()
conn.close()

print("Migración completada. Ahora reserva_id es opcional.")