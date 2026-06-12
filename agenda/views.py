from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import IntegrityError
from .models import *
from django.db.models import Sum, Count
from django.contrib.auth import login, logout, authenticate


def index(request):
    return render(request, "index.html")


#CRUD CLIENTE


def ver_clientes(request):
    c = Clientes.objects.all()
    contexto = {
        "datos" : c
    }
    return render(request,"cliente/clientes.html", contexto)


def crear_clientes(request):
    if request.method == "POST":
        try:
            c = Clientes(
                nombre = request.POST.get('nombre'),
                apellido = request.POST.get('apellido'),
                telefono = request.POST.get('telefono'),
                email = request.POST.get('email'),
                color_piel = request.POST.get('color_piel'),
            )
            c.save()
            messages.success(request, "Cliente creado con exito!!")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect("agenda:clientes")
    else:
        return render(request,"cliente/formulario_cliente.html")
   


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
def ver_citas(request):
    c = Citas.objects.all()
    contexto ={
        "datos": c
    }
    return render(request,"cita/citas.html", contexto)




def crear_citas(request):
    if request.method == "POST":
        try:
            cliente_id = request.POST.get('cliente')
            manicurista_id = request.POST.get('manicurista')
            servicios_id = request.POST.get('servicios')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')

            estado = request.POST.get('estado')
            #Validar datos
            existe = Citas.objects.filter(fecha=fecha, hora=hora, manicurista_id = manicurista_id).exists()


            if existe:
                messages.error(request, "Horario no disponible")
                return redirect("agenda:citas")
            try:
                servicios = Servicios.objects.get(pk=servicios_id)
            except Servicios.DoesNotExist:
                messages.error(request, "El servicio no existe")
                return redirect("agenda:citas")
            
            c = Citas(
                cliente_id = cliente_id,
                fecha =fecha,
                hora = hora,
                manicurista_id = manicurista_id,
                servicios_id = servicios_id,
                estado = estado,
                total = servicios.precio
            )
            c.save()
            Notificaciones.objects.create(
                cliente_id = cliente_id,
                mensaje = (
                    f"Cita agendada"
                    f"Fecha: {fecha}"
                    f"Hora {hora}"
                )
            )
            Pagos.objects.create(
                cita = c,
                metodo_pago ="Pendiente",
                estado = "Pendiente",
                valor = c.total
            )
            messages.success(request, "Cita agendada correctamente")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect("agenda:citas")
    else:
        cliente = Clientes.objects.all()
        manicurista = Manicurista.objects.all()
        servicios = Servicios.objects.all()
        contexto = {
            "clientes": cliente,
            "manicurista": manicurista,
            "servicios": servicios


        }
        return render(request, "cita/formulario_cita.html", contexto)


def eliminar_citas(request, id):
    try:
        q = Citas.objects.get(pk=id)
        q.delete()
        messages.success(request,"Cita eliminada correctamente")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("agenda:citas")


def actualizar_citas(request, id):
    if request.method == "POST":
        try:
            q =Citas.objects.get(pk=id)
            cliente_id = request.POST.get('cliente')
            manicurista_id = request.POST.get('manicurista')
            servicios_id = request.POST.get('servicios')
            fecha =request.POST.get('fecha')
            hora =request.POST.get('hora')
            estado = request.POST.get('estado')
        #validar
            existe = Citas.objects.filter(fecha = fecha, hora= hora, manicurista_id= manicurista_id).exclude(pk=id).exists()
            if existe:
                messages.error(request, "Horario no disponible")
                return redirect("agenda:citas")
            try:
                servicios = Servicios.objects.get(pk=servicios_id)
            except Servicios.DoesNotExist:
                messages.error(request, "El servicio no existe")
                return redirect("agenda:citas")
            
            q.cliente_id = cliente_id
            q.manicurista_id = manicurista_id
            q.servicios_id = servicios_id
            q.fecha = fecha
            q.hora = hora
            q.estado = estado
            q.total = servicios.precio
            q.save()


            messages.success(request, "Cita actualizada!!")
       
        except Exception as e:
            messages.error(request,f"Error: {e}")
        return redirect("agenda:citas")
    else:
        q = Citas.objects.get(pk=id)
        clientes= Clientes.objects.all()
        manicuristas= Manicurista.objects.all()
        servicios= Servicios.objects.all()
        contexto = {
            "datos": q,
            "clientes":clientes,
            "manicurista":manicuristas,
            "servicios": servicios
        }
        return render(request, "cita/formulario_cita.html", contexto)


#CRUD MANICURISTA


def ver_manicurista(request):
    m = Manicurista.objects.all()
    contexto = {
        "datos" : m
    }
    return render(request,"manicurista/manicuristas.html", contexto)


def crear_manicuristas(request):
    if request.method == "POST":
        try:
            m = Manicurista(
                nombre = request.POST.get('nombre'),
                apellido = request.POST.get('apellido'),
                telefono = request.POST.get('telefono'),
                email = request.POST.get('email'),
                especialidad = request.POST.get('especialidad'),
                fecha_ingreso = request.POST.get('fecha_ingreso'),
                estado = request.POST.get('estado'),
            )
            m.save()
            messages.success(request, "Manicurista creada con exito!!")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect("agenda:manicuristas")
    else:
        return render(request,"manicurista/formulario_manicuristas.html")
   


