from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.db.models import Count, Q
from django.db import transaction

# Create your views here.

def index(request):
    if not request.session.get("logueado"):
        messages.error(request, "Debes iniciar sesión para acceder a esta página.")
        return redirect("login")
    rol = request.session.get('rol')
    correo = request.session.get('correo')
    equipos = []
    tareas_recientes = []
    if rol == 'L':
        equipos = Equipos.objects.filter(usuario_lider_id__correo=correo)
        tareas_recientes = Tareas.objects.filter(
            id__in=Equipos_Desarrollo.objects.filter(
                nombre_equipo_id__usuario_lider_id__correo=correo
            ).values_list('tarea_id', flat=True)
        ).order_by('-fecha_limite')
    elif rol == 'D':
        equipos = Equipos.objects.filter(
            nombre_equipo__in=Equipos_Desarrollo.objects.filter(
                desarrollador_id__correo=correo
            ).values_list('nombre_equipo_id__nombre_equipo', flat=True)
        )
        tareas_recientes = Tareas.objects.filter(
            id__in=Equipos_Desarrollo.objects.filter(
                desarrollador_id__correo=correo
            ).values_list('tarea_id', flat=True)
        ).order_by('-fecha_limite')
    return render(request, "index.html", {
        'equipos': equipos,
        'tareas_recientes': tareas_recientes
    })

def recoleccion_info(request, id):
    equipo = get_object_or_404(Equipos, nombre_equipo=id)
    miembros_tareas = Equipos_Desarrollo.objects.filter(nombre_equipo_id=equipo)
    miembros_unicos = set()
    tareas = []
    for miembro in miembros_tareas:
        desarrollador = miembro.desarrollador_id
        miembros_unicos.add(desarrollador)
        tarea = miembro.tarea_id
        tareas.append({
            'tarea': tarea,
            'desarrollador': desarrollador
        })
    context = {
        'equipo': equipo,
        'miembros': list(miembros_unicos),
        'tareas': tareas,
    }
    return render(request, 'equipos/equipo.html', context)

# -----------------------------------------------------------------------
# Manejo de sesión
def login(request):
    if request.session.get("logueado"):
        messages.error(request, "Ya estás logueado.")
        return redirect("index")
    if request.method == "POST":
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        try:
            usuario = Usuarios.objects.get(correo=correo)
            if check_password(password, usuario.password):
                request.session['logueado'] = True
                request.session['correo'] = usuario.correo
                request.session['rol'] = usuario.rol
                
                messages.success(request, "¡Bienvenido!")
                return redirect("index")
            else:
                messages.error(request, "Usuario y/o contraseña inválido(s)")
        except Usuarios.DoesNotExist:
            messages.error(request, "Usuario y/o contraseña inválido(s)")

    return render(request, "login/login.html")

