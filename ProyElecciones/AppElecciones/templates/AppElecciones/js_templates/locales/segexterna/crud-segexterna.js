var csrftoken = Cookies.get('csrftoken');
$(function () {
    $("#pills-profile-tab").click(function () {
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
    let id_local = parseInt('{{ object.id }}');
    var tabla_seg_externa = $('#tabla-seg-externa').DataTable({
            responsive: true,
            autoWidth: true,
            destroy: true,
            deferRender: true,
            processing: true,
            serverSide: true,
            //lengthMenu: [[5, 10], [5, 10]],
            pageLength: 5,
            order: [[0, "asc"]],
           //paging: false,
            //bFilter: false,
            ajax: {
                url: "{% url 'listado-de-seguridad-externa' %}",
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'id_local': id_local
                },
            },
            columns: [
                { data: 'fuerza__fuerza_seg', orderable: true },
                { data: 'cant_efectivos', orderable: true },
                {
                    data: null,
                    orderable: false,
                    render:  function(data, type, row){
                        let boton = '';
                        if (row.editar){
                            boton += '<span id="editar-seg-externa" title="Editar" id_edit_seg_ext_local="'+row.id+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp'
                        }
                        if (row.eliminar){
                            boton += '<span id="elimiar-seg-externa" title="Eliminar" id_del_seg_ext_local="'+row.id+'" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
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
            }
        });
    function RecargarTabla() {
            comprobarSesion()
            tabla_seg_externa.ajax.reload(null, true);
        };
    var MostrarFormularioSegExterna = function () {
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
                    $('#modal-seg-externa').modal('show')
                    $('#modal-seg-externa .modal-content').html(data.html_form);
                    $('#fuerza').select2({
                        theme: "bootstrap4",
                        allowClear: true,
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
    var GuardarFormularioSegExterna = function () {
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
                        $('#modal-seg-externa').modal('hide');
                        RecargarTabla();
                         Swal.fire({
                             position: 'center',
                             text: data['mensaje'],
                             showConfirmButton: false,
                             timer: 1500
                         });
                    }
                    else {
                        $('#modal-seg-externa .modal-content').html(data.html_form)
                        $('#fuerza').select2({
                            theme: "bootstrap4",
                            allowClear: true,
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
    $('#mostrar-modal-seg-externa').click(MostrarFormularioSegExterna)
    $("#modal-seg-externa").on("submit", ".agregar-segexterna", GuardarFormularioSegExterna)
    $("#modal-seg-externa").on("submit", ".actualizar-segexterna", GuardarFormularioSegExterna);
    $('#tabla-seg-externa tbody').on('click', '#editar-seg-externa', function () {
            comprobarSesion()
            var id = $(this).attr('id_edit_seg_ext_local');
            $.ajax({
                url: "{% url 'actualizar-seg-externa' 991 %}".replace('991',id),
                type: "get",
                dataType: "json",
                data: { 'id_local': id_local },
                success: function (data) {
                    $('#modal-seg-externa').modal('show');
                    $('#modal-seg-externa .modal-content').html(data.html_form);
                    $('#fuerza').select2({
                        //dropdownParent: $('#modal-seg-interna'),
                        theme: "bootstrap4",
                        allowClear: true,
                        placeholder: 'Seleccione',
                        language: {
                            inputTooShort: function (args) {
                                // args.minimum is the minimum required length
                                // args.input is the user-typed text
                                var t = args.minimum - args.input.length
                                return 'Por favor, introduzca ' + t + ' caracteres del apellido o dni';
                            },
                            noResults: function () {
                                return "Se se encontraron resultados";
                            },
                            searching: function () {

                                return "Buscando..";
                            }
                        },
                    });
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    alert('Error modificando datos de seguridad externa');
                }
            });
        });
    $('#tabla-seg-externa tbody').on('click', '#elimiar-seg-externa', function () {
            comprobarSesion()
            var id = $(this).attr('id_del_seg_ext_local');
            Swal.fire({
                text: "Borrar este registro",
//              icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '',
                confirmButtonText: 'Sí, borrarlo'
            }).then((result) => {
                if (result.value) {
                    $.ajax({
                        url: "{% url 'eliminar-seg-externa' 991 %}".replace('991',id),
                        type: "get",
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
                            }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            alert('Error borrando seguridad externa');
                        }
                    });
                }
            })
        });
});
