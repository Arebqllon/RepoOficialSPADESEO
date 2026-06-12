from django.urls import path
from . import views

app_name = "agenda"

urlpatterns = [
    path('', views.index, name="index"),

    #Clientes
    path('clientes/', views.ver_clientes, name="clientes"),
    path('crear_cliente/', views.crear_clientes, name="crear_cliente"),
    path('eliminar_cliente/<int:id>/', views.eliminar_cliente, name="eliminar_cliente"),
    path('actualizar_cliente/<int:id>/', views.actualizar_cliente, name="actualizar_cliente"),

    #Citas
    path('citas/', views.ver_citas, name="citas"),
    path('crear_cita/', views.crear_citas, name="crear_citas"),
    path('eliminar_cita/<int:id>/', views.eliminar_citas, name="eliminar_cita"),
    path('actualizar_cita/<int:id>/', views.actualizar_citas, name="actualizar_cita"),

    #Manicurista
    path('manicuristas/', views.ver_manicurista, name="ver_manicurista"),
    path('crear_manicuristas/', views.crear_manicuristas, name="crear_manicuristas"),
    path('eliminar_manicurista/<int:id>/', views.eliminar_manicurista, name="eliminar_manicurista"),
    path('actualizar_manicurista/<int:id>/', views.actualizar_manicurista, name="actualizar_manicurista"),

    #Servicio
    path('servicios/', views.ver_servicio, name="ver_servicio"),
    path('crear_servicio/', views.crear_servicio, name="crear_servicio"),
    path('eliminar_servicio/<int:id>/', views.eliminar_servicio, name="eliminar_servicio"),
    path('actualizar_servicio/<int:id>/', views.actualizar_servicio, name="actualizar_servicio"),

    
    #Inventario
    path('inventario/', views.ver_inventario, name="ver_inventario"),
    path('crear_inventario/', views.crear_inventario, name="crear_inventario"),
    path('eliminar_inventario/<int:id>/', views.eliminar_inventario, name="eliminar_inventario"),
    path('actualizar_inventario/<int:id>/', views.actualizar_inventario, name="actualizar_inventario"),

    #Pagos
    path('pagos/', views.ver_pagos, name="ver_pagos"),
    path('crear_pago/', views.crear_pago, name="crear_pago"),
    path('eliminar_pago/<int:id>/', views.eliminar_pago, name="eliminar_pago"),
    path('actualizar_pago/<int:id>/', views.actualizar_pago, name="actualizar_pago"),

    #recibo
    path('recibo/<int:id>/', views.recibo, name="recibo"),

    #Gastos
    path('gastos/', views.ver_gasto, name="ver_gasto"),
    path('crear_gastos/', views.crear_gastos, name="crear_gastos"),
    path('eliminar_gastos/<int:id>/', views.eliminar_gastos, name="eliminar_gastos"),
    path('actualizar_gastos/<int:id>/', views.actualizar_gastos, name="actualizar_gastos"),

    #Reportes
    path('reportes/', views.reportes, name="reportes"),

    #notificaciones
    path('notificaciones/', views.ver_notificaciones, name="ver_notificaciones"),

    #Alerta_inventario
    path('alerta/', views.alerta_inventario, name="alerta_inventario"),
]

