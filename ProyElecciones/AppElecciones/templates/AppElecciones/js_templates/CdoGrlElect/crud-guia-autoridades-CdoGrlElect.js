var csrftoken = Cookies.get('csrftoken');
$(function () {
    $("#pills-guia-cge-tab").click(function () {
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
    var tabla_guia_cge = $('#tabla-guia-cge').DataTable({
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
            url: "{% url 'listado-guia-cge' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: { 'id_cge': id_cge },
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
                        boton += '<span id="editar-guia-cge" id_edit_guia="'+row.id+'"  title="Editar" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp'
                    }
                    if (row.eliminar){
                        boton += '<span id="eliminar-guia-cge" id_del_guia="'+row.id+'"  title="Eliminar" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
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
        tabla_guia_cge.ajax.reload(null, true);
    };
    var MostrarFormularioGuiaCge = function () {
        comprobarSesion();
        var boton = $(this);
        $.ajax({
            url: boton.attr("data-url"),
            type: "get",
            dataType: "json",
            data: { 'id_cge': id_cge },
            success: function (data) {
                $('#modal-guia-cge .modal-content').html(data.html_form);
                $('#modal-guia-cge').modal('show')
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
    var GuardarFormularioGuiaCge = function () {
        comprobarSesion();
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('data-url'),
            data: form.serialize() + "&id_cge=" + id_cge,
            dataType: "json",
            success: function (data) {
                //console.log(data)
                if (data.form_es_valido) {
                    $('#modal-guia-cge').modal('hide');
                    RecargarTabla();
                }
                else {
                    $('#modal-guia-cge .modal-content').html(data.html_form);
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
    $('#mostrar-formulario-guia-cge').click(MostrarFormularioGuiaCge)
    $("#modal-guia-cge").on("submit", ".agregar-guia-cge", GuardarFormularioGuiaCge)
    $("#modal-guia-cge").on("submit", ".modificar-guia-cge", GuardarFormularioGuiaCge)
    $('#tabla-guia-cge tbody').on('click', '#editar-guia-cge', function () {
        comprobarSesion();
        var id = $(this).attr('id_edit_guia')
        $.ajax({
            type: "get",
            url: "{% url 'actualizar-persona-guia-cge' 75 %}".replace('75', id),
            dataType: "json",
            headers: { 'X-CSRFToken': csrftoken },
            success: function (data) {
//                console.log(data)
                $('#modal-guia-cge').modal('show');
                $('#modal-guia-cge .modal-content').html(data.html_form);
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
    $('#tabla-guia-cge tbody').on('click', '#eliminar-guia-cge', function () {
        comprobarSesion();
        var id = $(this).attr('id_del_guia')
        Swal.fire({
            text: "Borrar este registro ?",
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '',
            confirmButtonText: 'Sí, borrarlo'
        }).then((result) => {
            if (result.value) {
                $.ajax({
                    url: "{% url 'eliminar-persona-guia-cge' 77 %}".replace('77', id),
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


