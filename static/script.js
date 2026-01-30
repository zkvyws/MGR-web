document.addEventListener('DOMContentLoaded', () => {
    // Aquí puedes añadir efectos dinámicos o interacciones si lo deseas.
    // Por ejemplo, un efecto de "glitch" sutil o animaciones al cargar.

    // Ejemplo básico: Parpadear los bordes holográficos ligeramente
    const borderElements = document.querySelectorAll('.display-border');
    
    borderElements.forEach(border => {
        setInterval(() => {
            border.style.opacity = Math.random() > 0.8 ? 0.7 : 1; // Parpadeo aleatorio
        }, 300); // Cada 300ms
    });

    console.log("Moon Galactic Regimen UI loaded.");
});