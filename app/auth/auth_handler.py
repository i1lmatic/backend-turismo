from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import db
from app.auth.jwt_handler import jwt_handler
from app.models.usuario import UsuarioResponse, UsuarioCreate
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

class AuthHandler(object):
    def __init__(self):
        self.connection = db.get_client()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UsuarioResponse]:
        """Autentica un usuario (turista u operador turístico) con email y contraseña"""
        try:
            logger.info(f"Intentando autenticar usuario: {email}")
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM usuarios WHERE email = ?",
                (email,)
            )
            user_data = cursor.fetchone()
            if not user_data:
                logger.warning(f"Usuario no encontrado: {email}")
                return None
            user_dict = dict(user_data)
            logger.info(f"Usuario encontrado: {user_dict}")
            if not jwt_handler.verify_password(password, user_dict['password_hash']):
                logger.warning(f"Contraseña incorrecta para usuario: {email}")
                return None
            logger.info(f"Contraseña correcta para usuario: {email}")
            cursor.execute(
                "UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id = ?",
                (user_dict['id'],)
            )
            self.connection.commit()
            return UsuarioResponse(**user_dict)
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return None
    
    async def register_user(self, user_data: UsuarioCreate) -> UsuarioResponse:
        """Registra un nuevo usuario en el sistema de turismo (turista u operador turístico)"""
        try:
            logger.info(f"Intentando registrar usuario: {user_data.email}")
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT id FROM usuarios WHERE email = ?",
                (user_data.email,)
            )
            if cursor.fetchone():
                logger.warning(f"El email ya está registrado: {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado en nuestro sistema de turismo"
                )
            hashed_password = jwt_handler.get_password_hash(user_data.password)
            logger.info(f"Hash de contraseña generado para {user_data.email}")
            user_dict = user_data.dict()
            user_dict['password_hash'] = hashed_password
            del user_dict['password']
            logger.info(f"Datos a insertar en la base de datos: {user_dict}")
            cursor.execute("""
                INSERT INTO usuarios (
                    email, password_hash, nombre, apellido, telefono, 
                    fecha_nacimiento, genero, pais, ciudad, direccion, 
                    codigo_postal, avatar_url, es_verificado, es_operador, 
                    fecha_registro, ultimo_acceso
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                user_dict['email'], user_dict['password_hash'], user_dict['nombre'],
                user_dict['apellido'], user_dict.get('telefono'), user_dict.get('fecha_nacimiento'),
                user_dict.get('genero'), user_dict.get('pais'), user_dict.get('ciudad'),
                user_dict.get('direccion'), user_dict.get('codigo_postal'), user_dict.get('avatar_url'),
                user_dict.get('es_verificado', False), user_dict.get('es_operador', False)
            ))
            self.connection.commit()
            logger.info(f"Usuario registrado correctamente: {user_data.email}")
            cursor.execute(
                "SELECT * FROM usuarios WHERE email = ?",
                (user_data.email,)
            )
            created_user = dict(cursor.fetchone())
            logger.info(f"Usuario creado en la base de datos: {created_user}")
            return UsuarioResponse(**created_user)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error en registro: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> UsuarioResponse:
        """Obtiene el usuario actual basado en el token JWT"""
        try:
            token = credentials.credentials
            logger.info(f"Token recibido: {token}")
            token_data = jwt_handler.verify_token(token)
            logger.info(f"Token data decodificada: {token_data}")
            if token_data is None:
                logger.warning("Token inválido o expirado")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            # Buscar usuario en la base de datos
            cursor = self.connection.cursor()
            logger.info(f"Buscando usuario con id: {token_data.user_id}")
            cursor.execute(
                "SELECT * FROM usuarios WHERE id = ?",
                (token_data.user_id,)
            )
            user_data = cursor.fetchone()
            logger.info(f"Resultado de búsqueda de usuario: {user_data}")
            if not user_data:
                logger.warning("Usuario no encontrado en la base de datos")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no encontrado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return UsuarioResponse(**dict(user_data))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al obtener usuario actual: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error de autenticación",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_current_active_user(self, current_user: UsuarioResponse = Depends(lambda: auth_handler.get_current_user)) -> UsuarioResponse:
        """Verifica que el usuario esté activo y verificado"""
        if not current_user.es_verificado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario no verificado. Por favor, verifique su cuenta para acceder a todas las funciones."
            )
        return current_user
    
    async def get_current_operator(self, current_user: UsuarioResponse = Depends(lambda: auth_handler.get_current_user)) -> UsuarioResponse:
        """Verifica que el usuario actual sea un operador turístico verificado"""
        if not current_user.es_operador:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. Esta funcionalidad es solo para operadores turísticos."
            )
        if not current_user.es_verificado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Su cuenta de operador turístico aún no ha sido verificada. Contacte al soporte."
            )
        return current_user
    
    async def get_current_tourist(self, current_user: UsuarioResponse = Depends(lambda: auth_handler.get_current_user)) -> UsuarioResponse:
        """Verifica que el usuario actual sea un turista (no operador)"""
        if current_user.es_operador:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Esta funcionalidad es específica para turistas."
            )
        return current_user

# Instancia global del manejador de autenticación
auth_handler = AuthHandler() 