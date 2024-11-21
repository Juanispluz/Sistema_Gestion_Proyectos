// ----------------------------------------------------------------------- 
// Alertas de Django/Bootstrap 
// document.querySelectorAll('.close').forEach(function (button) {
//     button.addEventListener('click', function () {
//         const alertBox = button.closest('.alert');
        
//         // Añadimos la animación de desaparición
//         alertBox.style.animation = 'desaparecer 1s forwards';  // Activamos la animación de desaparición

//         // Esperamos a que la animación termine antes de eliminar el elemento
//         setTimeout(function () {
//             alertBox.remove();  // Elimina la alerta después de que la animación haya terminado
//         }, 1000);  // 1000 ms es el tiempo de duración de la animación de desaparición
//     });
// });

// Buscar desarrolladores 
function filtrarDesarrolladores() {
    const buscador = document.querySelector("#buscador-desarrolladores"); // Buscar cualquiera de los dos
    const filtro = buscador.value.toLowerCase();
    const listaDesarrolladores = document.querySelectorAll("#desarrolladores-lista div, #desarrolladores-lista ul li");
    
    listaDesarrolladores.forEach(function(item) {
        const nombre = item.textContent.toLowerCase();
        if (nombre.includes(filtro)) {
            item.style.display = "";
        } else {
            item.style.display = "none";
        }
    });
}

// -----------------------------------------------------------------------
// index
document.querySelectorAll('li').forEach(item => {
    item.addEventListener('mouseenter', function() {
        const teamName = item.querySelector('.team-name');
        const link = item.querySelector('a');
        teamName.classList.remove('d-none');
        teamName.style.borderColor = 'black'; // Bordes alrededor del nombre
        link.style.borderColor = 'black'; // Bordes alrededor del cuadro
    });
    item.addEventListener('mouseleave', function() {
        const teamName = item.querySelector('.team-name');
        const link = item.querySelector('a');
        teamName.classList.add('d-none');
        teamName.style.borderColor = 'transparent'; // Elimina el borde alrededor del nombre
        link.style.borderColor = 'transparent'; // Elimina el borde alrededor del cuadro
    });
});

// -----------------------------------------------------------------------
// Register

// Ventana emergente


// Botones de rol
document.addEventListener('DOMContentLoaded', function() {
    const roleButtons = document.querySelectorAll('.role-btn');
    const rolInput = document.getElementById('rol-input');

    roleButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remover la clase active de todos los botones
            roleButtons.forEach(btn => btn.classList.remove('active'));
            
            // Agregar la clase active al botón seleccionado
            this.classList.add('active');
            
            // Actualizar el valor del input oculto
            rolInput.value = this.dataset.role;
        });
    });
});

// -----------------------------------------------------------------------
// Equipos

// Registrar equipo
function verificarNombreEquipo() {
    const nombreEquipo = document.getElementById("nombre_equipo").value;
    if (nombreEquipo.length > 0) {
        fetch(`/verificar_nombre_equipo/?nombre_equipo=${nombreEquipo}`)
            .then(response => response.json())
            .then(data => {
                const mensaje = document.getElementById("nombre-disponible");
                if (data.disponible) {
                    mensaje.textContent = "Nombre disponible.";
                    mensaje.style.color = "green";
                } else {
                    mensaje.textContent = "Este equipo ya se registrado.";
                    mensaje.style.color = "red";
                }
            });
    }
}

// -----------------------------------------------------------------------
// Tareas

// Tareas > 5 no se puede
function verificarNumeroDesarrolladores(checkbox) {
    const desarrolladoresSeleccionados = document.querySelectorAll('#desarrolladores-lista input[type="checkbox"]:checked');
    
    if (desarrolladoresSeleccionados.length > 5) {
        alert('Solo puedes seleccionar máximo 5 desarrolladores');
        checkbox.checked = false;
    }
}