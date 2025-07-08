var csrftoken = Cookies.get('csrftoken');
$(function () {
    $.ajaxSetup({
                statusCode: {403:function(xhr,errmsg,err){
                    window.location = xhr.responseJSON.redirect_to;
                }},
             });
    function comprobarSesion(){
                $.ajax({
                    url: window.location.pathname,
                    type: "get",
                    dataType: "json",
                });
            };
    let id_led = parseInt('{{ object.id }}')
    var tabla_seg_led_ffaa = $('#tabla-seg-led-ffaa').DataTable({
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 10], [5, 10]],
        order: [[0, "asc"]],
        ajax: {
            url: "{% url 'listado-seg-led-ffaa' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'id_led': id_led
            },
        },
        columns: [
            { data: 'fecha_inicio',  orderable: false },
            { data: 'fecha_fin',   orderable: false },
            { data: 'fuerza_armada__fuerza',  orderable: false },
            { data: 'cant_personal',  orderable: false },
            {
                data: null,
                orderable: false,
                render:  function(data, type, row){
                    let boton = '';
                    if(row.eliminar){
                        boton +='<span id="elimiar-seg-led-ffaa" id_led_ffaa="'+row.id+'"  title="Eliminar" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
                    }
                    return boton
                }
            }
        ],
        columnDefs: [{
            targets: [0, 1], render: function (data1) {
                moment.locale('es');
                //return moment(data).format('MMMM Do YYYY');moment("20111031", "YYYYMMDD").fromNow();
                return moment(data1).format('L LT');
            },
        }],
        language: {
            decimal: "",
            emptyTable: "Sin registros de seguridad",
            info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
            infoFiltered: "(Filtrado de _MAX_ LED en total)",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ registros",
            loadingRecords: "Cargando...",
            processing: "Procesando...",
            search: "Buscar:",
            zeroRecords: "Sin registros de seguridad",
            paginate: {
                first: "Primero",
                last: "Ultimo",
                next: "Siguiente",
                previous: "Anterior"
            },
        },
        initComplete: function (settings, json) {
        }
    });
    function RecargarTabla() {
        comprobarSesion()
        tabla_seg_led_ffaa.ajax.reload(null, true);
    };
    var MostrarFormularioSegLedFFAA = function () {
        comprobarSesion()
        var boton = $(this);
        $.ajax({
            url: boton.attr("data-url"),
            type: "get",
            dataType: "json",
            data: { 'id_led': id_led },
            success: function (data) {
                //Respetar este orden para que funcione select2
                $('#modal-led-seg-ffaa').modal('show')
                $('#modal-led-seg-ffaa .modal-content').html(data.html_form);
                jQuery.datetimepicker.setLocale('es');
                setTimeout(function () {
                    $('#fecha_inicio').datetimepicker({
                        //maxDate: tomorrow,
                        timepicker: true,
                        format: 'd/m/Y H:i',
                    });
                    $('#fecha_fin').datetimepicker({
                        //maxDate: tomorrow,
                        timepicker: true,
                        format: 'd/m/Y H:i',
                    });
                }, 300)
                $('#fuerza_armada').select2({
                    //dropdownParent: $('#modal-seg-interna'),
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    language: {
                        inputTooShort: function (args) {
                            // args.minimum is the minimum required length
                            // args.input is the user-typed text
                            var t = args.minimum - args.input.length
                            return 'Ingrese ' + t + ' caracteres del apellido o dni';
                        },
                        noResults: function () {
                            return "No se encontraron resultados";
                        },
                        searching: function () {
                            return "Buscando..";
                        }
                    },
                });
            }
        });
    };
    var GuardarFormularioLedFFAA = function () {
        comprobarSesion()
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('data-url'),
            data: form.serialize() + "&id_led=" + id_led,
            dataType: "json",
            headers: { 'X-CSRFToken': csrftoken },
            success: function (data) {
                if (data.form_es_valido) {
                    //$('#boton-agregar').hide()
                    $('#modal-led-seg-ffaa').modal('hide');
                    RecargarTabla();
                }
                else {
                    //$('#modal-seg-interna .modal-content').html(data.html_form)
                    $('#modal-led-seg-ffaa .modal-content').html(data.html_form);
                    setTimeout(function () {
                        $('#fecha_inicio').datetimepicker({
                            //maxDate: tomorrow,
                            timepicker: true,
                            format: 'd/m/Y H:i',
                        });
                        $('#fecha_fin').datetimepicker({
                            //maxDate: tomorrow,
                            timepicker: true,
                            format: 'd/m/Y H:i',
                        });
                    }, 300)
                    $('#fuerza_armada').select2({
                        //dropdownParent: $('#modal-seg-interna'),
                        theme: "bootstrap4",
                        placeholder: 'Seleccione',
                        language: {
                            inputTooShort: function (args) {
                                // args.minimum is the minimum required length
                                // args.input is the user-typed text
                                var t = args.minimum - args.input.length
                                return 'Ingrese ' + t + ' caracteres del apellido o dni';
                            },
                            noResults: function () {
                                return "No se encontraron resultados";
                            },
                            searching: function () {
                                return "Buscando..";
                            }
                        },
                    });
                }
            }
        })
        return false;
    };
    $('#mostrar-modal-seg-led-ffaa').click(MostrarFormularioSegLedFFAA)
    $("#modal-led-seg-ffaa").on("submit", ".agregar-seg-led-ffaa", GuardarFormularioLedFFAA)
    $("#modal-led-seg-ffaa").on("submit", ".actualizar-seg-led-ffaa", GuardarFormularioLedFFAA);
    $('#tabla-seg-led-ffaa tbody').on('click', '#editar-seg-led-ffaa', function () {
        comprobarSesion()
        var data = tabla_seg_led_ffaa.row($(this).parents('tr')).data();
        var id = data.id;
        $.ajax({
            url: "{% url 'actualizar-seg-led-ffaa' 77 %}".replace('77', id),
            type: "get",
            headers: { 'X-CSRFToken': csrftoken },
            dataType: "json",
            success: function (data) {
                $('#modal-led-seg-ffaa').modal('show')
                $('#modal-led-seg-ffaa .modal-content').html(data.html_form);
                jQuery.datetimepicker.setLocale('es');
                setTimeout(function () {
                    $('#fecha_inicio').datetimepicker({
                        //maxDate: tomorrow,
                        timepicker: true,
                        format: 'd/m/Y H:i',
                    });
                    $('#fecha_fin').datetimepicker({
                        //maxDate: tomorrow,
                        timepicker: true,
                        format: 'd/m/Y H:i',
                    });
                }, 300)
                $('#fuerza_armada').select2({
                    //dropdownParent: $('#modal-seg-interna'),
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    language: {
                        inputTooShort: function (args) {
                            // args.minimum is the minimum required length
                            // args.input is the user-typed text
                            var t = args.minimum - args.input.length
                            return 'Ingrese ' + t + ' caracteres del apellido o dni';
                        },
                        noResults: function () {
                            return "No se encontraron resultados";
                        },
                        searching: function () {

                            return "Buscando..";
                        }
                    },
                });
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert('Error modificando datos de seguridad en el LED con FFAA');
            }
        });
    });
    $('#tabla-seg-led-ffaa tbody').on('click', '#elimiar-seg-led-ffaa', function () {
        comprobarSesion()
        var id = $(this).attr('id_led_ffaa');
        Swal.fire({
            //title: 'Borrar este registro ?',
            text: "Borrar este registro ?",
//            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '',
            confirmButtonText: 'Sí, borrarlo'
        }).then((result) => {
            if (result.value) {
                $.ajax({
                    url: "{% url 'eliminar-seg-led-ffaa' 88 %}".replace('88', id),
                    type: "get",
                    headers: { 'X-CSRFToken': csrftoken },
                    dataType: "json",
                    success: function (data) {
                        if (data.permitido) {
                            RecargarTabla();
                            //$('#boton-agregar').show()
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        alert('Error borrando datos de seguridad en el LED con FFAA');
                    }
                });
            }
        })
    });
});
