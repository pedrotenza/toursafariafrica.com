/**
 * ========================================
 * Archivo: admin_custom.js
 * Ubicación: static/app/js/admin_custom.js
 * Descripción: Funcionalidades personalizadas para Django Admin
 * ========================================
 */

document.addEventListener("DOMContentLoaded", function() {
    initializeHorizontalScroll();
    setupEventListeners();
});

function initializeHorizontalScroll() {
    // Esperar a que la tabla esté completamente renderizada
    const waitForTable = setInterval(function() {
        const tableWrapper = document.querySelector(".change-list .results");
        const table = document.querySelector("#result_list");
        
        if (tableWrapper && table) {
            clearInterval(waitForTable);
            createCustomScroll(tableWrapper, table);
        }
    }, 100);
}

function createCustomScroll(tableWrapper, table) {
    // Crear contenedor del scroll superior
    const topScrollContainer = document.createElement("div");
    topScrollContainer.className = "custom-top-scroll";
    
    // Crear elemento interno para el scroll
    const topScrollContent = document.createElement("div");
    topScrollContent.className = "custom-top-scroll-inner";
    
    // Insertar antes de la tabla
    tableWrapper.parentNode.insertBefore(topScrollContainer, tableWrapper);
    topScrollContainer.appendChild(topScrollContent);
    
    // Función para actualizar dimensiones
    const updateScrollDimensions = () => {
        const tableWidth = table.scrollWidth;
        const wrapperWidth = tableWrapper.clientWidth;
        
        // Asegurarse de que el scroll solo aparece cuando es necesario
        if (tableWidth > wrapperWidth) {
            topScrollContent.style.width = `${tableWidth}px`;
            topScrollContainer.style.display = 'block';
        } else {
            topScrollContainer.style.display = 'none';
        }
    };
    
    // Configurar observador de mutaciones
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(() => {
            setTimeout(updateScrollDimensions, 50);
        });
    });
    
    observer.observe(table, {
        childList: true,
        subtree: true,
        attributes: true,
        characterData: true
    });
    
    // Configurar redimensionamiento de ventana
    window.addEventListener('resize', function() {
        setTimeout(updateScrollDimensions, 100);
    });
    
    // Sincronizar scrolls
    topScrollContainer.addEventListener('scroll', function() {
        tableWrapper.scrollLeft = this.scrollLeft;
    });
    
    tableWrapper.addEventListener('scroll', function() {
        topScrollContainer.scrollLeft = this.scrollLeft;
    });
    
    // Actualizar inicialmente
    updateScrollDimensions();
    
    // Forzar una segunda actualización después de 500ms para capturar cambios dinámicos
    setTimeout(updateScrollDimensions, 500);
}

function setupEventListeners() {
    // Event listeners adicionales pueden ir aquí
    document.addEventListener('click', function(e) {
        // Ejemplo: Manejar clicks en botones personalizados
        if (e.target.classList.contains('custom-filter-btn')) {
            // Lógica para mostrar/ocultar filtros
        }
    });
}

// Función auxiliar para debounce
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}