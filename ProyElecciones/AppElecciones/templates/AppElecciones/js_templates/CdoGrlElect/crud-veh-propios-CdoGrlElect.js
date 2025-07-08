var csrftoken = Cookies.get('csrftoken');
$(function () {
    $("#pills-vpropios-tab").click(function () {
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
    let id_cge = parseInt('{{ object.id }}')
    var tabla_vhpropios_cge = $('#tabla-vehiculos-propios-cge').DataTable({
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
            url: "{% url 'listar-vhpropios-en-cge' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: { 'id_cge': id_cge },
        },
        columns: [
            { data: 'veh_propio__tipo_vehiculo_provisto__tipo_vehiculo_provisto', orderable: false },
            { data: 'veh_propio__ni_patente_matricula', orderable: false },
            { data: 'zona_trabajo', orderable: false},
//            { data: 'cond_veh_propio', orderable: false },
            {
                data: null,
                orderable: false,
                render:  function(data, type, row){
                    let boton = '';
                    if (row.editar){
                        boton += '<span id="editar-vhpropio-cge" title="Editar" id_edit_vp="'+row.id+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp'
                    }
                    if (row.eliminar){
                        boton += '<span id="elimiar-vhpropio-cge" id_del_vp="'+row.id+'" title="Eliminar" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
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
        tabla_vhpropios_cge.ajax.reload(null, true);
    };
    var MostrarFormularioVhPropioscge = function () {
        comprobarSesion()
        var boton = $(this);
        $.ajax({
            url: boton.attr("data-url"),
            type: "get",
            dataType: "json",
            success: function (data) {
                $('#modal-vpropios-cge .modal-content').html(data.html_form);
                $('#modal-vpropios-cge').modal('show')
                $('#veh_propio').select2({
                    //dropdownParent: $('#modal-seg-interna'),
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
                        url: "{% url 'obtener-veh-propios' %}",
                        dataType: 'json',
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: ' NI: ' + item.ni_patente_matricula + ' Tipo: ' + item.tipo_vehiculo_provisto__tipo_vehiculo_provisto + ' Unidad: ' + item.unidad__nombre
                                    };
                                })
                            };
                        },
                    },
                    minimumInputLength: 3
                });
//                $('#conductor_veh_propio').select2({
//                    //dropdownParent: $('#modal-seg-interna'),
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
                $('#tareas').select2({
                    theme: "bootstrap4",
                    allowClear: true,
                    placeholder: 'Seleccione',
                });
                jQuery.datetimepicker.setLocale('es');
                setTimeout(function () {
                    $('#id_desde').datetimepicker({
                        //maxDate: tomorrow,
                        timepicker: false,
                        format: 'd/m/Y',
                    });
                    $('#id_hasta').datetimepicker({
                        //maxDate: tomorrow,
                        timepicker: false,
                        format: 'd/m/Y',
                    });
                }, 300);
            }
        });
    };
    var GuardarFormularioVhPropioscge = function () {
        comprobarSesion()
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('data-url'),
            data: form.serialize() + "&id_cge=" + id_cge,
            dataType: "json",
            success: function (data) {
                //console.log(data)
                if (data.form_es_valido) {
                    $('#modal-vpropios-cge').modal('hide');
                    RecargarTabla();
                }
                else {
                    $('#modal-vpropios-cge .modal-content').html(data.html_form);
                    $('#veh_propio').select2({
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
                            url: "{% url 'obtener-veh-propios' %}",
                            dataType: 'json',
                            processResults: function (data) {
                                return {
                                    results: $.map(data, function (item) {
                                        return {
                                            id: item.id, text: ' NI: ' + item.ni_patente_matricula + ' Tipo: ' + item.tipo_vehiculo_provisto__tipo_vehiculo_provisto + ' Unidad: ' + item.unidad__nombre
                                        };
                                    })
                                };
                            },
                        },
                        minimumInputLength: 3
                    });
//                    $('#conductor_veh_propio').select2({
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
                    $('#tareas').select2({
                        theme: "bootstrap4",
                        allowClear: true,
                        placeholder: 'Seleccione',
                    });
                    jQuery.datetimepicker.setLocale('es');
                    setTimeout(function () {
                        $('#id_desde').datetimepicker({
                            //maxDate: tomorrow,
                            timepicker: false,
                            format: 'd/m/Y',
                        });
                        $('#id_hasta').datetimepicker({
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
    $('#agregar-vehiculos-propios-cge').click(MostrarFormularioVhPropioscge)
    $("#modal-vpropios-cge").on("submit", ".crear-vhpropios-en-cge", GuardarFormularioVhPropioscge)
    $("#modal-vpropios-cge").on("submit", ".actualizar-vhpropios-en-cge", GuardarFormularioVhPropioscge)
    $('#tabla-vehiculos-propios-cge tbody').on('click', '#editar-vhpropio-cge', function () {
        comprobarSesion()
        var id = $(this).attr('id_edit_vp')
        //console.log(window.location.origin)
        $.ajax({
            url: "{% url 'actualizar-vhpropios-en-cge' 55 %}".replace('55', id),
            type: 'get',
            dataType: "json",
            //data: { 'id_local': id_local },
            success: function (data) {
                //console.log(data.html_form)
                $('#modal-vpropios-cge .modal-content').html(data.html_form);
                $('#modal-vpropios-cge').modal('show')
                $('#veh_propio').select2({
                    //dropdownParent: $('#modal-seg-interna'),
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
                        url: "{% url 'obtener-veh-propios' %}",
                        dataType: 'json',
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: ' NI: ' + item.ni_patente_matricula + ' Tipo: ' + item.tipo_vehiculo_provisto__tipo_vehiculo_provisto + ' Unidad: ' + item.unidad__nombre
                                    };
                                })
                            };
                        },
                    },
                    minimumInputLength: 3
                });
//                $('#conductor_veh_propio').select2({
//                    //dropdownParent: $('#modal-seg-interna'),
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
                $('#tareas').select2({
                    theme: "bootstrap4",
                    allowClear: true,
                    placeholder: 'Seleccione',
                });
                jQuery.datetimepicker.setLocale('es');
                setTimeout(function () {
                    $('#id_desde').datetimepicker({
                        //maxDate: tomorrow,
                        timepicker: false,
                        format: 'd/m/Y',
                    });
                    $('#id_hasta').datetimepicker({
                        //maxDate: tomorrow,
                        timepicker: false,
                        format: 'd/m/Y',
                    });
                }, 300);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert('Error modificando datos de vehículos propios en el cge');
            }
        });

    });
    $('#tabla-vehiculos-propios-cge tbody').on('click', '#elimiar-vhpropio-cge', function () {
        comprobarSesion()
        var id = $(this).attr('id_del_vp')
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
                    url: "{% url 'eliminar-vhpropios-en-cge' 44 %}".replace('44', id),
                    type: "get",
                    dataType: "json",
                    success: function (data) {
                        if (data.permitido) {
                            RecargarTabla();
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        alert('Error eliminando datos de vehículos propios en el cge');
                    }
                });
            }
        })
    });
});


