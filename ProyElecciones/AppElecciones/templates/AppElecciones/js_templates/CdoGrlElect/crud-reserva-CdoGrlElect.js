var csrftoken = Cookies.get('csrftoken');
$(function () {
    $("#pills-reserva-tab").click(function () {
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
    var tabla_reserva_cge = $('#tabla-reserva-cge').DataTable({
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
            url: "{% url 'listar-reserva-en-cge' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: { 'id_cge': id_cge },
        },
        columns: [
            { data: 'persona', orderable: false },
            { data: 'obs', orderable: false },
            {
                data: null,
                orderable: false,

                render:  function(data, type, row){
                    let boton = '';
                    if (row.editar){
                        boton += '<span id="editar-reserva-cge" title="Editar" id_edit_res="'+row.id+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp'
                    }
                    if (row.eliminar) {
                        boton += '<span id="elimiar-reserva-cge" title="Eliminar" id_del_res="'+row.id+'" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
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
        tabla_reserva_cge.ajax.reload(null, true);
    };
    var MostrarFormularioReservacge = function () {
        comprobarSesion()
        var boton = $(this);
        $.ajax({
            url: boton.attr("data-url"),
            type: "get",
            dataType: "json",
            success: function (data) {
                $('#modal-reserva-cge .modal-content').html(data.html_form);
                $('#modal-reserva-cge').modal('show')
                $('#integrante_reserva_cge').select2({
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
    var GuardarFormularioReservacge = function () {
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
                    $('#modal-reserva-cge').modal('hide');
                    RecargarTabla();
                }
                else {
                    $('#modal-reserva-cge .modal-content').html(data.html_form);
                    $('#integrante_reserva_cge').select2({
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
                        ajax: {
                            url: "{% url 'crear-reserva-en-cge' %}",
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
    $('#mostrar-formulario-reserva-cge').click(MostrarFormularioReservacge)
    $("#modal-reserva-cge").on("submit", ".agregar-reserva-cge", GuardarFormularioReservacge)
    $("#modal-reserva-cge").on("submit", ".modificar-reserva-cge", GuardarFormularioReservacge)
    $('#tabla-reserva-cge tbody').on('click', '#editar-reserva-cge', function () {
        comprobarSesion()
        var id = $(this).attr('id_edit_res')
        $.ajax({
            url: "{% url 'actualizar-reserva-en-cge' 33 %}".replace('33', id),
            type: 'get',
            dataType: "json",
            success: function (data) {
                //console.log(data.html_form)
                $('#modal-reserva-cge .modal-content').html(data.html_form);
                $('#modal-reserva-cge').modal('show')
                $('#integrante_reserva_cge').select2({
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
                alert('Error modificando datos de distribución de la reserva de personal en cge');
            }
        });
    });
    $('#tabla-reserva-cge tbody').on('click', '#elimiar-reserva-cge', function () {
        comprobarSesion()
        var id = $(this).attr('id_del_res')
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
                    url: "{% url 'eliminar-reserva-en-cge' 88 %}".replace('88', id),
                    type: "get",
                    dataType: "json",
                    success: function (data) {
                        if (data.permitido) {
                            RecargarTabla();
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        alert('Error eliminando datos de reserva de personal en cge');
                    }
                });
            }
        })
    });
});


