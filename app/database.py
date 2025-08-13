import sqlite3
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_path = Path("database.sqlite")
        self.connection: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establece conexión con SQLite"""
        try:
            self.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            # Habilitar foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Configurar para retornar diccionarios
            self.connection.row_factory = sqlite3.Row
            logger.info("Conexión a SQLite establecida correctamente")
        except Exception as e:
            logger.error(f"Error al conectar con SQLite: {e}")
            raise
    
    def _create_tables(self):
        """Crea las tablas si no existen"""
        try:
            # Verificar si las tablas ya existen
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
            
            if cursor.fetchone():
                logger.info("Las tablas ya existen, omitiendo creación")
                return
            
            with open("database.sql", "r", encoding="utf-8") as f:
                sql_script = f.read()
            
            # Ejecutar el script SQL
            self.connection.executescript(sql_script)
            self.connection.commit()
            logger.info("Tablas creadas correctamente")
        except Exception as e:
            logger.error(f"Error al crear tablas: {e}")
            raise
    
    def get_client(self):
        """Retorna la conexión de SQLite"""
        return self.connection
    
    def health_check(self) -> bool:
        """Verifica la salud de la conexión"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception as e:
            logger.error(f"Error en health check: {e}")
            return False
    
    def close(self):
        """Cierra la conexión"""
        if self.connection:
            self.connection.close()

# Instancia global de la base de datos
db = Database() 