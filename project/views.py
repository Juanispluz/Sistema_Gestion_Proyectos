from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.db.models import Count, Q
from django.db import transaction

# Create your views here.

def index(request):
    # Evitar acceso si no esta logueado
    if not request.session.get("logueado"):
        messages.error(request, "Debes iniciar sesión para acceder a esta página.")
        return redirect("login")

    rol = request.session.get('rol')
    equipos = []

    # Obtener equipos 
    if rol == 'L':
        equipos = Equipos.objects.filter(usuario_lider_id__correo=request.session.get('correo'))
    
    # Obtener equipos de desarrollo
    elif rol == 'D':
        equipos = Equipos_Desarrollo.objects.filter(desarrollador_id__correo=request.session.get('correo'))
    
    return render(request, "index.html", {'equipos': equipos})

def recoleccion_info(request, id):
    equipo = get_object_or_404(Equipos, nombre_equipo=id)
    miembros_tareas = Equipos_Desarrollo.objects.filter(nombre_equipo_id=equipo)
    
    miembros_unicos = set()
    tareas = []
    
    for miembro in miembros_tareas:
        desarrollador = miembro.desarrollador_id
        miembros_unicos.add(desarrollador)  # Añade desarrolladores únicos al conjunto
        tarea = miembro.tarea_id
        tareas.append({
            'tarea': tarea,
            'desarrollador': desarrollador
        })
    
    context = {
        'equipo': equipo,
        'miembros': list(miembros_unicos),  # Convertimos el conjunto a una lista para la plantilla
        'tareas': tareas,
    }
    return render(request, 'equipos/equipo.html', context)

# -----------------------------------------------------------------------
# Manejo de sesión
def login(request):
    # Evitar acceso si ya esta logueado
    if request.session.get("logueado"):
        messages.error(request, "Ya estás logueado.")
        return redirect("index")
    
    if request.method == "POST":
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        try:
            usuario = Usuarios.objects.get(correo=correo)
            if check_password(password, usuario.password):
                # Variables de sesión
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

def register(request): # Añadir el mensaje de desea añadir otro usuario con js, añadir permiso de logueado y solo el rol A
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        correo_confirm = request.POST.get('correo_confirm')
        rol = request.POST.get('rol')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Verificar usuarios repetidos
        if Usuarios.objects.filter(correo=correo).exists():
            messages.error(request, "Error. Este usuario ya se encuentra registrado")
            return render(request, "login/register.html")

        # No registrar rol A
        if rol == 'A':
            messages.error(request, "No está permitido registrar usuarios con el rol 'A'.")
            return render(request, "login/register.html")
        
        # Validar selección del rol
        if rol not in ['L', 'D']:
            messages.warning(request, "Debe seleccionar un rol.")
            return render(request, "login/register.html")

        # Comparar Correos
        if correo != correo_confirm:
            messages.warning(request, 'Los "CORREOS" deben de coincidir.')
            return render(request, "login/register.html")

        # Comparar Passwords
        if password != password_confirm:
            messages.warning(request, 'Las "CONTRASEÑAS", deben de coincidir.')
            return render(request, "login/register.html")

        # Hasheo de la Contraseña
        password_hashed = make_password(password)

        # Guardar al usuario
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
# Equipos
def crear_equipo(request):
    if request.method == 'POST':
        nombre_equipo = request.POST.get('nombre_equipo')
        desarrolladores_seleccionados = request.POST.getlist('desarrolladores')

        # Validar nombre del equipo
        if Equipos.objects.filter(nombre_equipo=nombre_equipo).exists():
            messages.error(request, "Error: el nombre del equipo ya está registrado.")
            return redirect("crear_equipo")

        # Obtener el usuario líder desde la sesión
        if not request.session.get('logueado'):
            messages.error(request, "Debes estar logueado para crear un equipo.")
            return redirect("login")

        # Obtener los detalles del usuario logueado
        correo_lider = request.session.get('correo')
        try:
            lider = Usuarios.objects.get(correo=correo_lider, rol='L')
            
            # Registrar el equipo
            equipo = Equipos.objects.create(nombre_equipo=nombre_equipo, usuario_lider_id=lider)

            # Registrar los desarrolladores en el equipo
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

def verificar_nombre_equipo(request):
    nombre_equipo = request.GET.get('nombre_equipo')
    disponible = not Equipos.objects.filter(nombre_equipo=nombre_equipo).exists()
    return JsonResponse({"disponible": disponible})