def eliminar_manicurista(request, id):
    try:
        m = Manicurista.objects.get(pk=id)
        m.delete()
        messages.success(request, f"Manicurista '{m.nombre}' eliminada")
    except IntegrityError:
        messages.info(request,"Error, la manicurista cuenta con citas asociadas")
    except Clientes.DoesNotExist:
        messages.warning(request,"La manicurista no existe.")
    except Exception as e:
        messages.error(request,f"Error: {e}")
    return redirect("agenda:manicuristas")


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


def ver_servicio(request):
    s = Servicios.objects.all()
    contexto = {
        "datos" : s
    }
    return render(request,"servicio/servicios.html", contexto)


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
   


def eliminar_servicio(request, id):
    try:
        s = Servicios.objects.get(pk=id)
        s.delete()
        messages.success(request, f"Servicio '{s.nombre}' eliminado")
    except IntegrityError:
        messages.info(request,"Error al eliminar el servicio")
    except Clientes.DoesNotExist:
        messages.warning(request,"El servicio no existe.")
    except Exception as e:
        messages.error(request,f"Error: {e}")
    return redirect("agenda:servicios")


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
def ver_inventario(request):
    i = Inventario.objects.all()
    contexto = {
        "datos" : i
    }
    return render(request, "inventario/inventario.html", contexto)

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

def eliminar_inventario(request, id):
    try:
        i = Inventario.objects.get(pk=id)
        i.delete()
        messages.success(request, f"Producto '{i.nombre}' se eliminó correctamente")
    except IntegrityError:
        messages.info(request,"Error al eliminar el producto")
    except Clientes.DoesNotExist:
        messages.warning(request,"El producto no existe.")
    except Exception as e:
        messages.error(request,f"Error: {e}")
    return redirect("agenda:inventario")

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
    try:
        pago_recibo = Pagos.objects.get(pk=id)
        contexto = {
            "pagos": pago_recibo,
        }
        return render(request,"recibo/recibo.html", contexto)
    except Pagos.DoesNotExist:
        messages.warning(request, "Pago no encontrado")
        return redirect("agenda:pagos")



#CRUD GASTOS
def ver_gasto(request):
    g = Gastos.objects.all()
    contexto = {
        "datos" : g
    }
    return render(request, "gastos/gastos.html", contexto)

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

def eliminar_gastos(request, id):
    try:
        g = Gastos.objects.get(pk=id)
        g.delete()
        messages.success(request, f"Gasto eliminado correctamente")
    except IntegrityError:
        messages.info(request,"Error")
    except Clientes.DoesNotExist:
        messages.warning(request,"El gasto no existe.")
    except Exception as e:
        messages.error(request,f"Error: {e}")
    return redirect("agenda:gastos")

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

def ver_pagos (request):
    p =Pagos.objects.all()

    contexto = {
        "datos": p
    }

    return render(request, "pago/pago.html", contexto)

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

def eliminar_pago(request, id):
    try: 
        p =  Pagos.objects.get(pk=id)
        p.delete()
        messages.success(request, "Pago eliminado correctamente")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("agenda:pagos")

def actualizar_pago(request,id):
    if request.method == "POST":
        try:
            p= Pagos.objects.get(pk=id)
            citas_id = request.POST.get('citas')
            metodo_pago = request.POST.get('metodo_pago')
            estado = request.POST.get('estado')
            referencia = request.POST.get('referencia')

            c= Citas.objects.get(pk=id)
            p.citas_id = citas_id
            p.metodo_pago = metodo_pago
            p.estado = estado
            p.referencia = referencia
            p.valor = c.total
            p.save()
            messages.success(request, "Pago actualizado correctamente")
        except Exception as e:
            messages.error(request, f"Error: {e}")  
        return redirect("agenda:pagos")
    else:
        p = Pagos.objectos.get(pk=id)
        c= Citas.objects.all()
        contexto = {
            "datos": p,
            "citas": c
        }
        return render(request, "pago/formulario_pago.html", contexto)
    

def reportes(request):
    total_ingresos = Pagos.objects.filter(estado = "Realizado").aaggregate(total = Sum("valor"))
    total_gastos = Gastos.objects.aaggregate(total = Sum("valor"))
    total_citas = Citas.objects.count()
    servicio_popular = Citas.objects.values("Servicios__nombres").annotate(cantidad =Count("id")).order_by( "-Cantidad").first
    ingresos = total_ingresos["total"] or 0
    gastos = total_gastos["total"] or 0
    utilidad = ingresos - gastos 
    contexto = {
        "ingresos" : ingresos,
        "gastos": gastos,
        "utilidad" : utilidad,
        "citas" : total_citas,
        "servicio" : servicio_popular
    }

    return render(request, "reportes/reportes.html", contexto) 

def ver_notificaciones(request):
    n = (
        Notificaciones.objects.all().order_by("-fecha")
    )
    contexto = {
        "datos": n
    }
    return render(request, "notificaciones/notificaciones.html", contexto) 

def alerta_inventario(request):
    inventario_bajo = Inventario.objects.filter(cantidad__Ite = models.F("stock minimo"))

    contexto = {
        "inventario_bajo" : inventario_bajo

    }
    return render(request, "alerta_inventario/alerta_inventario.html", contexto) 



    



    







