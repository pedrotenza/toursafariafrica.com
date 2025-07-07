document.addEventListener('DOMContentLoaded', function() {
    // Eliminar el botón nativo de Django de forma más agresiva
    const removeNativeButton = function() {
        // Todos los selectores posibles donde puede aparecer el botón nativo
        const selectors = [
            '#toolbar form#changelist-search + a',
            '#toolbar form#changelist-search ~ a',
            '#changelist-search + a',
            '#changelist-search ~ a'
        ];
        
        selectors.forEach(selector => {
            const buttons = document.querySelectorAll(selector);
            buttons.forEach(btn => {
                if (btn.textContent.match(/show filters|mostrar filtros/i)) {
                    btn.style.display = 'none';
                    btn.remove();
                }
            });
        });
    };

    // Crear nuestro botón personalizado
    const setupCustomButton = function() {
        const filterSection = document.getElementById('changelist-filter');
        if (!filterSection) return;

        // Eliminar cualquier versión previa de nuestro botón
        const oldButtons = document.querySelectorAll('.custom-filter-btn');
        oldButtons.forEach(btn => btn.remove());

        // Crear nuevo botón
        const btn = document.createElement('button');
        btn.className = 'custom-filter-btn';
        btn.textContent = 'Toggle Filters';
        btn.style.cssText = `
            background: #417690;
            color: white;
            padding: 8px 15px;
            margin: 0 15px 15px 0;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        `;

        // Insertar en la ubicación correcta
        const search = document.getElementById('changelist-search') || 
                      document.querySelector('.actions');
        if (search) {
            search.parentNode.insertBefore(btn, search.nextSibling);
        }

        // Funcionalidad del botón
        btn.addEventListener('click', function() {
            filterSection.classList.toggle('visible');
            btn.textContent = filterSection.classList.contains('visible') 
                ? 'Hide Filters' 
                : 'Show Filters';
        });

        // Estado inicial
        filterSection.classList.remove('visible');
    };

    // Ejecutar con retraso y verificación continua
    let attempts = 0;
    const maxAttempts = 10;
    
    const init = setInterval(() => {
        removeNativeButton();
        setupCustomButton();
        
        attempts++;
        if (attempts >= maxAttempts || 
            (!document.querySelector('a[href="#"]') && 
             document.querySelector('.custom-filter-btn'))) {
            clearInterval(init);
        }
    }, 200);
});