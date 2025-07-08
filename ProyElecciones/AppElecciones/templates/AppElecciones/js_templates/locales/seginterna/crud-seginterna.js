var csrftoken = Cookies.get('csrftoken');
$(function () {
    $("#pills-home-tab").click(function () {
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
    let id_local = parseInt('{{ object.id }}')
    var tabla_seg_interna = $('#tabla-seg-interna').DataTable({
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        //lengthMenu: [[5, 10], [5, 10]],
        pageLength: 1,
        //order: [[1, "asc"]],
        paging: false,
        bFilter: false,
        ajax: {
            url: "{% url 'listado-de-seguridad-interna' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'id_local': id_local
            },
        },
        columns: [
            {
                className: 'details-control',
                orderable: false,
                data: null,
                defaultContent: ''
            },
            {
                data: 'jefe',
                orderable: false,
            },
            {
                data: null,
                orderable: false,
                render:  function(data, type, row){
                    let boton = '';
                    if (row.editar){
                        boton += '<span id="editar-seg-interna" id_edit_seg_int_local="'+row.id+'"  title="Editar" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp'
                    }
                    if (row.eliminar){
                        boton += '<span id="elimiar-seg-interna"id_del_seg_int_local="'+row.id+'" title="Eliminar" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
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
        initComplete: function (settings, json) {
            //Oculto o muestro el boton de agregar seg interna
            if (json.data.length>0) {
                $('#boton-agregar').hide()

            }
            else {
                $('#boton-agregar').show()

            }

        }
    });
    //Otra forma de obtener datos del datatables para futuros usos
    //var info = tabla_seg_interna.page.info();
    //console.log(info.recordsTotal);
    function RecargarTabla() {
        comprobarSesion()
        tabla_seg_interna.ajax.reload(function (json) {
            //Oculto o muestro el boton de agregar seg interna
            if (json.data.length>0) {
                $('#boton-agregar').hide()

            }
            else {
                $('#boton-agregar').show()

            }
            console.log(json.data)
        }, true);
    };
    var MostrarFormularioSegInterna = function () {
        comprobarSesion()
        var boton = $(this);
        $.ajax({
            url: boton.attr("data-url"),
            type: "get",
            dataType: "json",
            data: { 'id_local': id_local },
            beforeSend: function () {
            },
            success: function (data) {
                //Respetar este orden para que funcione select2

                $('#modal-seg-interna .modal-content').html(data.html_form);
                $('#modal-seg-interna').modal('show')
                $('#id_jefe_local').select2({
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    allowClear: true,
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
                    ajax: {
                        url: "{% url 'obtener-personas' %}",
                        dataType: 'json',
                        headers: { 'X-CSRFToken': csrftoken },
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: item.grado__grado + ' ' + item.nombre
                                            + ' ' + item.apellido + ' ' + item.dni
                                    };
                                })
                            };
                        },
                    },
                    minimumInputLength: 3

                });
                $('#id_auxiliares').select2({
                    //dropdownParent: $('#modal-seg-interna'),
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    allowClear: true,
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
                    ajax: {
                        url: "{% url 'obtener-personas' %}",
                        dataType: 'json',
                        headers: { 'X-CSRFToken': csrftoken },
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: item.grado__grado + ' ' + item.nombre
                                            + ' ' + item.apellido + ' ' + item.dni
                                    };
                                })
                            };

                        },
                    },
                    minimumInputLength: 3

                });
            }
        });
    };
    var GuardarFormularioSegInterna = function () {
        comprobarSesion()
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('data-url'),
            data: form.serialize() + "&id_local=" + id_local,
            dataType: "json",
            headers: { 'X-CSRFToken': csrftoken },
            success: function (data) {

                if (data.form_es_valido) {
                    $('#boton-agregar').hide()

                    $('#modal-seg-interna').modal('hide');
                    RecargarTabla();
                     Swal.fire({
                         position: 'center',
                         text: data['mensaje'],
                         showConfirmButton: false,
                         timer: 1500
                     });
                }
                else {
                    //$('#modal-seg-interna .modal-content').html(data.html_form)
                    $('#modal-seg-interna .modal-content').html(data.html_form);
                    $('#id_jefe_local').select2({
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
                        //dropdownParent: $('#modal-seg-interna'),
                        ajax: {
                            url: "{% url 'obtener-personas' %}",
                            dataType: 'json',
                            headers: { 'X-CSRFToken': csrftoken },
                            processResults: function (data) {
                                return {
                                    results: $.map(data, function (item) {
                                        return {
                                            id: item.id, text: item.grado__grado + ' ' + item.nombre
                                                + ' ' + item.apellido + ' ' + item.dni
                                        };
                                    })
                                };

                            },
                        },
                        minimumInputLength: 3

                    });
                    $('#id_auxiliares').select2({
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
                        //dropdownParent: $('#modal-seg-interna'),
                        ajax: {
                            url: "{% url 'obtener-personas' %}",
                            dataType: 'json',
                            headers: { 'X-CSRFToken': csrftoken },
                            processResults: function (data) {
                                return {
                                    results: $.map(data, function (item) {
                                        return {
                                            id: item.id, text: item.grado__grado + ' ' + item.nombre
                                                + ' ' + item.apellido + ' ' + item.dni
                                        };
                                    })
                                };
                            },
                        },
                        minimumInputLength: 3
                    });
                }
            }
        })
        return false;
    };
    $('#mostrar-modal-seg-interna').click(MostrarFormularioSegInterna)
    $("#modal-seg-interna").on("submit", ".agregar-seginterna", GuardarFormularioSegInterna)
    $("#modal-seg-interna").on("submit", ".actualizar-seginterna", GuardarFormularioSegInterna);
    $('#tabla-seg-interna tbody').on('click', '#editar-seg-interna', function () {
        comprobarSesion()
        var id = $(this).attr('id_edit_seg_int_local');
        $.ajax({
            url: "{% url 'actualizar-seguridad-interna' 99 %}".replace('99', id),
            type: "get",
            dataType: "json",
            headers: { 'X-CSRFToken': csrftoken },
            data: { 'id_local': id_local },
            success: function (data) {
                // $('#modal-seg-interna').modal('show');
                // $('#modal-seg-interna .modal-content').html(data.html_form);
                $('#modal-seg-interna .modal-content').html(data.html_form);
                $('#modal-seg-interna').modal('show')
                $('#id_jefe_local').select2({
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    allowClear: true,
                    //language: 'es',
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
                    //dropdownParent: $('#modal-seg-interna'),
                    ajax: {
                         url: "{% url 'obtener-personas' %}",
                        dataType: 'json',
                        headers: { 'X-CSRFToken': csrftoken },
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: item.grado__grado + ' ' + item.nombre
                                            + ' ' + item.apellido + ' ' + item.dni
                                    };
                                })
                            };

                        },
                    },
                    minimumInputLength: 3

                });
                $('#id_auxiliares').select2({
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    allowClear: true,
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
                    //dropdownParent: $('#modal-seg-interna'),
                    ajax: {
                        url: "{% url 'obtener-personas' %}",
                        dataType: 'json',
                        headers: { 'X-CSRFToken': csrftoken },
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: item.grado__grado + ' ' + item.nombre
                                            + ' ' + item.apellido + ' ' + item.dni
                                    };
                                })
                            };

                        },
                    },
                    minimumInputLength: 3

                });
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert('Error modificando datos de seguridad interna');
            }
        });
    });
    $('#tabla-seg-interna tbody').on('click', '#elimiar-seg-interna', function () {
        comprobarSesion()
        var id = $(this).attr('id_del_seg_int_local');
        Swal.fire({
            //title: 'Borrar este registro ?',
            text: "Borrar este registro",
            //icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '',
            confirmButtonText: 'Sí, borrarlo'
        }).then((result) => {
            if (result.value) {
                $.ajax({
                    url: "{% url 'eliminar-seguridad-interna' 777 %}".replace('777', id),
                    type: "get",
                    headers: { 'X-CSRFToken': csrftoken },
                    dataType: "json",
                    success: function (data) {
                        if (data.borrado) {
                            RecargarTabla();
                             Swal.fire({
                                 position: 'center',
                                 text: data['mensaje'],
                                 showConfirmButton: false,
                                 timer: 1500
                             });
                            $('#boton-agregar').show()
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        alert('Error borrando seguridad interna');
                    }
                });
            }
        })
    });
    function Auxiliares(d) {
        id_aux = d.id
        var div = $('<div/>')
            .addClass('cargando')
            .text('Cargando...');

        $.ajax({
            url: "{% url 'mostrar-auxiliares' 998 %}".replace('998', id_aux),
            type: "get",
            headers: { 'X-CSRFToken': csrftoken },
            dataType: "json",
            success: function (data) {
                //console.log(data)
                if (data.hay_dato) {
                    var mostrar = '<span class="visor_imagenes">AUXILIARES</span>' + '<br>';
                    $.each(data.auxiliares, function (i, d) {
                        mostrar += '<span>' + d + '</span>' + '<br>'
                    })
                    div.html(mostrar).removeClass('loading');
                }
                else {
                    var mostrar = '<span class="visor_imagenes">Sin auxiliares designados</span>' + '<br>';

                    div.html(mostrar).removeClass('loading');
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert('Error cargando auxiliares en la seg interna del local');
            }
        });
        return div

    }
    // Agregar un evento para cuando se abra o cierra
    $('#tabla-seg-interna tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = tabla_seg_interna.row(tr);
        if (row.child.isShown()) {
            // Este fila esta abierta - la cerramos
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Abrir la fila
            row.child(Auxiliares(row.data())).show();
            tr.addClass('shown');
        }
    });
});


