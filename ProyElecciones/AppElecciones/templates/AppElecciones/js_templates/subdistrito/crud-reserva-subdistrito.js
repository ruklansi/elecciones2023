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
    var id_subdistrito = parseInt('{{ object.id }}')
    var tabla_reserva_subdistrito = $('#tabla-reserva-subdistrito').DataTable({
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
            url: '{% url "listar-reserva-en-subdistrito" %}',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: { 'id_subdistrito': id_subdistrito },
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
                        boton += '<span id="editar-reserva-subdistrito" title="Editar" id_edit_res_sub="'+row.id+'"   class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp'
                    }
                    if (row.eliminar){
                        boton += '<span id="elimiar-reserva-subdistrito" id_del_res_sub="'+row.id+'" title="Eliminar" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
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
        tabla_reserva_subdistrito.ajax.reload(null, true);
    };
    var MostrarFormularioReservaSubdistrito = function () {
        comprobarSesion()
        var boton = $(this);
        $.ajax({
            url: boton.attr("data-url"),
            type: "get",
            dataType: "json",
            success: function (data) {
                $('#modal-reserva-subdistrito .modal-content').html(data.html_form);
                $('#modal-reserva-subdistrito').modal('show')
                $('#integrante_reserva_subdistrito').select2({
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
                        url: '{% url "obtener-personas" %}',
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
    var GuardarFormularioReservaSubdistrito = function () {
        comprobarSesion()
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('data-url'),
            data: form.serialize() + "&id_subdistrito=" + id_subdistrito,
            dataType: "json",
            success: function (data) {
                //console.log(data)
                if (data.form_es_valido) {
                    $('#modal-reserva-subdistrito').modal('hide');
                    RecargarTabla();
                }
                else {
                    $('#modal-reserva-subdistrito .modal-content').html(data.html_form);
                    $('#integrante_reserva_subdistrito').select2({
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
                            url: '{% url "obtener-personas" %}',
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
    $('#mostrar-formulario-reserva-subdistrito').click(MostrarFormularioReservaSubdistrito)
    $("#modal-reserva-subdistrito").on("submit", ".agregar-reserva-en-subdistrito", GuardarFormularioReservaSubdistrito)
    $("#modal-reserva-subdistrito").on("submit", ".modificar-reserva-en-subdistrito", GuardarFormularioReservaSubdistrito)
    $('#tabla-reserva-subdistrito tbody').on('click', '#editar-reserva-subdistrito', function () {
        comprobarSesion()
        let id = $(this).attr('id_edit_res_sub');
        //console.log(window.location.origin)
        $.ajax({
            url: "{% url 'actualizar-reserva-en-subdistrito' 99 %}".replace(99,id),
            type: 'get',
            dataType: "json",
            success: function (data) {
                //console.log(data.html_form)
                $('#modal-reserva-subdistrito .modal-content').html(data.html_form);
                $('#modal-reserva-subdistrito').modal('show')
                $('#integrante_reserva_subdistrito').select2({
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
                alert('Error modificando datos de distribucion de la reserva de personal en Subdistrito');
            }
        });
    });
    $('#tabla-reserva-subdistrito tbody').on('click', '#elimiar-reserva-subdistrito', function () {
        comprobarSesion()
        let id = $(this).attr('id_del_res_sub');
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
                    url: "{% url 'eliminar-reserva-en-subdistrito'  99 %}".replace('99',id),
                    type: "get",
                    dataType: "json",
                    success: function (data) {
                        if (data.permitido) {
                            RecargarTabla();
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        alert('Error eliminando datos de reserva de personal en subdistrito');
                    }
                });
            }
        })
    });
});


