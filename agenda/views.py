from django.shortcuts import render, redirect, get_object_or_404
from .models import Citas, Clientes, Manicurista, Servicios
from django.http import HttpResponse
from django.contrib import messages
from django.db import IntegrityError
from .models import *
from .utils import validar_password


import json
# importar las serializaciones de los modelos
from .serializador import *

# importar el módulo de ViewSets para las vistas de las API's
from rest_framework import viewsets

from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Servicios
from .permissions import *
from .permissions import IsStaffOrReadOnly  # <--- Importa tu permiso
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg, Max, Min, Q  # Herramientas analíticas avanzadas

from rest_framework.decorators import action
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .utils import validar_password, requiere_rol


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Elimina el token asociado al usuario de la petición
        request.user.auth_token.delete()
        return Response(
            {"message": "Sesión cerrada correctamente. Token destruido."}, 
            status=status.HTTP_200_OK
        )


    
# Vistas para las APIs
class ClientesViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, TieneRolDB]


    queryset = Clientes.objects.all()
    serializer_class = ClientesSerializer


class ManicuristaViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]


    queryset = Manicurista.objects.all()
    serializer_class = ManicuristaSerializer


class ServiciosViewSet(viewsets.ModelViewSet):
    queryset = Servicios.objects.all()
    serializer_class = ServiciosSerializer
        
    # Combinamos IsAuthenticated para obligar a usar token, e IsStaffOrReadOnly para el rol
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly, TieneRolDB]

    # =========================================================================
    # ENDPOINT 1: DASHBOARD DE ESTADÍSTICAS (GET /api/servicios/dashboard/)
    # =========================================================================
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        # Mapeo y conteo de estados en la BD
        total_servicios = self.queryset.count()
        activos = self.queryset.filter(estado="Activo").count()
        inactivos = self.queryset.filter(estado="Inactivo").count()

        # Operaciones matemáticas directas en el motor de base de datos
        metricas_financieras = self.queryset.aggregate(
            recaudacion_total=Sum('precio'),
            costo_promedio=Avg('precio'),
            servicio_mas_caro=Max('precio'),
            servicio_mas_barato=Min('precio')
        )

        return Response({
            "contadores": {
                "total_registrados": total_servicios,
                "servicios_activos": activos,
                "servicios_inactivos": inactivos,
            },
            "finanzas": {
                "suma_total_costos": metricas_financieras['recaudacion_total'] or 0,
                "promedio_costo": round(metricas_financieras['costo_promedio'] or 0, 2),
                "precio_maximo": metricas_financieras['servicio_mas_caro'] or 0,
                "precio_minimo": metricas_financieras['servicio_mas_barato'] or 0
            }
        }, status=status.HTTP_200_OK)

    # =========================================================================
    # ENDPOINT 2: BÚSQUEDA AVANZADA MULTI-CAMPO (GET /api/servicios/buscar/?q=texto)
    # =========================================================================
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        query_texto = request.query_params.get('q', '').strip()

        if not query_texto:
            return Response(
                {"error": "Debes proporcionar un término de búsqueda en el parámetro 'q'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filtro con compuerta lógica OR buscando coincidencias parciales (case-insensitive)
        resultados = self.queryset.filter(
            Q(nombre__icontains=query_texto) | 
            Q(descripcion__icontains=query_texto)
        )

        serializer = self.get_serializer(resultados, many=True)
        
        return Response({
            "termino_buscado": query_texto,
            "total_coincidencias": resultados.count(),
            "resultados": serializer.data
        }, status=status.HTTP_200_OK)
    

    @extend_schema(
        summary="Lista de todos los servicios"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class CitasViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, TieneRolDB]
    queryset = Citas.objects.all()
    serializer_class = CitasSerializer

    @extend_schema(
        summary="Lista de todas las citas"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class InventarioViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAdminUser, EsAdministrador]


    queryset = Inventario.objects.all()
    serializer_class = InventarioSerializer

    @extend_schema(
        summary="Lista del inventario"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class PagosViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, TieneRolDB]

    queryset = Pagos.objects.all()
    serializer_class = PagosSerializer  

    @extend_schema(
        summary="Lista de todos los pagos"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ReciboViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAdminUser, EsAdministrador]
    queryset = Recibo.objects.all()
    serializer_class = ReciboSerializer

    @extend_schema(
        summary="Lista de todos los recibos"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class GastosViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAdminUser, EsAdministrador]


    queryset = Gastos.objects.all()
    serializer_class = GastosSerializer

    @extend_schema(
        summary="Lista de todos los gastos"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)




def index(request):
    return render(request, "index.html")

def login(request):
    if request.method == "POST":
        usuario = request.POST.get("user")
        clave = request.POST.get("password")

        # Autenticar utilizando el sistema de usuarios de Django
        user = authenticate(
            request,
            username=usuario,
            password=clave
        )

        # Verificar que las credenciales sean correctas
        if user is not None:

            # Verificar que tenga un PerfilUsuario y un Rol
            try:
                rol = user.perfil.rol.nombre
            except (AttributeError, PerfilUsuario.DoesNotExist):
                messages.error(
                    request,
                    "El usuario no tiene un rol asignado."
                )
                return redirect("agenda:login")

            # Iniciar sesión con Django
            auth_login(request, user)

            # Mantener temporalmente tu sesión actual
            request.session["logueado"] = {
                "id": user.id,
                "nombre": user.get_full_name() or user.username,
                "rol": rol
            }

            return redirect("agenda:dashboard")

        # Si las credenciales no son correctas
        messages.error(request, "Credenciales inválidas")
        return redirect("agenda:login")

    return render(request, "login.html")

"""def login(request):
    if request.method == "POST":
        usuario = request.POST.get("user")
        clave = request.POST.get("password")

        try:
            q = Manicurista.objects.get(email=usuario, password=clave)

            request.session["logueado"] = {
                "id": q.id,
                "nombre": f"{q.nombre} {q.apellido}",
                "rol": "Manicurista"
            }

            return redirect("agenda:dashboard")

        except Manicurista.DoesNotExist:
            pass
        

        try:
            q = Clientes.objects.get(email=usuario, password=clave)

            request.session["logueado"] = {
                "id": q.id,
                "nombre": f"{q.nombre} {q.apellido}",
                "rol": "Cliente"
            }

            return redirect("agenda:dashboard")

        except Clientes.DoesNotExist:
            messages.error(request, "Credenciales inválidas")
            return redirect("agenda:login")

    return render(request, "login.html") """




def register(request):
    if request.method == "POST":

        rol_nombre = request.POST.get("rol")
        password = request.POST.get("password")
        email = request.POST.get("email")

        # Solo permitimos estos dos roles desde el registro público
        if rol_nombre not in ["CLIENTE", "MANICURISTA"]:
            messages.error(request,"Rol de registro no válido.")
            return redirect("agenda:register")

        # Validar contraseña
        error = validar_password(password)

        if error:
            messages.error(request, error)
            return redirect("agenda:register")

        # Verificar correo
        if User.objects.filter(username=email).exists():
            messages.error(request,"Ya existe una cuenta con ese correo.")
            return redirect("agenda:register")

        try:
            with transaction.atomic():

                # Crear usuario Django
                user = User(
                    username=email,
                    email=email,
                    first_name=request.POST.get("nombre"),
                    last_name=request.POST.get("apellido")
                )

                user.set_password(password)
                user.save()

                # Buscar rol
                rol = Rol.objects.get(nombre=rol_nombre)

                # Crear perfil
                PerfilUsuario.objects.create(
                    user=user,
                    rol=rol
                )

                # Crear información adicional
                if rol_nombre == "CLIENTE":

                    Clientes.objects.create(
                        user=user,
                        nombre=request.POST.get("nombre"),
                        apellido=request.POST.get("apellido"),
                        telefono=request.POST.get("telefono"),
                        email=email,
                        color_piel=request.POST.get("color_piel")
                    )

                elif rol_nombre == "MANICURISTA":

                    Manicurista.objects.create(
                        user=user,
                        nombre=request.POST.get("nombre"),
                        apellido=request.POST.get("apellido"),
                        telefono=request.POST.get("telefono"),
                        email=email,
                        especialidad=request.POST.get("especialidad"),
                        fecha_ingreso=request.POST.get("fecha_ingreso")
                    )

            messages.success(request,"Cuenta creada correctamente. Ahora puedes iniciar sesión.")

            return redirect("agenda:login")

        except Rol.DoesNotExist:
            messages.error(request,f"El rol {rol_nombre} no existe en la base de datos.")

        except Exception as e:
            messages.error(request,f"Error al crear la cuenta: {e}")

    return render(request, "register.html")

@login_required(login_url="agenda:login")
def dashboard(request):

    try:
        rol = request.user.perfil.rol.nombre
    except (AttributeError, PerfilUsuario.DoesNotExist):
        messages.error(request,"Tu usuario no tiene un rol asignado.")
        return redirect("agenda:login")

    datos = request.session.get("logueado", {})

    cliente_id_logueado = None

    if rol == "CLIENTE":
        try:
            cliente = Clientes.objects.get(user=request.user)
            cliente_id_logueado = cliente.id
        except Clientes.DoesNotExist:
            messages.error(request,"No existe información de cliente asociada a tu usuario.")
            return redirect("agenda:login")

    citas = Citas.objects.filter(
        cliente_id=cliente_id_logueado
    ) if cliente_id_logueado else Citas.objects.none()

    servicios_disponibles = Servicios.objects.all()
    manicuristas_disponibles = Manicurista.objects.all()

    return render(request, "dashboard_copy.html", {
        "usuario": request.user.get_full_name() or request.user.username,
        "rol": rol,
        "citas": citas,
        "servicios": servicios_disponibles,
        "manicurista": manicuristas_disponibles,
        "cliente_id_logueado": cliente_id_logueado
    })



def logout(request):
    auth_logout(request)

    request.session.pop("logueado", None)

    messages.success( request,"Sesión cerrada correctamente.")

    return redirect("agenda:login")

"""def logout(request):
    try:
        del request.session["logueado"]
        messages.success(request, "Sesión cerrada")
        return redirect("agenda:login")
    except Exception as e:
        messages.warning(request, f"Error: {e}")
        return redirect("agenda:index")
    
"""
@requiere_rol("ADMINISTRADOR","MANICURISTA")
def ver_cliente(request):
    c = Clientes.objects.all()
    contexto = {
        "datos" : c
    }
    return render(request,"cliente/clientes.html", contexto)

@requiere_rol("ADMINISTRADOR")
def crear_cliente(request):
    if request.method == "POST":
        password = request.POST.get("password")
        email = request.POST.get("email")

        error = validar_password(password)

        if error:
            messages.error(request, error)
            return redirect("agenda:crear_cliente")

        # Verificar que el correo no esté registrado
        if User.objects.filter(username=email).exists():
            messages.error(
                request,
                "Ya existe un usuario registrado con ese correo."
            )
            return redirect("agenda:crear_cliente")

        try:
            with transaction.atomic():

                # 1. Crear usuario de Django
                user = User(
                    username=email,
                    email=email,
                    first_name=request.POST.get("nombre"),
                    last_name=request.POST.get("apellido")
                )

                # 2. Guardar contraseña de forma segura
                user.set_password(password)
                user.save()

                # 3. Buscar el rol CLIENTE
                rol = Rol.objects.get(nombre="CLIENTE")

                # 4. Crear PerfilUsuario
                PerfilUsuario.objects.create(
                    user=user,
                    rol=rol
                )

                # 5. Crear el cliente
                Clientes.objects.create(
                    user=user,
                    nombre=request.POST.get("nombre"),
                    apellido=request.POST.get("apellido"),
                    telefono=request.POST.get("telefono"),
                    email=email,
                    color_piel=request.POST.get("color_piel")
                )

            messages.success(request,"Cliente creado correctamente.")

            return redirect("agenda:login")

        except Rol.DoesNotExist:
            messages.error(request, "El rol CLIENTE no existe. Créalo primero.")

        except Exception as e:
            messages.error(request,f"Error al crear el cliente: {e}")

    return render(request, "cliente/crear_cliente.html")



@requiere_rol("ADMINISTRADOR")
def eliminar_cliente(request, id):
    try:
        q = Clientes.objects.get(pk=id)
        q.delete()
        messages.success(request, f"Cliente '{q.nombre}' eliminado")
    except IntegrityError:
        messages.info(request,"Error, el cliente cuenta con citas asociadas")
    except Clientes.DoesNotExist:
        messages.warning(request,"El cliente no existe.")
    except Exception as e:
        messages.error(request,f"Error: {e}")
    return redirect("agenda:clientes")

@requiere_rol("ADMINISTRADOR")
def actualizar_cliente(request, id):
    if request.method == "POST":
        try:
            q = Clientes.objects.get(pk=id)
            q.nombre = request.POST.get('nombre')
            q.apellido = request.POST.get('apellido')
            q.telefono = request.POST.get('telefono')
            q.email = request.POST.get('email')
            q.color_piel = request.POST.get('color_piel')
            q.save()
            messages.success(request, "Cliente Actualizado!!")
        except Exception as e:
            messages.error(request, f"Error: {e}")
       
        return redirect("agenda:clientes")
    else:
        q = Clientes.objects.get(pk=id)
        contexto ={
            "datos" : q
        }
        return render (request,"cliente/formulario_cliente.html", contexto)


#CRUD CITAS
@login_required(login_url="agenda:login")
@requiere_rol("CLIENTE")
def mis_citas(request):

    cliente = get_object_or_404(
        Clientes,
        user=request.user
    )

    citas = Citas.objects.filter(
        cliente=cliente
    )

    return render(request, "cliente/mis_citas.html", {
        "citas": citas
    })


@requiere_rol("ADMINISTRADOR")
def ver_citas(request):
    c = Citas.objects.all()
    contexto ={
        "datos": c
    }
    return render(request,"cita/citas.html", contexto)



@requiere_rol("CLIENTE")
@transaction.atomic
def crear_citas(request):


    cliente = get_object_or_404(
        Clientes,
        user=request.user
    )

    if request.method == "POST":
        try:
            manicurista_id = request.POST.get("manicurista")
            servicios_id = request.POST.get("servicios")
            fecha = request.POST.get("fecha")
            hora = request.POST.get("hora")

            manicurista = get_object_or_404(
                Manicurista,
                pk=manicurista_id
            )

            servicio = get_object_or_404(
                Servicios,
                pk=servicios_id
            )


            existe = Citas.objects.filter(
                fecha=fecha,
                hora=hora,
                manicurista=manicurista
            ).exists()

            if existe:
                messages.error( request,"Horario no disponible para la manicurista seleccionada.")
                return redirect("agenda:crear_citas")

            cita = Citas.objects.create(
                cliente=cliente,
                manicurista=manicurista,
                servicios=servicio,
                fecha=fecha,
                hora=hora,
                total=servicio.precio
            )

            messages.success(request, "Cita agendada correctamente.")

            return redirect("agenda:mis_citas")

        except Exception as e:
            messages.error(
                request,
                f"Error al crear la cita: {e}"
            )
            return redirect("agenda:crear_citas")

    # GET
    manicuristas = Manicurista.objects.filter(estado="Activa")

    servicios = Servicios.objects.filter(estado="Activo")

    contexto = {
        "cliente": cliente,
        "manicurista": manicuristas,
        "servicios": servicios
    }

    return render(
        request, "cliente/crear_cita.html", contexto)

@requiere_rol("CLIENTE")
def eliminar_citas(request, id):
    try:
        cliente = get_object_or_404(
            Clientes,
            user=request.user
        )

        cita = get_object_or_404(
            Citas,
            pk=id,
            cliente=cliente
        )

        cita.delete()

        messages.success(request,"Cita eliminada correctamente")

    except Exception as e:
        messages.error( request, f"Error: {e}")

    return redirect("agenda:mis_citas")

@requiere_rol("CLIENTE")
@transaction.atomic
def actualizar_citas(request, id):

    # Obtener el cliente relacionado con el usuario autenticado
    cliente = get_object_or_404(
        Clientes,
        user=request.user
    )

    # Buscar la cita SOLO si pertenece al cliente autenticado
    cita = get_object_or_404(
        Citas,
        pk=id,
        cliente=cliente
    )

    if request.method == "POST":
        try:
            manicurista_id = request.POST.get("manicurista")
            servicios_id = request.POST.get("servicios")
            fecha = request.POST.get("fecha")
            hora = request.POST.get("hora")

            # Verificar que la manicurista exista
            manicurista = get_object_or_404(
                Manicurista,
                pk=manicurista_id,
                estado="Activa"
            )

            # Verificar que el servicio exista
            servicio = get_object_or_404(
                Servicios,
                pk=servicios_id,
                estado="Activo"
            )

            # Verificar choque de horario
            existe = Citas.objects.filter(
                fecha=fecha,
                hora=hora,
                manicurista=manicurista
            ).exclude(
                pk=cita.id
            ).exists()

            if existe:
                messages.error(request, "Horario no disponible para la manicurista seleccionada.")
                return redirect("agenda:actualizar_citas",id=id)

            # Actualizar la cita
            cita.manicurista = manicurista
            cita.servicios = servicio
            cita.fecha = fecha
            cita.hora = hora
            cita.total = servicio.precio

            cita.save()

            messages.success(request,"Cita actualizada correctamente.")

            return redirect("agenda:mis_citas")

        except Exception as e:
            messages.error(request,f"Error al actualizar la cita: {e}")

            return redirect("agenda:actualizar_citas",id=id)

    # GET
    contexto = {
        "cita": cita,
        "cliente": cliente,
        "manicurista": Manicurista.objects.filter(
            estado="Activa"
        ),
        "servicios": Servicios.objects.filter(
            estado="Activo"
        ),
    }

    return render(request, "cliente/actualizar_citas.html",contexto)


#CRUD MANICURISTA

@requiere_rol("ADMINISTRADOR")
def ver_manicurista(request):
    m = Manicurista.objects.all()
    contexto = {
        "datos" : m
    }
    return render(request,"manicurista/manicuristas.html", contexto)

@requiere_rol("ADMINISTRADOR")
def crear_manicurista(request):
    if request.method == "POST":
        password = request.POST.get("password")
        email = request.POST.get("email")

        error = validar_password(password)

        if error:
            messages.error(request, error)
            return redirect("agenda:crear_manicuristas")

        # Verificar correo
        if User.objects.filter(username=email).exists():
            messages.error(
                request,
                "Ya existe un usuario registrado con ese correo."
            )
            return redirect("agenda:crear_manicuristas")

        try:
            with transaction.atomic():

                # 1. Crear usuario Django
                user = User(
                    username=email,
                    email=email,
                    first_name=request.POST.get("nombre"),
                    last_name=request.POST.get("apellido")
                )

                # 2. Contraseña segura
                user.set_password(password)
                user.save()

                # 3. Buscar rol MANICURISTA
                rol = Rol.objects.get(nombre="MANICURISTA")

                # 4. Crear perfil
                PerfilUsuario.objects.create(
                    user=user,
                    rol=rol
                )

                # 5. Crear manicurista
                Manicurista.objects.create(
                    user=user,
                    nombre=request.POST.get("nombre"),
                    apellido=request.POST.get("apellido"),
                    telefono=request.POST.get("telefono"),
                    email=email,
                    especialidad=request.POST.get("especialidad"),
                    fecha_ingreso=request.POST.get("fecha_ingreso")
                )

            messages.success(request,"Manicurista registrada correctamente.")

            return redirect("agenda:login")

        except Rol.DoesNotExist:
            messages.error(request,"El rol MANICURISTA no existe. Créalo primero.")

        except Exception as e:
            messages.error(request,f"Error al crear la manicurista: {e}")

    return render(request, "manicurista/crear_manicurista.html")
   

@requiere_rol("ADMINISTRADOR")
def eliminar_manicurista(request, id):
    try:
        m = Manicurista.objects.get(pk=id)
        m.delete()
        messages.success(request, f"Manicurista '{m.nombre}' eliminada")
    except IntegrityError:
        messages.info(request,"Error, la manicurista cuenta con citas asociadas")
    except Manicurista.DoesNotExist:
        messages.warning(request,"La manicurista no existe.")
    except Exception as e:
        messages.error(request,f"Error: {e}")
    return redirect("agenda:manicuristas")

@requiere_rol("ADMINISTRADOR")
def actualizar_manicurista(request, id):
    if request.method == "POST":
        try:
            m = Manicurista.objects.get(pk=id)
            m.nombre = request.POST.get('nombre')
            m.apellido = request.POST.get('apellido')
            m.telefono = request.POST.get('telefono')
            m.email = request.POST.get('email')
            m.especialidad = request.POST.get('especialidad')
            m.fecha_ingreso = request.POST.get('fecha_ingreso')
            m.estado = request.POST.get('estado')
            m.save()
            messages.success(request, "Manicurista actualizda correctamente")
        except Exception as e:
            messages.error(request, f"Error: {e}")
       
        return redirect("agenda:manicuristas")
    else:
        m = Manicurista.objects.get(pk=id)
        contexto ={
            "datos" : m
        }
        return render(request,"manicurista/formulario_manicuristas.html", contexto)

#CRUD SERVICIOS

@requiere_rol("ADMINISTRADOR", "CLIENTE", "MANICURISTA")
def ver_servicio(request):
    s = Servicios.objects.all()
    contexto = {
        "datos" : s
    }
    return render(request,"servicio/servicios.html", contexto)

@requiere_rol("ADMINISTRADOR")
def crear_servicio(request):
    if request.method == "POST":
        try:
            s = Servicios(
                nombre = request.POST.get('nombre'),
                precio = request.POST.get('precio'),
                descripcion = request.POST.get('descripcion'),
                duracion = request.POST.get('duracion'),
    
            )
            s.save()
            messages.success(request, "Servicio creado con exito!!")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect("agenda:servicios")
    else:
        return render(request,"servicio/formulario_servicio.html")
   

@requiere_rol("ADMINISTRADOR")
def eliminar_servicio(request, id):
    try:
        s = Servicios.objects.get(pk=id)
        s.delete()
        messages.success(request, f"Servicio '{s.nombre}' eliminado")
    except IntegrityError:
        messages.info(request,"Error al eliminar el servicio")
    except Servicios.DoesNotExist:
        messages.warning(request,"El servicio no existe.")
    except Exception as e:
        messages.error(request,f"Error: {e}")
    return redirect("agenda:servicios")

@requiere_rol("ADMINISTRADOR")
def actualizar_servicio(request, id):
    if request.method == "POST":
        try:
            s = Servicios.objects.get(pk=id)
            s.nombre = request.POST.get('nombre')
            s.precio = request.POST.get('precio')
            s.descripcion = request.POST.get('descripcion')
            s.duracion = request.POST.get('duracion')
            s.save()
            messages.success(request, "Servicio actualizado correctamente")
        except Exception as e:
            messages.error(request, f"Error: {e}")
       
        return redirect("agenda:servicios")
    else:
        s = Servicios.objects.get(pk=id)
        contexto ={
            "datos" : s
        }
        return render(request,"servicio/formulario_servicio.html", contexto)


#CRUD INVENTARIO
@requiere_rol("ADMINISTRADOR")
def ver_inventario(request):
    i = Inventario.objects.all()
    contexto = {
        "datos" : i
    }
    return render(request, "inventario/inventario.html", contexto)

@requiere_rol("ADMINISTRADOR")
def crear_inventario(request):
    if request.method == "POST":
        try:
            i = Inventario (
                nombre =request.POST.get('nombre'),
                cantidad =request.POST.get('cantidad'),
                stock_minimo = request.POST.get('stock_minimo'),
                precio_compra = request.POST.get('precio_compra'),
                fecha_compra =request.POST.get('fecha_compra')
            )
            i.save()
            messages.success(request, "Producto agregado correctamente")
        except Exception as e:
            messages.error(request, f"Error{e}")
        return redirect("agenda:inventario")
    
    else:
        return render(request,"inventario/formulario_inventario.html")

@requiere_rol("ADMINISTRADOR")
def eliminar_inventario(request, id):
    try:
        i = Inventario.objects.get(pk=id)
        i.delete()
        messages.success(request, f"Producto '{i.nombre}' se eliminó correctamente")
    except IntegrityError:
        messages.info(request,"Error al eliminar el producto")
    except Inventario.DoesNotExist:
        messages.warning(request,"El producto no existe.")
    except Exception as e:
        messages.error(request,f"Error: {e}")
    return redirect("agenda:inventario")

@requiere_rol("ADMINISTRADOR")
def actualizar_inventario(request, id):
    if request.method == "POST":
        try:
            i = Inventario.objects.get(pk=id)
            i.nombre = request.POST.get('nombre')
            i.cantidad = request.POST.get('cantidad')
            i.stock_minimo = request.POST.get('stock_minimo')
            i.precio_compra = request.POST.get('precio_compra')
            i.fecha_compra = request.POST.get('fecha_compra')
            i.save()
            messages.success(request, "Producto actualizado correctamente")
        except Exception as e:
            messages.error(request, f"Error: {e}")
       
        return redirect("agenda:inventario")
    else:
        i = Inventario.objects.get(pk=id)
        contexto ={
            "datos" : i
        }
        return render(request,"inventario/formulario_inventario.html", contexto)




def recibo(request, id):
    citas = Citas.objects.get(pk=id)
    contexto = {
        "citas": citas,
    }
    return render(request,"recibo/recibo.html", contexto)

#CRUD GASTOS
@requiere_rol("ADMINISTRADOR")
def ver_gasto(request):
    g = Gastos.objects.all()
    contexto = {
        "datos" : g
    }
    return render(request, "gastos/gastos.html", contexto)

@requiere_rol("ADMINISTRADOR")
def crear_gastos(request):
    if request.method == "POST":
        try:
            g = Gastos (
                concepto =request.POST.get('concepto'),
                valor =request.POST.get('valor'),
                fecha = request.POST.get('fecha'),
                descripcion = request.POST.get('descripcion')

            )
            g.save()
            messages.success(request, "Gasto registrado correctamente")
        except Exception as e:
            messages.error(request, f"Error{e}")
        return redirect("agenda:gastos")
    
    else:
        return render(request,"gastos/formulario_gastos.html")

@requiere_rol("ADMINISTRADOR")
def eliminar_gastos(request, id):
    try:
        g = Gastos.objects.get(pk=id)
        g.delete()
        messages.success(request, f"Gasto eliminado correctamente")
    except IntegrityError:
        messages.info(request,"Error")
    except Gastos.DoesNotExist:
        messages.warning(request,"El gasto no existe.")
    except Exception as e:
        messages.error(request,f"Error: {e}")
    return redirect("agenda:gastos")

@requiere_rol("ADMINISTRADOR")
def actualizar_gastos(request, id):
    if request.method == "POST":
        try:
            g = Gastos.objects.get(pk=id)
            g.concepto =request.POST.get('concepto')
            g.valor =request.POST.get('valor')
            g.fecha = request.POST.get('fecha')
            g.descripcion = request.POST.get('descripcion')
            g.save()
            messages.success(request, "Gasto actualizado correctamente")
        except Exception as e:
            messages.error(request, f"Error: {e}")
       
        return redirect("agenda:gastos")
    else:
        g = Gastos.objects.get(pk=id)
        contexto ={
            "datos" : g
        }
        return render(request,"gastos/formulario_gastos.html", contexto)

@requiere_rol("ADMINISTRADOR")
def ver_pagos (request):
    p =Pagos.objects.all()

    contexto = {
        "datos": p
    }

    return render(request, "pago/pago.html", contexto)

@requiere_rol("ADMINISTRADOR")
def crear_pago(request):
    if request.method  == "POST":
        try:
            citas_id = request.POST.get('citas')
            metodo_pago = request.POST.get('metodo_pago')
            estado = request.POST.get('estado')
            referencia = request.POST.get('referencias')

            citas = Citas.objects.get(pk= citas_id)
            existe = Pagos.objects.filter(citas_id = citas_id).exists()

            if existe:
                messages.warning(request, "Pago registrado con anterioridad")
                return redirect("agenda:pagos")
            p = Pagos(
                citas_id = citas_id,
                metodo_pago = metodo_pago,
                estado = estado,
                referencia = referencia,
                valor = citas.total
            )
            p.save()
            messages.success(request, "Pago registrado correctamente")
        except Exception as e: 
            messages.error(request, f"Error:{e}")
            return redirect("agenda:pagos")
    else:
        citas = Citas.objects.all()
        contexto = {
            "citas":citas
        }
        return render(request, "pago/formulario_pago.html", contexto)

@requiere_rol("ADMINISTRADOR")
def eliminar_pago(request, id):
    try: 
        p =  Pagos.objects.get(pk=id)
        p.delete()
        messages.success(request, "Pago eliminado correctamente")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("agenda:pagos")

@requiere_rol("ADMINISTRADOR")
def actualizar_pago(request, id):

    pago = get_object_or_404(
        Pagos,
        pk=id
    )

    if request.method == "POST":
        try:
            citas_id = request.POST.get("citas")
            metodo_pago = request.POST.get("metodo_pago")
            estado = request.POST.get("estado")
            referencia = request.POST.get("referencia")

            # Buscar la cita seleccionada
            cita = get_object_or_404(
                Citas,
                pk=citas_id
            )

            # Actualizar el pago
            pago.citas = cita
            pago.metodo_pago = metodo_pago
            pago.estado = estado
            pago.referencia = referencia
            pago.valor = cita.total

            pago.save()

            messages.success(request,"Pago actualizado correctamente")

            return redirect("agenda:pagos")

        except Exception as e:
            messages.error(request,f"Error al actualizar el pago: {e}")

            return redirect("agenda:actualizar_pago",id=id)

    # GET
    citas = Citas.objects.all()

    contexto = {
        "datos": pago,
        "citas": citas
    }

    return render(request,"pago/formulario_pago.html",contexto)