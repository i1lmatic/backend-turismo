from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from app.models.usuario import UsuarioLogin, UsuarioCreate, UsuarioResponse, Token
from app.auth.auth_handler import auth_handler
from app.auth.jwt_handler import jwt_handler
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticación - Sistema de Turismo"])

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UsuarioCreate):
    """Registra un nuevo usuario (turista u operador turístico)"""
    try:
        user = await auth_handler.register_user(user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UsuarioLogin):
    """Inicia sesión y retorna tokens JWT"""
    try:
        user = await auth_handler.authenticate_user(user_credentials.email, user_credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear tokens JWT con información del rol
        tokens = jwt_handler.create_tokens(
            str(user.id), 
            user.email, 
            user.es_operador, 
            user.es_verificado
        )
        
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresca el token de acceso usando el refresh token"""
    try:
        # Verificar refresh token
        token_data = jwt_handler.verify_token(refresh_token)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Obtener información actualizada del usuario de la base de datos
        from app.repositories.instances import usuario_repository
        user = await usuario_repository.get_user_by_id(token_data.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear nuevos tokens con información actualizada
        tokens = jwt_handler.create_tokens(
            str(user.id), 
            user.email, 
            user.es_operador, 
            user.es_verificado
        )
        
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al refrescar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/me", response_model=UsuarioResponse)
async def get_me(current_user: UsuarioResponse = Depends(auth_handler.get_current_user)):
    """Obtiene la información del usuario actual"""
    return current_user

@router.get("/me/role")
async def get_my_role(current_user: UsuarioResponse = Depends(auth_handler.get_current_user)):
    """Obtiene el rol del usuario actual (turista u operador turístico)"""
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "es_operador": current_user.es_operador,
        "role": "operador_turistico" if current_user.es_operador else "turista",
        "es_verificado": current_user.es_verificado
    }

@router.post("/logout")
async def logout():
    """Cierra sesión (el cliente debe eliminar los tokens)"""
    return {"message": "Sesión cerrada exitosamente"}

@router.post("/verify-email/{user_id}")
async def verify_email(user_id: str):
    """Verifica el email de un usuario (endpoint para administradores del sistema de turismo)"""
    try:
        from app.repositories.instances import usuario_repository
        user = await usuario_repository.verify_user(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return {"message": "Usuario verificado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al verificar email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        ) 