document.addEventListener('DOMContentLoaded', function () {
    // Obtener los inputs
    const providerPriceInput = document.getElementById('id_provider_price');
    const commissionInput = document.getElementById('id_commission');
    const clientPriceInput = document.getElementById('id_client_price');

    function calculateClientPrice() {
        let providerPrice = parseFloat(providerPriceInput.value) || 0;
        let commission = parseFloat(commissionInput.value) || 0;

        let clientPrice = providerPrice * commission;

        // Limitar decimales a 2 y actualizar el campo readonly
        clientPriceInput.value = clientPrice.toFixed(2);
    }

    if (providerPriceInput && commissionInput && clientPriceInput) {
        // Calcular al cargar la página por si ya tienen valores
        calculateClientPrice();

        // Calcular cada vez que cambien provider_price o commission
        providerPriceInput.addEventListener('input', calculateClientPrice);
        commissionInput.addEventListener('input', calculateClientPrice);
    }
});
