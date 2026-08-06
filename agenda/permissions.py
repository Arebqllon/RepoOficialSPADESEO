from rest_framework import permissions
from .models import PerfilUsuario

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir que cualquiera lea los servicios,
    pero solo los usuarios de staff puedan modificarlos o crearlos.
    """
    def has_permission(self, request, view):
        # Permitir métodos seguros (GET, HEAD, OPTIONS) a cualquier usuario autenticado
        if request.method in permissions.SAFE_METHODS:
            return True

        # Solo permitir POST, PUT, DELETE si el usuario es staff (is_staff=True)
        return bool(request.user and request.user.is_staff)


class TieneRolDB(permissions.BasePermission):
    def has_permission(self, request, view):
        # 1. Bloquear si el usuario no viene autenticado por Token
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            # 2. Consultar directamente nuestra tabla en la base de datos
            rol_del_usuario = request.user.perfil.rol.nombre
        except (AttributeError, PerfilUsuario.DoesNotExist):
            return False # Bloquear si no tiene un perfil o rol asignado

        # 3. Definir directrices por Métodos HTTP
        if request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            # Permitir lectura a usuarios con roles ADMINISTRADOR o VENDEDOR
            return rol_del_usuario in ['ADMINISTRADOR', 'VENDEDOR']
        
        # Para mutaciones (POST, PUT, PATCH, DELETE) sobre el modelo Servicio
        # Restringir estrictamente a que su rol en la base de datos sea ADMINISTRADOR
        return rol_del_usuario == 'ADMINISTRADOR'