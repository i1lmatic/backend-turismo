-- Sistema de Paquetes Turísticos - Backend con FastAPI y SQLite
-- Esquema optimizado para SQLite con JWT

-- Tabla de usuarios con autenticación JWT
CREATE TABLE usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  nombre TEXT NOT NULL,
  apellido TEXT NOT NULL,
  telefono TEXT,
  fecha_nacimiento DATE,
  genero TEXT,
  pais TEXT,
  ciudad TEXT,
  direccion TEXT,
  codigo_postal TEXT,
  es_operador BOOLEAN DEFAULT 0,
  es_verificado BOOLEAN DEFAULT 0,
  fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ultimo_acceso TIMESTAMP,
  avatar_url TEXT,
  -- Campos para operadores turísticos
  descripcion_perfil TEXT,
  idiomas TEXT, -- JSON string de idiomas
  respuesta_tiempo_horas INTEGER
);

-- Tabla de paquetes turísticosm
CREATE TABLE paquetes_turisticos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  operador_id INTEGER NOT NULL,
  titulo TEXT NOT NULL,
  descripcion TEXT,
  tipo_paquete TEXT NOT NULL CHECK(tipo_paquete IN ('aventura', 'cultural', 'gastronomico', 'playa', 'montaña', 'ciudad', 'ecoturismo', 'romantico', 'familiar', 'negocios')),
  duracion_dias INTEGER NOT NULL CHECK(duracion_dias > 0),
  capacidad_maxima INTEGER NOT NULL CHECK(capacidad_maxima > 0),
  nivel_dificultad TEXT NOT NULL CHECK(nivel_dificultad IN ('facil', 'moderado', 'dificil', 'extremo')),
  precio_por_persona DECIMAL(10,2) NOT NULL CHECK(precio_por_persona > 0),
  precio_niño DECIMAL(10,2) DEFAULT 0 CHECK(precio_niño >= 0),
  incluye_transporte BOOLEAN DEFAULT 0,
  incluye_alojamiento BOOLEAN DEFAULT 0,
  incluye_comidas BOOLEAN DEFAULT 0,
  incluye_guia BOOLEAN DEFAULT 0,
  -- Ubicación
  destino TEXT GENERATED ALWAYS AS (ciudad_destino || ', ' || pais_destino) STORED,
  pais_destino TEXT NOT NULL,
  ciudad_destino TEXT NOT NULL,
  punto_encuentro TEXT NOT NULL,
  latitud DECIMAL(10,8),
  longitud DECIMAL(11,8),
  -- Estado y configuración
  esta_activo BOOLEAN DEFAULT 1,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  -- Horarios y políticas
  hora_inicio TEXT DEFAULT '09:00',
  hora_fin TEXT DEFAULT '18:00',
  edad_minima INTEGER DEFAULT 0,
  requiere_experiencia BOOLEAN DEFAULT 0,
  permite_cancelacion BOOLEAN DEFAULT 1,
  dias_cancelacion INTEGER DEFAULT 7,
  -- Servicios incluidos (como JSON string)
  servicios_incluidos TEXT,
  FOREIGN KEY (operador_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla de imágenes de paquetes turísticos
CREATE TABLE imagenes_paquetes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  paquete_id INTEGER NOT NULL,
  url_imagen TEXT NOT NULL,
  es_principal BOOLEAN DEFAULT 0,
  orden INTEGER DEFAULT 0,
  fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (paquete_id) REFERENCES paquetes_turisticos(id) ON DELETE CASCADE
);

