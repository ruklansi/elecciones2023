var csrftoken = Cookies.get('csrftoken');
$(function () {
    $("#pills-contact-tab").click(function () {
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
    var tabla_novedad_local = $('#tabla-novedades-local').DataTable({
            rowCallback: function (row, data, index) {
                if (data.subsanada == 'No') {
                    //$('td', row).css('background-color', 'pink'); //Toda la fila de la tabla
                    //$('td', row).css('color', 'yellow'); //Toda la fila de la tabla
                    $(row).find('td:eq(0)').css('background-color', '#f4aba4');
                    $(row).find('td:eq(1)').css('background-color', '#f4aba4');
                    $(row).find('td:eq(2)').css('background-color', '#f4aba4');
                    $(row).find('td:eq(3)').css('background-color', '#f4aba4');
                    $(row).find('td:eq(4)').css('background-color', '#f4aba4');
                    $(row).find('td:eq(5)').css('background-color', '#f4aba4');
                    $(row).find('td:eq(0)').css('color', 'black');
                    $(row).find('td:eq(1)').css('color', 'black');
                    $(row).find('td:eq(2)').css('color', 'black');
                    $(row).find('td:eq(3)').css('color', 'black');
                    $(row).find('td:eq(4)').css('color', 'black');
                    $(row).find('td:eq(5)').css('color', 'black');
                    //$(row).find('td:eq(2)').css('color', 'yellow'); //Solo el color del texto de la celda
                    //$(row).find('td:eq(2)').css('background-color', 'yellowgreen'); // Solo el color de la celda greenyellow
                }
            },
            select: true,
            responsive: true,
            autoWidth: true,
            destroy: true,
            deferRender: true,
            processing: true,
            serverSide: true,
            lengthMenu: [[5, 10], [5, 10]],
            pageLength: 5,
            order: [[1, "asc"]],
            ajax: {
                url: "{% url 'listado-de-novedades-local' %}",
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'id_local': id_local
                },
            },
            columns: [
                {
                    data: null,
                    defaultContent: '',
                    orderable: false,
                    className: 'select-checkbox',
                },
                { data: 'fecha' },
                { data: 'tipo__tipo', orderable: false },
                { data: 'detalle', orderable: false },
                { data: 'subsanada', orderable: false },
                { data: 'medidas_adoptadas', orderable: false },
                {
                    data: null,
                    orderable: false,
                    render:  function(data, type, row){
                        let boton = '';
                        if (row.editar){
                            boton += '<span id="editar-novedad-local" id_edit_nov_local="'+row.id+'"  title="Editar" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp'
                        }
                        if (row.eliminar){
                            boton += '<span id="elimiar-novedad-local" id_del_nov_local="'+row.id+'" title="Eliminar" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
                        }
                        return boton
                    }
                }

            ],
            columnDefs: [{
                targets: 1, render: function (data) {
                    moment.locale('es');
                    //return moment(data).format('MMMM Do YYYY');moment("20111031", "YYYYMMDD").fromNow();
                    return moment(data).format('L LT');

                }
            }],
            dom: "<'row'<'col-md-3'B>><'row'<'mt-3 ml-3'l>>frtip",
            buttons: [
                {
                    text: 'Exportar en PDF',
                    extend: 'selected',
                    //className: 'btn-success',
                    className: 'mipdf',
                    action: function (e, dt, button, config) {
                        var lista_id = []
                        $.map(dt.rows({ selected: true }).data().toArray(), function (item) {
                            var dict = {};
                            dict['id'] = item.id
                            lista_id.push(dict)
                        })
                        let mi_url='{% url "generar-novedades-en-local-pdf" 0 %}'
                        window.open(window.location.origin + mi_url.replace('0', id_local) + '?lista_id=' + JSON.stringify(lista_id));
                    }
                },
            ],
            select: {
                style: 'os',
                selector: 'td:first-child'
            },
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
                },
                select: {
                    rows: {
                        _: "Seleccionadas %d filas",
                        0: "",
                        1: " %d fila seleccionada"
                    }
                }
            },

            initComplete: function (settings, json) {

            }
        });
    //Permite seleccionar todos los chec box juntos para cambiar el estado
    $(".seleccionarTodasNovedades").on("click", function (e) {
            if ($(this).is(":checked")) {
                tabla_novedad_local.rows().select()
                //var loc = locales.rows({ selected: true, page: 'current' }).data();
                //console.log(loc)

            } else {
                tabla_novedad_local.rows().deselect();
            }
        });
    function RecargarTabla() {
            comprobarSesion()
            tabla_novedad_local.ajax.reload();
        };
    var MostrarFormularioNovLocal = function () {
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
                    $('#modal-novedad-local .modal-content').html(data.html_form);
                    jQuery.datetimepicker.setLocale('es');
                    setTimeout(function () {
                        $('#id_fecha').datetimepicker({
                            //maxDate: tomorrow,
                            timepicker: true,
                            format: 'd/m/Y H:i',
                        });
                    }, 300)
                    $('#modal-novedad-local').modal('show')
                    $('#tipo').select2({
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
                    $('#subsanada').select2({
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

                }
            });
        };
    var GuardarFormularioNovLocal = function () {
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
                        $('#modal-novedad-local').modal('hide');
                        RecargarTabla();
                         Swal.fire({
                             position: 'center',
                             text: data['mensaje'],
                             showConfirmButton: false,
                             timer: 1500
                         });
                    }
                    else {
                        $('#modal-novedad-local .modal-content').html(data.html_form)
                        setTimeout(function () {
                            $('#id_fecha').datetimepicker({
                                timepicker: true,
                                format: 'd/m/Y H:i',
                            })
                        }, 300)
                        $('#tipo').select2({
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
                        $('#subsanada').select2({
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
                    }
                }
            })
            return false;
        };
    $('#mostrar-novedades-local').click(MostrarFormularioNovLocal)
    $("#modal-novedad-local").on("submit", ".agregar-novedad-local", GuardarFormularioNovLocal)
    $("#modal-novedad-local").on("submit", ".actualizar-novedad-local", GuardarFormularioNovLocal);
    $('#tabla-novedades-local tbody').on('click', '#editar-novedad-local', function () {
            comprobarSesion()
            var id = $(this).attr('id_edit_nov_local');
            //console.log(id)
            $.ajax({
                url: "{% url 'actualizar-novedad-local' 991 %}".replace('991',id),
                type: "get",
                dataType: "json",
                data: { 'id_local': id_local },
                success: function (data) {
                    $('#modal-novedad-local').modal('show');
                    $('#modal-novedad-local .modal-content').html(data.html_form);
                    jQuery.datetimepicker.setLocale('es');
                    setTimeout(function () {
                        $('#id_fecha').datetimepicker({
                            timepicker: true,
                            format: 'd/m/Y H:i',
                        });
                    }, 300)
                    $('#tipo').select2({
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
                    $('#subsanada').select2({
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
                    alert('Error modificando datos de novedades en el local');
                }
            });
        });
    $('#tabla-novedades-local tbody').on('click', '#elimiar-novedad-local', function () {
            comprobarSesion()
            var id = $(this).attr('id_del_nov_local');
            Swal.fire({
                text: "Borrar este registro",
//                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: 'Cancelar',
                confirmButtonText: 'Sí, borrarlo'
            }).then((result) => {
                if (result.value) {
                    $.ajax({
                        url: "{% url 'eliminar-novedad-local' 991 %}".replace('991',id),
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
