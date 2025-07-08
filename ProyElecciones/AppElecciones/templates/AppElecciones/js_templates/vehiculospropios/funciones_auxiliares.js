$(function () {
        jQuery.datetimepicker.setLocale('es');
        $('#id_desde').datetimepicker({
            timepicker: false,
            format: 'd/m/Y',
        });

        $('#id_hasta').datetimepicker({
            timepicker: false,
            format: 'd/m/Y',
        });

        $('#medio').select2({
            theme: "bootstrap4",
            language: 'es',
            placeholder: 'Seleccione',
            allowClear: true,

        });
        $('#fuerza').select2({
            theme: "bootstrap4",
            language: 'es',
            placeholder: 'Seleccione',
            allowClear: true,

        });
        $('#unidad').select2({
            theme: "bootstrap4",
            language: 'es',
            placeholder: 'Seleccione',
            allowClear: true,

        });
        $('#tipo_veh_pro').select2({
            theme: "bootstrap4",
            language: 'es',
            placeholder: 'Seleccione',
            allowClear: true,

        });
        $('#tareas').select2({
            theme: "bootstrap4",
            language: 'es',
            placeholder: 'Seleccione',
            allowClear: true,

        });
        $('#tipo_combustible').select2({
            theme: "bootstrap4",
            language: 'es',
            placeholder: 'Seleccione',
            allowClear: true,

        });

});