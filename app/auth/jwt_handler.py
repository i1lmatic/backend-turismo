from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError,jwt
from passlib.context import CryptContext
from app.config import settings
from app.models.usuario import TokenData
import logging

logger = logging.getLogger(__name__)

class JWTHandler(object):
    """Manejador de tokens JWT para el sistema de turismo"""
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = settings.jwt_refresh_token_expire_days
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña coincide con el hash almacenado"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error al verificar contraseña: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Genera el hash seguro de la contraseña usando bcrypt"""
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Error al generar hash de contraseña: {e}")
            raise
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crea un token de acceso JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Crea un token de refresco JWT"""
        to_encode = data.copy()
        expire = datetime.now() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verifica y decodifica un token JWT del sistema de turismo"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            
            if user_id is None or email is None:
                logger.warning("Token inválido: falta user_id o email")
                return None
            
            # Validar tipo de token si está presente
            token_type = payload.get("type")
            if token_type and token_type not in ["access", "refresh"]:
                logger.warning(f"Tipo de token inválido: {token_type}")
                return None
            
            return TokenData(user_id=user_id, email=email)
        except JWTError as e:
            logger.error(f"Error al verificar token JWT: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al verificar token: {e}")
            return None
    
    def extract_user_info_from_token(self, token: str) -> Optional[dict]:
        """Extrae información completa del usuario desde el token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "es_operador": payload.get("es_operador", False),
                "es_verificado": payload.get("es_verificado", False),
                "user_type": payload.get("user_type", "turista"),
                "token_type": payload.get("type", "access")
            }
        except JWTError as e:
            logger.error(f"Error al extraer información del token: {e}")
            return None
    
    def validate_token_for_operation(self, token: str, required_role: str = None) -> bool:
        """Valida si un token es válido para una operación específica"""
        try:
            user_info = self.extract_user_info_from_token(token)
            if not user_info:
                return False
            
            # Validar rol si es requerido
            if required_role == "operador" and not user_info.get("es_operador"):
                return False
            elif required_role == "turista" and user_info.get("es_operador"):
                return False
            
            # Validar verificación para operaciones críticas
            if required_role == "operador" and not user_info.get("es_verificado"):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error al validar token para operación: {e}")
            return False
    
    def create_tokens(self, user_id: str, email: str, es_operador: bool = False, es_verificado: bool = False) -> dict:
        """Crea tokens de acceso y refresco para usuarios del sistema de turismo"""
        data = {
            "sub": user_id, 
            "email": email,
            "es_operador": es_operador,
            "es_verificado": es_verificado,
            "user_type": "operador_turistico" if es_operador else "turista"
        }
        access_token = self.create_access_token(data)
        refresh_token = self.create_refresh_token(data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "user_type": data["user_type"],
            "es_verificado": es_verificado
        }

# Instancia global del manejador JWT
jwt_handler = JWTHandler() 