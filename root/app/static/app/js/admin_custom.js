document.addEventListener('DOMContentLoaded', function() {
    // Espera a que exista el elemento de filtros
    const waitForFilters = setInterval(function() {
        const filterSection = document.getElementById('changelist-filter');
        const contentMain = document.getElementById('content-main');
        
        if (filterSection && contentMain) {
            clearInterval(waitForFilters);
            
            // 1. Crear botón de toggle
            const toggleBtn = document.createElement('button');
            toggleBtn.innerHTML = '❌ Ocultar Filtros';
            toggleBtn.style.cssText = `
                background: #417690;
                color: white;
                padding: 8px 15px;
                margin: 0 15px 15px 0;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
            `;
            
            // 2. Insertar botón en un lugar visible
            const search = document.getElementById('changelist-search');
            if (search) {
                search.after(toggleBtn);
            } else {
                document.querySelector('.actions').before(toggleBtn);
            }
            
            // 3. Función para ocultar/mostrar
            function toggleFilters() {
                if (filterSection.style.display === 'none') {
                    // Mostrar filtros
                    filterSection.style.display = 'block';
                    contentMain.style.marginRight = '250px';
                    toggleBtn.innerHTML = '❌ Ocultar Filtros';
                } else {
                    // Ocultar completamente
                    filterSection.style.display = 'none';
                    contentMain.style.marginRight = '0';
                    toggleBtn.innerHTML = '👁️ Mostrar Filtros';
                }
            }
            
            // 4. Evento click
            toggleBtn.addEventListener('click', toggleFilters);
            
            // 5. Inicialmente visibles
            filterSection.style.display = 'block';
            contentMain.style.marginRight = '250px';
            contentMain.style.transition = 'margin-right 0.3s ease';
        }
    }, 100);
});