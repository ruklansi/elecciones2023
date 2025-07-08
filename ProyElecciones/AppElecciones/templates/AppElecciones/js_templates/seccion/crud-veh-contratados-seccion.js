var csrftoken = Cookies.get('csrftoken');
$(function () {
    $("#pills-vcontratados-tab").click(function () {
        RecargarTabla();
    });
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
    let id_seccion = parseInt('{{ object.id }}')
    var tabla_vhcontratados_seccion = $('#tabla-vehiculos-contratados-seccion').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 10], [5, 10]],
        order: [[0, "asc"]],
        paging: true,
        bFilter: true,
        ajax: {
            url: "{% url 'listar-vhcontratados-en-seccion' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: { 'id_seccion': id_seccion },
        },
        columns: [
            { data: 'vehiculo_contratado__tipo_vehiculo_contratado__tipo_vehiculo_civil', orderable: false },
            { data: 'vehiculo_contratado__patente_matricula', orderable: false },
            { data: 'zona_trabajo', orderable: false },
//            { data: 'cond_veh_cont', orderable: false },
            {
                data: null,
                orderable: false,
                render:  function(data, type, row){
                    let boton = '';
                    if (row.editar){
                        boton += '<span id="editar-vhcontratado-seccion" id_edit_vc_sec="'+row.id+'"  title="Editar" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp'
                    }
                    if (row.eliminar){
                        boton += '<span id="elimiar-vhcontratado-seccion" id_del_vc_sec="'+row.id+'" title="Eliminar" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
                    }
                    return boton
                }
            }
        ],
        language: {
            decimal: "",
            emptyTable: "Sin resultados encontrados",
            info: "Mostrando _START_ a _END_ de _TOTAL_ Registros",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
            infoFiltered: "(Filtrado de _MAX_ registros en total)",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ Registros",
            loadingRecords: "Cargando...",
            processing: "Procesando...",
            search: "Buscar:",
            zeroRecords: "Sin resultados encontrados",
            paginate: {
                first: "Primero",
                last: "Ultimo",
                next: "Siguiente",
                previous: "Anterior"
            }
        },
        initComplete: function (settings, json) { }
    });
    function RecargarTabla() {
        comprobarSesion()
        tabla_vhcontratados_seccion.ajax.reload(null, true);
    };
    var MostrarFormularioVhContratadosSeccion = function () {
        comprobarSesion()
        var boton = $(this);
        $.ajax({
            url: boton.attr("data-url"),
            type: "get",
            dataType: "json",
            success: function (data) {
                $('#modal-vcontratados-seccion .modal-content').html(data.html_form);
                $('#modal-vcontratados-seccion').modal('show')

                $('#tareas_veh_civil_sec').select2({
                    theme: "bootstrap4",
                    allowClear: true,
                    placeholder: 'Seleccione',
                });
//                $('#responsable_veh_contratado_sec').select2({
//                    theme: "bootstrap4",
//                    placeholder: 'Seleccione',
//                    allowClear: true,
//                    language: {
//                        inputTooShort: function (args) {
//                            // args.minimum is the minimum required length
//                            // args.input is the user-typed text
//                            var t = args.minimum - args.input.length
//                            return 'Ingrese ' + t + ' caracteres del DNI o apellido';
//                        },
//                        noResults: function () {
//                            return "No se encontraron resultados";
//                        },
//                        searching: function () {
//
//                            return "Buscando..";
//                        }
//                    },
//                   ajax: {
//                        url: "{% url 'obtener-personas' %}",
//                        dataType: 'json',
//                        processResults: function (data) {
//                            return {
//                                results: $.map(data, function (item) {
//                                    return {
//                                        id: item.id, text: item.grado__grado+ ' ' + item.nombre
//                                            + ' ' + item.apellido + ' ' + item.dni
//                                    };
//                                })
//                            };
//                        },
//                    },
//                    minimumInputLength: 3
//                });
                jQuery.datetimepicker.setLocale('es');
                setTimeout(function () {
                    $('#veh_cont_seccion').select2({
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    allowClear: true,
                    language: {
                        inputTooShort: function (args) {
                            // args.minimum is the minimum required length
                            // args.input is the user-typed text
                            var t = args.minimum - args.input.length
                            return 'Ingrese ' + t + ' caracteres del vehículo o NI';
                        },
                        noResults: function () {
                            return "No se encontraron resultados";
                        },
                        searching: function () {

                            return "Buscando..";
                        }
                    },
                    ajax: {
                        url: "{% url 'obtener-veh-contratados' %}",
                        dataType: 'json',
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: ' Patente: ' + item.patente_matricula + ' Tipo: ' + item.tipo_vehiculo_contratado__tipo_vehiculo_civil
                                    };
                                })
                            };
                        },
                    },
                    minimumInputLength: 3
                });
                    $('#id_desde_veh_civil_sec').datetimepicker({
                        //maxDate: tomorrow,
                        timepicker: false,
                        format: 'd/m/Y',
                    });
                    $('#id_hasta_veh_civil_sec').datetimepicker({
                        //maxDate: tomorrow,
                        timepicker: false,
                        format: 'd/m/Y',
                    });
                }, 300);
            }
        });
    };
    var GuardarFormularioVhContratadosSeccion = function () {
        comprobarSesion()
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('data-url'),
            data: form.serialize() + "&id_seccion=" + id_seccion,
            dataType: "json",
            success: function (data) {
               if (data.form_es_valido) {
                    $('#modal-vcontratados-seccion').modal('hide');
                    RecargarTabla();
                }
               else {
                    $('#modal-vcontratados-seccion .modal-content').html(data.html_form);
                    $('#tareas_veh_civil_sec').select2({
                        theme: "bootstrap4",
                        allowClear: true,
                        placeholder: 'Seleccione',
                    });
//                    $('#responsable_veh_contratado_sec').select2({
//                        theme: "bootstrap4",
//                        placeholder: 'Seleccione',
//                        allowClear: true,
//                        language: {
//                            inputTooShort: function (args) {
//                                // args.minimum is the minimum required length
//                                // args.input is the user-typed text
//                                var t = args.minimum - args.input.length
//                                return 'Ingrese ' + t + ' caracteres del DNI o apellido';
//                            },
//                            noResults: function () {
//                                return "No se encontraron resultados";
//                            },
//                            searching: function () {
//
//                                return "Buscando..";
//                            }
//                        },
//                       ajax: {
//                            url: "{% url 'obtener-personas' %}",
//                            dataType: 'json',
//                            processResults: function (data) {
//                                return {
//                                    results: $.map(data, function (item) {
//                                        return {
//                                            id: item.id, text: item.grado__grado+ ' ' + item.nombre
//                                                + ' ' + item.apellido + ' ' + item.dni
//                                        };
//                                    })
//                                };
//                            },
//                        },
//                        minimumInputLength: 3
//                    });
                    jQuery.datetimepicker.setLocale('es');
                    setTimeout(function () {
                        $('#veh_cont_seccion').select2({
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    allowClear: true,
                    language: {
                        inputTooShort: function (args) {
                            // args.minimum is the minimum required length
                            // args.input is the user-typed text
                            var t = args.minimum - args.input.length
                            return 'Ingrese ' + t + ' caracteres del vehículo o NI';
                        },
                        noResults: function () {
                            return "No se encontraron resultados";
                        },
                        searching: function () {

                            return "Buscando..";
                        }
                    },
                    ajax: {
                        url: "{% url 'obtener-veh-contratados' %}",
                        dataType: 'json',
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: ' Patente: ' + item.patente_matricula + ' Tipo: ' + item.tipo_vehiculo_contratado__tipo_vehiculo_civil
                                    };
                                })
                            };
                        },
                    },
                    minimumInputLength: 3
                });
                        $('#id_desde_veh_civil_sec').datetimepicker({
                            //maxDate: tomorrow,
                            timepicker: false,
                            format: 'd/m/Y',
                        });
                        $('#id_hasta_veh_civil_sec').datetimepicker({
                            //maxDate: tomorrow,
                            timepicker: false,
                            format: 'd/m/Y',
                        });
                    }, 300);
                }
            }
        })
        return false;
    };
    $('#agregar-vehiculos-contratados-seccion').click(MostrarFormularioVhContratadosSeccion)
    $("#modal-vcontratados-seccion").on("submit", ".crear-vhcontratados-en-seccion", GuardarFormularioVhContratadosSeccion)
    $("#modal-vcontratados-seccion").on("submit", ".actualizar-vhcontratados-en-seccion", GuardarFormularioVhContratadosSeccion)
    $('#tabla-vehiculos-contratados-seccion tbody').on('click', '#editar-vhcontratado-seccion', function () {
        comprobarSesion()
        let id = $(this).attr('id_edit_vc_sec');
        //console.log(window.location.origin)
        $.ajax({
            url: "{% url 'actualizar-vhcontratados-seccion' 77 %}".replace('77', id),
            type: 'get',
            dataType: "json",
            success: function (data) {
                $('#modal-vcontratados-seccion .modal-content').html(data.html_form);
                $('#modal-vcontratados-seccion').modal('show')
                $('#tareas_veh_civil_sec').select2({
                        theme: "bootstrap4",
                        allowClear: true,
                        placeholder: 'Seleccione',
                    });
//                $('#responsable_veh_contratado_sec').select2({
//                        theme: "bootstrap4",
//                        placeholder: 'Seleccione',
//                        allowClear: true,
//                        language: {
//                            inputTooShort: function (args) {
//                                // args.minimum is the minimum required length
//                                // args.input is the user-typed text
//                                var t = args.minimum - args.input.length
//                                return 'Ingrese ' + t + ' caracteres del DNI o apellido';
//                            },
//                            noResults: function () {
//                                return "No se encontraron resultados";
//                            },
//                            searching: function () {
//
//                                return "Buscando..";
//                            }
//                        },
//                       ajax: {
//                            url: "{% url 'obtener-personas' %}",
//                            dataType: 'json',
//                            processResults: function (data) {
//                                return {
//                                    results: $.map(data, function (item) {
//                                        return {
//                                            id: item.id, text: item.grado__grado+ ' ' + item.nombre
//                                                + ' ' + item.apellido + ' ' + item.dni
//                                        };
//                                    })
//                                };
//                            },
//                        },
//                        minimumInputLength: 3
//                    });
                jQuery.datetimepicker.setLocale('es');
                    setTimeout(function () {
                        $('#veh_cont_seccion').select2({
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    allowClear: true,
                    language: {
                        inputTooShort: function (args) {
                            // args.minimum is the minimum required length
                            // args.input is the user-typed text
                            var t = args.minimum - args.input.length
                            return 'Ingrese ' + t + ' caracteres del vehículo o NI';
                        },
                        noResults: function () {
                            return "No se encontraron resultados";
                        },
                        searching: function () {

                            return "Buscando..";
                        }
                    },
                    ajax: {
                        url: "{% url 'obtener-veh-contratados' %}",
                        dataType: 'json',
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: ' Patente: ' + item.patente_matricula + ' Tipo: ' + item.tipo_vehiculo_contratado__tipo_vehiculo_civil
                                    };
                                })
                            };
                        },
                    },
                    minimumInputLength: 3
                });
                        $('#id_desde_veh_civil_sec').datetimepicker({
                            //maxDate: tomorrow,
                            timepicker: false,
                            format: 'd/m/Y',
                        });
                        $('#id_hasta_veh_civil_sec').datetimepicker({
                            //maxDate: tomorrow,
                            timepicker: false,
                            format: 'd/m/Y',
                        });
                    }, 300);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert('Error modificando datos de vehículos contratados en la Sección');
            }
        });
    });
    $('#tabla-vehiculos-contratados-seccion tbody').on('click', '#elimiar-vhcontratado-seccion', function () {
        comprobarSesion()
        var id = $(this).attr('id_del_vc_sec')
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
                    url: "{% url 'eliminar-vhcontratados-seccion' 66 %}".replace('66', id),
                    type: "get",
                    dataType: "json",
                    success: function (data) {
                        if (data.permitido) {
                            RecargarTabla();
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        alert('Error eliminando datos de vehículos contratados en la Sección');
                    }
                });
            }
        })
    });
});


