from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
import re


def requiere_rol(*roles):

    def decorador(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect("agenda:login")

            try:
                rol = request.user.perfil.rol.nombre
            except (AttributeError, Exception):
                messages.error(
                    request,
                    "No tienes un rol configurado."
                )
                return redirect("agenda:login")

            if rol not in roles:
                messages.error(
                    request,
                    "No tienes permisos para acceder a esta sección."
                )
                return redirect("agenda:dashboard")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorador


def validar_password(password):
    if len(password) < 8:
        return "La contraseña debe tener mínimo 8 caracteres"

    if not re.search(r"[A-Z]", password):
        return "Debe contener al menos una mayúscula"

    if not re.search(r"[a-z]", password):
        return "Debe contener al menos una minúscula"

    if not re.search(r"[0-9]", password):
        return "Debe contener al menos un número"

    return None