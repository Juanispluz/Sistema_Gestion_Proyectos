from django.contrib import admin
from .models import *

# Register your models here.

class Usuario_Admin(admin.ModelAdmin):
    list_display = ["correo", "nombre", "rol","password"]

class Tareas_Admin(admin.ModelAdmin):
    list_display = ["id", "titulo", "descripcion", "fecha_limite", "prioridad", "estado", "observaciones"]

class Equipos_Admin(admin.ModelAdmin):
    list_display = ['nombre_equipo', 'usuario_lider_id']

class Observaciones_Tareas_Admin(admin.ModelAdmin):
    list_display = ['id', 'usuario_observacion', 'tarea_id', 'obsevaciones_cambiada']

class Equipos_Desarrollo_Admin(admin.ModelAdmin):
    list_display = ['id', 'nombre_equipo_id', 'desarrollador_id', 'tarea_id',]


admin.site.register(Usuarios, Usuario_Admin)
admin.site.register(Tareas, Tareas_Admin)
admin.site.register(Equipos, Equipos_Admin)
admin.site.register(Observaciones_Tareas, Observaciones_Tareas_Admin)
admin.site.register(Equipos_Desarrollo, Equipos_Desarrollo_Admin)
