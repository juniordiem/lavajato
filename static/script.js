document.addEventListener('DOMContentLoaded', function() {
    // Ativar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Máscara para placa de veículo
    var placaInputs = document.querySelectorAll('input[name="placa"]');
    placaInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            if (this.value.length > 7) {
                this.value = this.value.substring(0, 7);
            }
        });
    });
    
    // Máscara para telefone
    var contatoInputs = document.querySelectorAll('input[name="contato"]');
    contatoInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '');
        });
    });
    
    // Mostrar/ocultar valor pago no modal de status
    var statusModals = document.querySelectorAll('.modal');
    statusModals.forEach(function(modal) {
        modal.addEventListener('show.bs.modal', function(event) {
            var statusSelect = modal.querySelector('select[name="status"]');
            var valorPagoContainer = modal.querySelector('[id^="valorPagoContainer"]');
            
            if (statusSelect && valorPagoContainer) {
                if (statusSelect.value === 'Finalizado') {
                    valorPagoContainer.style.display = 'block';
                } else {
                    valorPagoContainer.style.display = 'none';
                }
                
                statusSelect.addEventListener('change', function() {
                    if (this.value === 'Finalizado') {
                        valorPagoContainer.style.display = 'block';
                    } else {
                        valorPagoContainer.style.display = 'none';
                    }
                });
            }
        });
    });
});