def register(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        correo_confirm = request.POST.get('correo_confirm')
        rol = request.POST.get('rol')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        if Usuarios.objects.filter(correo=correo).exists():
            messages.error(request, "Error. Este usuario ya se encuentra registrado")
            return render(request, "login/register.html")
        if rol == 'A':
            messages.error(request, "No está permitido registrar usuarios con el rol 'A'.")
            return render(request, "login/register.html")
        if rol not in ['L', 'D']:
            messages.warning(request, "Debe seleccionar un rol.")
            return render(request, "login/register.html")
        if correo != correo_confirm:
            messages.warning(request, 'Los "CORREOS" deben de coincidir.')
            return render(request, "login/register.html")
        if password != password_confirm:
            messages.warning(request, 'Las "CONTRASEÑAS", deben de coincidir.')
            return render(request, "login/register.html")
        password_hashed = make_password(password)
        registro = Usuarios(
            correo=correo,
            nombre=nombre,
            password=password_hashed,
            rol=rol
        )
        registro.save()
        messages.success(request, "El usuario se registro con éxito.")
        return redirect("index")
    return render(request, "login/register.html")

def logout(request):
    try:
        del request.session["logueado"]
        return redirect("login")
    except:
        messages.error(request, "Error. Intente de nuevo...")
        return redirect("index")

# -----------------------------------------------------------------------
# Verificaciones
def verificar_correo_y_contraseña(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        password = request.POST.get("password")
        try:
            usuario = Usuarios.objects.get(correo=correo)
            if check_password(password, usuario.password):
                return JsonResponse({"valido": True, "mensaje": "Credenciales correctas."})
            else:
                return JsonResponse({"valido": False, "mensaje": "Contraseña incorrecta."})
        except Usuarios.DoesNotExist:
            return JsonResponse({"valido": False, "mensaje": "Correo no registrado."})
    return JsonResponse({"error": "Método no permitido"}, status=405)

def existencia_correo(request):
    if request.method == "GET":
        correo = request.GET.get("correo")
        existe = Usuarios.objects.filter(correo=correo).exists()
        return JsonResponse({
            "disponible": not existe,
            "mensaje": "Correo disponible." if not existe else "El correo ya está en uso."
        })
    return JsonResponse({"error": "Método no permitido"}, status=405)

def verificar_nombre_equipo(request):
    nombre_equipo = request.GET.get('nombre_equipo')
    disponible = not Equipos.objects.filter(nombre_equipo=nombre_equipo).exists()
    return JsonResponse({"disponible": disponible})

# -----------------------------------------------------------------------
# Equipos
def crear_equipo(request):
    if request.method == 'POST':
        nombre_equipo = request.POST.get('nombre_equipo')
        desarrolladores_seleccionados = request.POST.getlist('desarrolladores')
        if Equipos.objects.filter(nombre_equipo=nombre_equipo).exists():
            messages.error(request, "Error: el nombre del equipo ya está registrado.")
            return redirect("crear_equipo")
        if not request.session.get('logueado'):
            messages.error(request, "Debes estar logueado para crear un equipo.")
            return redirect("login")
        correo_lider = request.session.get('correo')
        try:
            lider = Usuarios.objects.get(correo=correo_lider, rol='L')
            equipo = Equipos.objects.create(nombre_equipo=nombre_equipo, usuario_lider_id=lider)
            for desarrollador_correo in desarrolladores_seleccionados:
                desarrollador = Usuarios.objects.get(correo=desarrollador_correo, rol='D')
                Equipos_Desarrollo.objects.create(nombre_equipo_id=equipo, desarrollador_id=desarrollador)
            messages.success(request, "Equipo creado exitosamente.")
            return redirect("index")
        except Usuarios.DoesNotExist:
            messages.error(request, "Error: usuario líder no válido.")
            return redirect("crear_equipo")
    lideres = Usuarios.objects.filter(rol='L')
    desarrolladores = Usuarios.objects.filter(rol='D').annotate(
        num_equipos=models.Count('equipos_desarrollo')
    ).filter(num_equipos__lt=10)
    return render(request, "equipos/crear_equipo.html", {
        "lideres": lideres, 
        "desarrolladores": desarrolladores,
    })

def editar_equipo(request, id):
    equipo = get_object_or_404(Equipos, nombre_equipo=id)
    if request.method == 'POST':
        nuevo_nombre = request.POST.get('nombre_equipo')
        nuevo_lider_id = request.POST.get('usuario_lider')
        miembros = request.POST.getlist('desarrolladores')
        if nuevo_nombre and Equipos.objects.filter(nombre_equipo=nuevo_nombre).exclude(nombre_equipo=id).exists():
            messages.error(request, "Error: el nombre del equipo ya está en uso.")
            return redirect('editar_equipo', id=id)
        if nuevo_nombre:
            equipo.nombre_equipo = nuevo_nombre
        if nuevo_lider_id:
            equipo.usuario_lider_id = Usuarios.objects.get(correo=nuevo_lider_id)
        equipo.save()
        for registro in Equipos_Desarrollo.objects.filter(nombre_equipo_id=equipo):
            if not registro.tarea_id:
                registro.delete()
        for miembro_correo in miembros:
            desarrollador = Usuarios.objects.get(correo=miembro_correo, rol='D')
            if not Equipos_Desarrollo.objects.filter(nombre_equipo_id=equipo, desarrollador_id=desarrollador).exists():
                Equipos_Desarrollo.objects.create(nombre_equipo_id=equipo, desarrollador_id=desarrollador)
        messages.success(request, "Equipo actualizado correctamente.")
        return redirect('index')
    lideres = Usuarios.objects.filter(rol='L')
    miembros_actuales = Equipos_Desarrollo.objects.filter(nombre_equipo_id=equipo)
    desarrolladores_disponibles = Usuarios.objects.filter(
        rol='D'
    ).exclude(
        correo__in=miembros_actuales.values_list('desarrollador_id__correo', flat=True)
    )
    return render(request, "equipos/crear_equipo.html", {
        'equipo': equipo,
        'lideres': lideres,
        'desarrolladores': desarrolladores_disponibles,
        'miembros_actuales': miembros_actuales,
        'editar': True,
        'gestionar_equipo': True
    })

def eliminar_equipo(request, id):
    equipo = get_object_or_404(Equipos, nombre_equipo=id)
    tareas_asociadas = Tareas.objects.filter(equipos_desarrollo__nombre_equipo_id=equipo)
    if tareas_asociadas.exists():
        tareas_no_terminadas = tareas_asociadas.exclude(estado__in=[1, 4])
        if tareas_no_terminadas.exists():
            messages.error(request, "No se puede eliminar el equipo porque hay tareas pendientes o en proceso.")
            return redirect("index")
        for tarea in tareas_asociadas:
            if tarea.estado in [1, 4]:
                Observaciones_Tareas.objects.filter(tarea_id=tarea).delete()
        tareas_asociadas.filter(estado__in=[1, 4]).delete()
    Equipos_Desarrollo.objects.filter(nombre_equipo_id=equipo).delete()
    equipo.delete()

    messages.success(request, "Equipo eliminado exitosamente.")
    return redirect("index")

# -----------------------------------------------------------------------
# Tareas
def crear_task(request, id):
    equipo = get_object_or_404(Equipos, nombre_equipo=id)
    desarrolladores = Usuarios.objects.filter(
        rol='D'
    ).annotate(
        equipo_count=Count('equipos_desarrollo')
    ).filter(
        Q(equipo_count__lt=10) | Q(equipo_count__isnull=True)
    )
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        fecha_limite = request.POST.get('fecha_limite')
        prioridad = request.POST.get('prioridad')
        estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones')
        desarrolladores_seleccionados = request.POST.getlist('desarrolladores')

        if len(desarrolladores_seleccionados) > 5:
            messages.error(request, "Solo puedes seleccionar máximo 5 desarrolladores")
            return redirect('crear_tarea', id=id)
        tarea = Tareas.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            fecha_limite=fecha_limite,
            prioridad=prioridad,
            estado=estado,
            observaciones=observaciones,
        )
        for desarrollador_correo in desarrolladores_seleccionados:
            desarrollador = Usuarios.objects.get(correo=desarrollador_correo)
            Equipos_Desarrollo.objects.create(
                nombre_equipo_id=equipo,
                desarrollador_id=desarrollador,
                tarea_id=tarea 
            )
        messages.success(request, "Tarea creada exitosamente")
        return redirect('ver_info_equipo', id=id)
    context = {
        'equipo': equipo,
        'desarrolladores': desarrolladores,
    }
    return render(request, "tasks/crear_task.html", context)

def editar_task(request, id):
    tarea = get_object_or_404(Tareas, id=id)
    equipo = tarea.equipos_desarrollo_set.first().nombre_equipo_id
    desarrolladores_tarea = list(Equipos_Desarrollo.objects.filter(
        tarea_id=tarea
    ).values_list('desarrollador_id__correo', flat=True))
    desarrolladores = Usuarios.objects.filter(
        rol='D'
    ).annotate(
        equipo_count=Count('equipos_desarrollo')
    ).filter(
        Q(equipo_count__lt=10) | Q(equipo_count__isnull=True)
    )
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        fecha_limite = request.POST.get('fecha_limite')
        prioridad = request.POST.get('prioridad')
        estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones')
        desarrolladores_seleccionados = request.POST.getlist('desarrolladores')
        if len(desarrolladores_seleccionados) > 5:
            messages.error(request, "Solo puedes seleccionar máximo 5 desarrolladores")
            return redirect('editar_tarea', id=id)
        tarea.titulo = titulo
        tarea.descripcion = descripcion
        tarea.fecha_limite = fecha_limite
        tarea.prioridad = prioridad
        tarea.estado = estado
        tarea.observaciones = observaciones
        tarea.save()
        Equipos_Desarrollo.objects.filter(tarea_id=tarea).delete()
        for desarrollador_correo in desarrolladores_seleccionados:
            desarrollador = Usuarios.objects.get(correo=desarrollador_correo)
            Equipos_Desarrollo.objects.create(
                nombre_equipo_id=equipo,
                desarrollador_id=desarrollador,
                tarea_id=tarea
            )
        messages.success(request, "Tarea actualizada exitosamente")
        return redirect('ver_info_equipo', id=equipo.nombre_equipo)
    context = {
        'equipo': equipo,
        'desarrolladores': desarrolladores,
        'tarea': tarea,
        'desarrolladores_tarea': desarrolladores_tarea,
    }
    return render(request, "tasks/crear_task.html", context)

def eliminar_task(request, id):
    tarea = get_object_or_404(Tareas, id=id)
    equipo_nombre = tarea.equipos_desarrollo_set.first().nombre_equipo_id.nombre_equipo if tarea.equipos_desarrollo_set.exists() else None
    Equipos_Desarrollo.objects.filter(tarea_id=tarea).delete()
    Observaciones_Tareas.objects.filter(tarea_id=tarea).delete()
    tarea.delete()
    if equipo_nombre:
        messages.success(request, "Tarea eliminada exitosamente")
        return redirect('ver_info_equipo', id=equipo_nombre)
    else:
        messages.error(request, "No se encontró el equipo asociado a la tarea")
        return redirect('ver_info_equipo', id=equipo.nombre_equipo)

def ver_info_tarea(request, id):
    tarea = get_object_or_404(Tareas, id=id)
    desarrollador = Equipos_Desarrollo.objects.filter(tarea_id=tarea).first()
    observaciones = Observaciones_Tareas.objects.filter(tarea_id=tarea)
    context = {
        'tarea': tarea,
        'desarrollador': desarrollador.desarrollador_id if desarrollador else None,
        'observaciones': observaciones
    }
    return render(request, "tasks/ver_task.html", context)
