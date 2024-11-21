from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),

    #-----------------------------------------------------------------------
    # Manejo de sesión
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),

    #-----------------------------------------------------------------------
    # Equipos
    path("crear_equipo/", views.crear_equipo, name="crear_equipo"),
    path("editar_equipo/<path:id>", views.editar_equipo ,name="editar_equipo"),
    path("eliminar_equipo/<path:id>", views.eliminar_equipo ,name="eliminar_equipo"),
    path("equipo/<path:id>", views.recoleccion_info, name="ver_info_equipo"),
    path("verificar_nombre_equipo/", views.verificar_nombre_equipo, name="verificar_nombre_equipo"),

    #-----------------------------------------------------------------------
    # Tareas
    path('crear_tarea/<path:id>', views.crear_task, name='crear_tarea'),
    path("editar_tarea/<int:id>", views.editar_task ,name="editar_tarea"),
    path("eliminar_tarea/<int:id>", views.eliminar_task ,name="eliminar_tarea"),
    # path("tarea/<path:id>", views.recoleccion_info ,name="ver_info_tarea"),


    path("perfil/", views.perfil, name="perfil")
    #-----------------------------------------------------------------------
    # Notificaciones

]