def editar_equipo(request, id):
    # Obtener el equipo o devolver un error 404 si no existe
    equipo = get_object_or_404(Equipos, nombre_equipo=id)

    if request.method == 'POST':
        # Actualizar datos del equipo
        nuevo_nombre = request.POST.get('nombre_equipo')
        nuevo_lider_id = request.POST.get('usuario_lider')
        miembros = request.POST.getlist('desarrolladores')

        # Validar si el nuevo nombre ya existe
        if nuevo_nombre and Equipos.objects.filter(nombre_equipo=nuevo_nombre).exclude(nombre_equipo=id).exists():
            messages.error(request, "Error: el nombre del equipo ya está en uso.")
            return redirect('editar_equipo', id=id)

        # Actualizar nombre y líder del equipo
        equipo.nombre_equipo = nuevo_nombre or equipo.nombre_equipo
        equipo.usuario_lider_id = Usuarios.objects.get(correo=nuevo_lider_id)
        equipo.save()

        # Eliminar desarrolladores existentes y sus tareas asociadas
        equipo_desarrollo = Equipos_Desarrollo.objects.filter(nombre_equipo_id=equipo)
        for registro in equipo_desarrollo:
            if registro.tarea_id:  # Eliminar tareas si existen
                registro.tarea_id.delete()
            registro.delete()

        # Agregar nuevos desarrolladores
        for miembro_correo in miembros:
            desarrollador = Usuarios.objects.get(correo=miembro_correo, rol='D')
            Equipos_Desarrollo.objects.create(nombre_equipo_id=equipo, desarrollador_id=desarrollador)

        messages.success(request, "Equipo actualizado correctamente.")
        return redirect('listar_equipos')

    # Preparar datos para renderizar el formulario
    lideres = Usuarios.objects.filter(rol='L')
    desarrolladores = Usuarios.objects.filter(rol='D')
    miembros_actuales = Equipos_Desarrollo.objects.filter(nombre_equipo_id=equipo)

    return render(request, "equipos/crear_equipo.html", {
        'equipo': equipo,
        'lideres': lideres,
        'desarrolladores': desarrolladores,
        'miembros_actuales': miembros_actuales,
        'editar': True,  # Bandera para distinguir entre crear y editar
    })

def eliminar_equipo(request, id):
    pass

# -----------------------------------------------------------------------
# Tareas
def crear_task(request, id):
    equipo = get_object_or_404(Equipos, nombre_equipo=id)
    
    # Filtrar desarrolladores con rol "D" y que estén en menos de 10 equipos o no estén en ninguno
    desarrolladores = Usuarios.objects.filter(
        rol='D'
    ).annotate(
        equipo_count=Count('equipos_desarrollo')  # Contar cuántos equipos tiene el desarrollador
    ).filter(
        Q(equipo_count__lt=10) | Q(equipo_count__isnull=True)  # Menos de 10 equipos o ninguno
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

        # Crear la tarea
        tarea = Tareas.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            fecha_limite=fecha_limite,
            prioridad=prioridad,
            estado=estado,
            observaciones=observaciones,
        )

        # Registrar los desarrolladores en Equipos_Desarrollo, con su relación con la tarea
        for desarrollador_correo in desarrolladores_seleccionados:
            desarrollador = Usuarios.objects.get(correo=desarrollador_correo)
            
            # Crear el objeto Equipos_Desarrollo, vincular tarea y equipo
            Equipos_Desarrollo.objects.create(
                nombre_equipo_id=equipo,
                desarrollador_id=desarrollador,
                tarea_id=tarea  # Relacionamos la tarea con el desarrollador y el equipo
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
    equipo = tarea.equipos_desarrollo_set.first().nombre_equipo_id  # Suponiendo que la tarea está asociada a un equipo
    
    # Obtener los desarrolladores actuales de la tarea
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
        
        # Actualizar la tarea
        tarea.titulo = titulo
        tarea.descripcion = descripcion
        tarea.fecha_limite = fecha_limite
        tarea.prioridad = prioridad
        tarea.estado = estado
        tarea.observaciones = observaciones
        tarea.save()
        
        # Eliminar asociaciones previas con desarrolladores (ahora se elimina en Equipos_Desarrollo)
        Equipos_Desarrollo.objects.filter(tarea_id=tarea).delete()
        
        # Crear nuevas asociaciones en Equipos_Desarrollo
        for desarrollador_correo in desarrolladores_seleccionados:
            desarrollador = Usuarios.objects.get(correo=desarrollador_correo)
            
            # Crear la relación entre el equipo, desarrollador y tarea en Equipos_Desarrollo
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
        'desarrolladores_tarea': desarrolladores_tarea,  # Añadido para marcar desarrolladores actuales
    }
    return render(request, "tasks/crear_task.html", context)

def eliminar_task(request, id):
    tarea = get_object_or_404(Tareas, id=id)
    
    # Obtener el nombre del equipo al que pertenece la tarea antes de eliminarla
    equipo_nombre = tarea.equipos_desarrollo_set.first().nombre_equipo_id.nombre_equipo if tarea.equipos_desarrollo_set.exists() else None
    
    # Eliminar la tarea de la tabla Equipos_Desarrollo (eliminamos las relaciones)
    Equipos_Desarrollo.objects.filter(tarea_id=tarea).delete()

    # Eliminar la tarea de la tabla Observaciones_Tareas
    Observaciones_Tareas.objects.filter(tarea_id=tarea).delete()

    # Eliminar la tarea de la tabla Tareas
    tarea.delete()
    
    # Verificar que el equipo todavía existe y redirigir
    if equipo_nombre:
        messages.success(request, "Tarea eliminada exitosamente")
        return redirect('ver_info_equipo', id=equipo_nombre)
    else:
        messages.error(request, "No se encontró el equipo asociado a la tarea")
        return redirect('ver_info_equipo', id=equipo.nombre_equipo)

def perfil(request):
    pass