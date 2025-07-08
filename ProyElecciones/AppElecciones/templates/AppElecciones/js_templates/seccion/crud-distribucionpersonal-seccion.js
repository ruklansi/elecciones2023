var csrftoken = Cookies.get('csrftoken');
$(function () {
    $("#pills-organizacion-tab").click(function () {
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
    var tabla_distribucion_personal_seccion = $('#tabla-distribucion-personal-seccion').DataTable({
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
            url: "{% url 'listar-organizacion-en-seccion' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: { 'id_seccion': id_seccion },
        },
        columns: [
            { data: 'cargo__cargo', orderable: false },
            { data: 'designacion', orderable: false },
            { data: 'persona', orderable: false },
            {
                data: null,
                orderable: false,
                render:  function(data, type, row){
                    let boton = '';
                    if (row.editar){
                        boton += '<span id="editar-distribucion-personal-seccion" id_edit_pers_sec="'+row.id+'"   title="Editar" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp'
                    }
                    if (row.eliminar){
                        boton += '<span id="elimiar-distribucion-personal-seccion" id_del_pers_sec="'+row.id+'" title="Eliminar" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
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
        tabla_distribucion_personal_seccion.ajax.reload(null, true);
    };
    var MostrarFormularioDistribucionPersonalSeccion = function () {
        comprobarSesion()
        var boton = $(this);
        $.ajax({
            url: boton.attr("data-url"),
            type: "get",
            dataType: "json",
            success: function (data) {
                $('#modal-distribucion-personal-seccion .modal-content').html(data.html_form);
                $('#modal-distribucion-personal-seccion').modal('show')
                $('#cargo_pers_sec').select2({
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
                $('#integrante_pers_sec').select2({
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
                    ajax: {
                        url: "{% url 'obtener-personas' %}",
                        dataType: 'json',
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
    var GuardarFormularioDistribucionPersonalSeccion = function () {
        comprobarSesion()
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('data-url'),
            data: form.serialize() + "&id_seccion=" + id_seccion,
            dataType: "json",
            success: function (data) {
                //console.log(data)
                if (data.form_es_valido) {
                    $('#modal-distribucion-personal-seccion').modal('hide');
                    RecargarTabla();
                }
                else {
                    $('#modal-distribucion-personal-seccion .modal-content').html(data.html_form);
                    $('#cargo_pers_sec').select2({
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
                    $('#integrante_pers_sec').select2({
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
                    ajax: {
                        url: "{% url 'obtener-personas' %}",
                        dataType: 'json',
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
    $('#mostrar-formulario-organizacion-seccion').click(MostrarFormularioDistribucionPersonalSeccion)
    $("#modal-distribucion-personal-seccion").on("submit", ".agregar-distribucion-personal-seccion", GuardarFormularioDistribucionPersonalSeccion)
    $("#modal-distribucion-personal-seccion").on("submit", ".modificar-distribucion-personal-seccion", GuardarFormularioDistribucionPersonalSeccion)
    $('#tabla-distribucion-personal-seccion tbody').on('click', '#editar-distribucion-personal-seccion', function () {
        comprobarSesion()
        let id = $(this).attr('id_edit_pers_sec');
        $.ajax({
            url: "{% url 'actualizar-organizacion-en-seccion' 44 %}".replace('44', id),
            type: 'get',
            dataType: "json",
            success: function (data) {
                $('#modal-distribucion-personal-seccion .modal-content').html(data.html_form);
                $('#modal-distribucion-personal-seccion').modal('show')
                $('#cargo_pers_sec').select2({
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
                $('#integrante_pers_sec').select2({
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
                    ajax: {
                        url: "{% url 'obtener-personas' %}",
                        dataType: 'json',
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
                alert('Error modificando datos de distribución de personal en la Sección');
            }
        });
    });
    $('#tabla-distribucion-personal-seccion tbody').on('click', '#elimiar-distribucion-personal-seccion', function () {
        comprobarSesion()
        let id =  $(this).attr('id_del_pers_sec');
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
                    url: "{% url 'eliminar-organizacion-en-seccion' 77 %}".replace('77', id),
                    type: "get",
                    dataType: "json",
                    success: function (data) {
                        if (data.permitido) {
                            RecargarTabla();
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        alert('Error eliminando datos de distribución de personal en la Sección');
                    }
                });
            }
        })
    });
});


