document.addEventListener('DOMContentLoaded', function() {
    // Función para alternar los filtros
    function toggleFilters() {
        const filterSection = document.getElementById('changelist-filter');
        const mainContent = document.querySelector('#changelist');
        
        if (filterSection) {
            // Alternar visibilidad
            filterSection.style.display = filterSection.style.display === 'none' ? 'block' : 'none';
            
            // Ajustar el ancho del contenido principal
            if (mainContent) {
                mainContent.style.width = filterSection.style.display === 'none' ? '100%' : 'calc(100% - 300px)';
            }
        }
    }

    // Crear botón
    const toggleButton = document.createElement('button');
    toggleButton.textContent = 'Mostrar/Ocultar Filtros';
    toggleButton.className = 'toggle-filters-btn';
    
    // Posicionar el botón
    const actions = document.querySelector('.actions');
    if (actions) {
        actions.before(toggleButton);
    } else {
        const search = document.querySelector('#changelist-search');
        if (search) search.after(toggleButton);
    }

    // Evento click
    toggleButton.addEventListener('click', toggleFilters);
    
    // Ocultar filtros al cargar (opcional)
    toggleFilters();
});