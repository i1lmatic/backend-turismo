from .usuario_repository import UsuarioRepository
from .paqueteturistico_repository import PaqueteTuristicoRepository
from .reserva_repository import ReservaRepository
from .review_repository import ReviewRepository
from .favorito_repository import FavoritoRepository

# Instancias de repositories
usuario_repository = UsuarioRepository()
paquete_turistico_repository = PaqueteTuristicoRepository()
reserva_repository = ReservaRepository()
review_repository = ReviewRepository()
favorito_repository = FavoritoRepository() 