$(function () {
    $('#fecha_nov').datetimepicker({
      format:'d/m/Y H:i',
    });
    $('#tipo_nov_grl').select2({
            theme: "bootstrap4",
            language: 'es',
            placeholder: 'Seleccione',
            allowClear: true,
        });
        $('#subsanada').select2({
            theme: "bootstrap4",
            language: 'es',
            placeholder: 'Seleccione',
            allowClear: true,
        });
});
