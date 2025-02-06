// Enable Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete actions
    var deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm || '¿Está seguro de que desea eliminar este elemento?')) {
                e.preventDefault();
            }
        });
    });

    // Format currency inputs
    var currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            var value = this.value.replace(/[^\d.]/g, '');
            value = value.replace(/\./, 'x').replace(/\./g, '').replace(/x/, '.');
            this.value = value;
        });
    });

    // Format date inputs to local format
    var dateElements = document.querySelectorAll('.date-local');
    dateElements.forEach(function(element) {
        var date = new Date(element.textContent);
        element.textContent = date.toLocaleDateString();
    });

    // Handle dynamic form fields
    var addFieldButtons = document.querySelectorAll('.add-field');
    addFieldButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var template = document.querySelector(this.dataset.template);
            var container = document.querySelector(this.dataset.container);
            var clone = template.content.cloneNode(true);
            container.appendChild(clone);
        });
    });

    // Handle file inputs
    var fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            var fileName = this.files[0].name;
            var label = this.nextElementSibling;
            label.textContent = fileName;
        });
    });

    // Handle responsive tables
    var tables = document.querySelectorAll('.table-responsive-stack');
    tables.forEach(function(table) {
        var thArray = [];
        var tdArray = [];

        table.querySelectorAll('th').forEach(function(th) {
            thArray.push(th.textContent);
        });

        table.querySelectorAll('td').forEach(function(td, index) {
            td.setAttribute('data-th', thArray[index % thArray.length]);
        });
    });
});
