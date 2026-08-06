from django.db import models
from django.contrib.auth.models import User

class Rol(models.Model):
    # Ejemplo de registros: 'ADMINISTRADOR', 'VENDEDOR', 'CLIENTE'
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Rol: {self.rol.nombre if self.rol else 'Sin Rol'}"

    
class Clientes(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    color_piel = models.CharField(max_length=100)


    def __str__(self):
        return f"{self.id} - {self.nombre} {self.apellido}"


class Manicurista(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    fecha_ingreso = models.DateField()
    ESTADO = (
        ("Activa", "ACTIVA"),
        ("Inactiva", "INACTIVA"),
    )
    estado = models.CharField(
        max_length= 20,
        choices=ESTADO,
        default="Activa"
    )


    def __str__(self):
        return f"{self.id} - {self.nombre} {self.apellido}"




class Servicios(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField()
    descripcion = models.TextField(null=True, blank=True)
    ESTADOS = (
        ("Activo", "ACTIVO"),
        ("Inactivo", "INACTIVO"),
    )
    estado = models.CharField(choices=ESTADOS, default="Activo", max_length=8)
    duracion = models.IntegerField(
        help_text="Duracion en minutos"
    )


    def __str__(self):
        return f"{self.id} - {self.nombre}"






class Citas(models.Model):
    
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    manicurista = models.ForeignKey(Manicurista, on_delete=models.CASCADE)
    servicios = models.ForeignKey(Servicios, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    total = models.IntegerField()
    

    def __str__(self):
        return f"{self.id} - {self.cliente.nombre} {self.cliente.apellido} - {self.fecha} {self.hora}"

class Inventario(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    stock_minimo = models.IntegerField()
    precio_compra = models.IntegerField()
    fecha_compra = models.DateField()

    def __str__(self):
        return f"{self.id} - {self.nombre} "


class Pagos(models.Model):
    ESTADOS =(
        ("Pendiente","PENDIENTE"),
        ("Realizado","REALIZADO"),
        ("Fallido","FALLIDO"),

    )
    METODOS =(
        ("Wompi","WOMPI"),
        ("Mercado Pago","MERCADO PAGO"),
        ("Transferencia","TRANSFERENCIA"),

    )
    citas = models.ForeignKey(Citas, on_delete=models.CASCADE)
    fecha_pago = models.DateField(auto_now_add=True)
    metodo_pago = models.CharField(
        max_length=50,
        choices=METODOS,
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Pendiente"
    )
    valor = models.IntegerField()
    referencia = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Pago #{self.id}"
    
class Recibo(models.Model):
    ESTADOS =(
        ("Pendiente","PENDIENTE"),
        ("Realizado","REALIZADO"),

    )
    citas = models.ForeignKey(Citas, on_delete=models.CASCADE)
    fecha_pago = models.DateField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=100)
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Pendiente"
    )
    valor = models.IntegerField()

    def __str__(self):
        return f"Pago #{self.id}"

class Gastos(models.Model):
    concepto = models.CharField(max_length=100)
    valor = models.IntegerField()
    fecha = models.DateField()
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.concepto} - {self.valor}"



