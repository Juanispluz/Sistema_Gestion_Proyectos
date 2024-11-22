from django.db import models

# Create your models here.

class  Usuarios(models.Model):
    correo = models.EmailField(max_length=254, primary_key=True)
    nombre = models.CharField(max_length=100)
    password = models.CharField(max_length=254)
    ROLES = (
        ('A', 'Administrador'),
        ('L', 'Lider'),
        ('D', 'Desarrollador'),
    )
    rol = models.CharField(max_length=1, choices=ROLES)

class Tareas(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=254, null=False, blank=False)
    fecha_limite = models.DateField(help_text="Formato dd-mm-YYYY")
    
    PRI = (
        ('A', 'Alta'),
        ('M', 'Media'),
        ('B', 'Baja'),
    )
    prioridad = models.CharField(max_length=1, choices=PRI)

    EST = (
        (1, 'Terminado'),
        (2, 'En proceso'),
        (3 , 'Pendiente'),
        (4, 'Cancelada'),
    )
    estado = models.IntegerField(choices=EST)

    observaciones = models.CharField(max_length=254)

class Equipos(models.Model):
    nombre_equipo = models.CharField(max_length=50, primary_key=True)
    usuario_lider_id = models.ForeignKey('Usuarios', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_equipo

    def lider_info(self):
        return f"Líder: {self.usuario_lider_id.correo}"


class Observaciones_Tareas(models.Model):
    id = models.AutoField(primary_key=True)
    usuario_observacion = models.ForeignKey('Usuarios', on_delete=models.CASCADE)
    tarea_id = models.ForeignKey('Tareas' ,on_delete=models.CASCADE)
    obsevaciones_cambiada = models.CharField(max_length=254, null=True, blank=True)
    
    def __str__(self):
        return f"Usuario: {self.usuario_observacion}, en Tarea: {self.tarea_id.id}"

class Equipos_Desarrollo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_equipo_id = models.ForeignKey('Equipos', on_delete=models.CASCADE)
    desarrollador_id = models.ForeignKey('Usuarios', on_delete=models.CASCADE)
    tarea_id = models.ForeignKey('Tareas' ,on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Equipo: {self.nombre_equipo_id.nombre_equipo}, Desarrollador: {self.desarrollador_id.correo}"
