
from django.contrib import admin
from .models import *


@admin.register(Clientes)


class ClientesAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "nombre",
        "apellido",
        "telefono",
        "email",
        "color_piel",
    ]


@admin.register(Manicurista)


class ManicuristaAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "nombre",
        "apellido",
        "telefono",
        "email",
        "especialidad",
        "fecha_ingreso",
        "estado"
    ]


@admin.register(Servicios)


class ServiciosAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "nombre",
        "precio",
        "duracion"
    ]
    search_fields = [
        "nombre"
    ]


@admin.register(Citas)


class CitasAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cliente",
        "manicurista",
        "servicios",
        "fecha",
        "hora",
        "total",
        "estado"
    ]

@admin.register(Inventario)


class InventarioAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "nombre",
        "cantidad",
        "stock_minimo",
        "precio_compra",
        "fecha_compra"
    ]
    search_fields = [
        "nombre"
    ]


@admin.register(Pagos)

class PagosAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "citas",
        "fecha_pago",
        "metodo_pago",
        "estado",
        "valor"
    ]
    search_fields = [
        "fecha_pago",
        "valor"

    ]

@admin.register(Notificaciones)

class NotificacionesAdmin(admin.ModelAdmin):
    list_display = [
        "cliente",
        "mensaje",
        "fecha",
        "leer"
    ]
    search_fields = [
        "fecha",
        "leer"

    ]

@admin.register(Perfil)

class PerfilAdmin(admin.ModelAdmin):
    list_display = [
        "usuario",
        "rol",
        "telefono"
    ]
    search_fields = [
        "rol"

    ]



