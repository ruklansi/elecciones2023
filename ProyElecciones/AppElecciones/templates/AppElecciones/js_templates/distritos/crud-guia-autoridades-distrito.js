var csrftoken = Cookies.get('csrftoken');
$(function () {
     $("#pills-guia-de-tab").click(function () {
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
    let id_del_distrito = parseInt('{{ object.id }}')
    var tabla_guia_distrito = $('#tabla-guia-distrito').DataTable({
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
            url: "{% url 'listado-guia-distrito' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: { 'id_del_distrito': id_del_distrito },

        },
        columns: [
            { data: 'puesto_texto', orderable: false },
            { data: 'org_texto', orderable: false },
            { data: 'persona', orderable: false },
            { data: 'tel_guia', orderable: false },
            { data: 'gde_guia', orderable: false },
            {
                data: null,
                orderable: false,
                render:   function(data, type, row){
                    let boton = '';
                    if (row.editar){
                        boton += '<span id="editar-guia-distrito" id_edit_distrito="'+row.id+'"  title="Editar" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp'
                    }
                    if (row.eliminar){
                        boton += '<span id="eliminar-guia-distrito" id_del_distrito="'+row.id+'"  title="Eliminar" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
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
        tabla_guia_distrito.ajax.reload(null, true);
    };
    var MostrarFormularioGuiaDistrito = function () {
        comprobarSesion();
        var boton = $(this);
        $.ajax({
            url: boton.attr("data-url"),
            type: "get",
            dataType: "json",

            success: function (data) {
                $('#modal-guia-distrito .modal-content').html(data.html_form);
                $('#modal-guia-distrito').modal('show')
                $('#id_puesto_guia').select2({
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    multiple: true,
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
                });
                $('#id_persona_guia').select2({
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
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: item.grado__grado+ ' ' + item.nombre
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
    var GuardarFormularioGuiaDistrito = function () {
        comprobarSesion();
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('data-url'),
            data: form.serialize(),
            dataType: "json",
            success: function (data) {
                //console.log(data)
                if (data.form_es_valido) {
                    $('#modal-guia-distrito').modal('hide');
                    RecargarTabla();
                }
                else {
                    $('#modal-guia-distrito .modal-content').html(data.html_form);
                    $('#id_puesto_guia').select2({
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    multiple: true,
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
                });
                    $('#id_persona_guia').select2({
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
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: item.grado__grado+ ' ' + item.nombre
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
    $('#mostrar-formulario-guia-distrito').click(MostrarFormularioGuiaDistrito)
    $("#modal-guia-distrito").on("submit", ".agregar-guia-distrito", GuardarFormularioGuiaDistrito)
    $("#modal-guia-distrito").on("submit", ".modificar-guia-distrito", GuardarFormularioGuiaDistrito)
    $('#tabla-guia-distrito tbody').on('click', '#editar-guia-distrito', function () {
        comprobarSesion();
        var id = $(this).attr('id_edit_distrito')
        $.ajax({
            type: "get",
            url: "{% url 'actualizar-persona-guia-distrito' 75 %}".replace('75', id),
            dataType: "json",
            headers: { 'X-CSRFToken': csrftoken },
            success: function (data) {
//                console.log(data)
                $('#modal-guia-distrito').modal('show');
                $('#modal-guia-distrito .modal-content').html(data.html_form);
                $('#id_puesto_guia').select2({
                    theme: "bootstrap4",
                    placeholder: 'Seleccione',
                    multiple: true,
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
                });
                $('#id_persona_guia').select2({
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
                        processResults: function (data) {
                            return {
                                results: $.map(data, function (item) {
                                    return {
                                        id: item.id, text: item.grado__grado+ ' ' + item.nombre
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
                alert('Error:' + textStatus + ': ' + errorThrown + ': ' + jqXHR.status + ': ' + jqXHR.statusText);
            }

        })
    });
    $('#tabla-guia-distrito tbody').on('click', '#eliminar-guia-distrito', function () {
        comprobarSesion();
        var id = $(this).attr('id_del_distrito')
        Swal.fire({
            text: "Borrar este registro ?",
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '',
            confirmButtonText: 'Sí, borrarlo'
        }).then((result) => {
            if (result.value) {
                $.ajax({
                    url: "{% url 'eliminar-persona-guia-distrito' 77 %}".replace('77', id),
                    type: "get",
                    dataType: "json",
                    success: function (data) {
                        if (data.permitido) {
                            RecargarTabla();
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        alert('Error eliminando guia cge:' + jqXHR.status, textStatus, errorThrown);
                    }
                });
            }
        })
    });
});


