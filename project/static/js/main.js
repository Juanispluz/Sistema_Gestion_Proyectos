// Obtener elementos del DOM
const correoInput = document.getElementById('correo');
const correoExistenteError = document.getElementById('correo-existente-error');

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

document.addEventListener("DOMContentLoaded", function () {
    const correoInput = document.getElementById("correo");
    const correoConfirmInput = document.getElementById("correo_confirm");
    const correoError = document.getElementById("correo-error");
    const correoExistenteError = document.getElementById("correo-existente-error");

    const passwordInput = document.getElementById("password");
    const passwordConfirmInput = document.getElementById("password_confirm");
    const passwordError = document.getElementById("password-error");

    // Validar correos coincidan
    correoConfirmInput.addEventListener("input", function () {
        if (correoInput.value !== correoConfirmInput.value) {
            correoError.textContent = "Los correos no coinciden.";
        } else {
            correoError.textContent = "";
        }
    });

    // Validar correo existente
    correoInput.addEventListener("input", function () {
        fetch(`/existencia_correo?correo=${correoInput.value}`)
            .then(response => response.json())
            .then(data => {
                if (!data.disponible) {  // Cambiar 'data.existe' por 'data.disponible'
                    correoExistenteError.textContent = "El correo ya está en uso.";
                } else {
                    correoExistenteError.textContent = "Check"; // Mensaje para correo disponible
                    correoExistenteError.style.color = "green"; // Cambia a verde si está disponible
                }
            });
    });

    // Validar contraseñas coincidan
    passwordConfirmInput.addEventListener("input", function () {
        if (passwordInput.value !== passwordConfirmInput.value) {
            passwordError.textContent = "Las contraseñas no coinciden.";
        } else {
            passwordError.textContent = "";
        }
    });
});

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
    // Solo verificar si no estamos en modo edición
    const esEdicion = document.getElementById("nombre_equipo").hasAttribute('readonly');
    
    if (!esEdicion && nombreEquipo.length > 0) {
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

// Editar equipo


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