-- Tabla de reservas
CREATE TABLE reservas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  paquete_id INTEGER NOT NULL,
  turista_id INTEGER NOT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  numero_personas INTEGER NOT NULL CHECK(numero_personas > 0),
  numero_adultos INTEGER NOT NULL CHECK(numero_adultos > 0),
  numero_niños INTEGER DEFAULT 0 CHECK(numero_niños >= 0),
  precio_total DECIMAL(10,2) NOT NULL CHECK(precio_total > 0),
  precio_por_persona DECIMAL(10,2) NOT NULL CHECK(precio_por_persona > 0),
  precio_niños DECIMAL(10,2) DEFAULT 0 CHECK(precio_niños >= 0),
  -- Información adicional
  necesidades_especiales TEXT,
  nivel_experiencia TEXT CHECK(nivel_experiencia IN ('principiante', 'intermedio', 'avanzado')),
  notas_adicionales TEXT,
  -- Estado de la reserva
  estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'confirmada', 'cancelada', 'completada')),
  -- Información de pago
  metodo_pago TEXT,
  pagado BOOLEAN DEFAULT 0,
  fecha_pago TIMESTAMP,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (paquete_id) REFERENCES paquetes_turisticos(id) ON DELETE CASCADE,
  FOREIGN KEY (turista_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla de reviews
CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  reserva_id INTEGER NOT NULL,
  autor_id INTEGER NOT NULL,
  paquete_id INTEGER NOT NULL,
  calificacion INTEGER NOT NULL CHECK(calificacion >= 1 AND calificacion <= 5),
  comentario TEXT,
  fecha_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  -- Categorías específicas para turismo
  organizacion INTEGER CHECK(organizacion >= 1 AND organizacion <= 5),
  comunicacion INTEGER CHECK(comunicacion >= 1 AND comunicacion <= 5),
  actividades INTEGER CHECK(actividades >= 1 AND actividades <= 5),
  guia INTEGER CHECK(guia >= 1 AND guia <= 5),
  seguridad INTEGER CHECK(seguridad >= 1 AND seguridad <= 5),
  valor INTEGER CHECK(valor >= 1 AND valor <= 5),
  FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE CASCADE,
  FOREIGN KEY (autor_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (paquete_id) REFERENCES paquetes_turisticos(id) ON DELETE CASCADE
);


-- Tabla de favoritos
CREATE TABLE favoritos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario_id INTEGER NOT NULL,
  paquete_id INTEGER NOT NULL,
  fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (paquete_id) REFERENCES paquetes_turisticos(id) ON DELETE CASCADE,
  UNIQUE(usuario_id, paquete_id)
);

-- Tabla de disponibilidad de paquetes turísticos
CREATE TABLE disponibilidad (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  paquete_id INTEGER NOT NULL,
  fecha DATE NOT NULL,
  disponible BOOLEAN DEFAULT 1,
  precio_especial DECIMAL(10,2) CHECK(precio_especial > 0),
  cupos_disponibles INTEGER CHECK(cupos_disponibles >= 0),
  FOREIGN KEY (paquete_id) REFERENCES paquetes_turisticos(id) ON DELETE CASCADE,
  UNIQUE(paquete_id, fecha)
);

-- Índices para optimizar consultas
CREATE INDEX idx_paquetes_operador ON paquetes_turisticos(operador_id);
CREATE INDEX idx_paquetes_ubicacion ON paquetes_turisticos(pais_destino, ciudad_destino);
CREATE INDEX idx_paquetes_activos ON paquetes_turisticos(esta_activo);
CREATE INDEX idx_paquetes_tipo ON paquetes_turisticos(tipo_paquete);
CREATE INDEX idx_paquetes_precio ON paquetes_turisticos(precio_por_persona);
CREATE INDEX idx_paquetes_nivel ON paquetes_turisticos(nivel_dificultad);
CREATE INDEX idx_reservas_paquete ON reservas(paquete_id);
CREATE INDEX idx_reservas_turista ON reservas(turista_id);
CREATE INDEX idx_reservas_fechas ON reservas(fecha_inicio, fecha_fin);
CREATE INDEX idx_reservas_estado ON reservas(estado);
CREATE INDEX idx_reviews_paquete ON reviews(paquete_id);
CREATE INDEX idx_reviews_calificacion ON reviews(calificacion);
CREATE INDEX idx_favoritos_usuario ON favoritos(usuario_id);
CREATE INDEX idx_favoritos_paquete ON favoritos(paquete_id);
CREATE INDEX idx_disponibilidad_paquete_fecha ON disponibilidad(paquete_id, fecha);
CREATE INDEX idx_disponibilidad_fecha ON disponibilidad(fecha);
CREATE INDEX idx_usuarios_operador ON usuarios(es_operador);
CREATE INDEX idx_usuarios_verificado ON usuarios(es_verificado);