from rest_framework import permissions
from .models import PerfilUsuario


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permite consultar información, pero solo usuarios
    administrativos pueden modificarla.
    """

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user.is_staff)


class TieneRolDB(permissions.BasePermission):
    """
    Comprueba el rol del usuario mediante PerfilUsuario.
    """

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        try:
            rol_del_usuario = request.user.perfil.rol.nombre
        except (AttributeError, PerfilUsuario.DoesNotExist):
            return False

        if request.method in permissions.SAFE_METHODS:
            return rol_del_usuario in [
                "ADMINISTRADOR",
                "CLIENTE",
                "MANICURISTA"
            ]

        return rol_del_usuario == "ADMINISTRADOR"


class EsAdministrador(permissions.BasePermission):
    """
    Permite el acceso únicamente al administrador.
    """

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol.nombre == "ADMINISTRADOR"
        except (AttributeError, PerfilUsuario.DoesNotExist):
            return False


class EsCliente(permissions.BasePermission):
    """
    Permite el acceso únicamente a clientes.
    """

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol.nombre == "CLIENTE"
        except (AttributeError, PerfilUsuario.DoesNotExist):
            return False


class EsManicurista(permissions.BasePermission):
    """
    Permite el acceso únicamente a manicuristas.
    """

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol.nombre == "MANICURISTA"
        except (AttributeError, PerfilUsuario.DoesNotExist):
            return False