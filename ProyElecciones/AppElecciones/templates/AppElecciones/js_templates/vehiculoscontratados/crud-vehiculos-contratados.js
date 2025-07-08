var csrftoken = Cookies.get('csrftoken');
$(function () {
     {% if request.user.rol == 3  or request.user.rol == 4 or request.user.rol == 10 %}
        $('#dis').hide()
     {% endif %}
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

    var id_distrito = '';

    cargar_distritos();

    var puesto = '';

    var tablaVehContratados = $('#tabla').DataTable({
         rowCallback: function (row, data, index) {
            if (data.puesto === "Si") {
                $(row).find("td:eq(5)").css("color", "#70dbdb");
            }
            if (data.puesto === "No") {
                $(row).find("td:eq(5)").css("color", "#ffb84d");
            }
         },
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 10], [5, 10]],
        order: [[0, "asc"]],
        ajax: {
            url: "{% url 'listado-vehiculos-contratados' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {
                d.id_distrito = id_distrito
                d.puesto = puesto
            }
        },
        columns: [
            { data: 'distrito__distrito', orderable: false },
            { data: 'tipo_vehiculo_contratado__tipo_vehiculo_civil', orderable: false },
            { data: 'patente_matricula', orderable: false },
            { data: 'sensor_rastreo', orderable: false },
            { data: 'troncal_', orderable: false },
            { data: 'puesto', orderable: false },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    let buttons = '';
                    if (data.puesto === 'Si'){
                        buttons = '<span id="tareas" id_vehiculo="'+row.id+'" title="Tareas donde se emplea el vehículo" class="" ><i class="fas fa-bus" style="font-size:15px;color:#70dbdb"></i></span>' + '&nbsp;&nbsp';
                    }
                    if (row.editar){
                        buttons += '<span id="editar-veh-contratado" title="Editar" id_veh_cont_edit="'+row.id+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp';
                    }
                    if (row.eliminar){
                        buttons += '<span id="eliminar-veh-contratado" id_veh_cont_del="'+row.id+'" veh_contratado="'+row.tipo_vehiculo_contratado__tipo_vehiculo_civil+'" title="Eliminar" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span> ' + '&nbsp;&nbsp';
                    }
                    return buttons;
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

        initComplete: function (settings, json) {}
    });

    function RecargarTabla(){
        tablaVehContratados.ajax.reload(null, true);
    }

    // Modal para visualizar donde se emplea de los vehículos
    $('#tabla tbody').on('click', '#tareas', function () {
        comprobarSesion()
        let id = $(this).attr('id_vehiculo');
        $.ajax({
            url: "{% url 'detalles-vehiculo-contratado' 1558 %}".replace('1558',id),
            type: "POST",
            headers: { 'X-CSRFToken': csrftoken },
            dataType: "json",
            success: function (data) {
                $('#modal-detalle-veh-contratado .modal-content').html(data.resultado);
                $('#modal-detalle-veh-contratado').modal('show')
            },
            error: function (jqXHR, textStatus, errorThrown) {
                       alert('Error mostrando detalle de las tareas del vehículo propio');
                   }
            });
    });

     $('#filtro-con-sin-destino-para-vhcontratado').on('change', function () {
        comprobarSesion()
        puesto = $(this).val();;
        RecargarTabla();
    });

    ///////Funcion que carga los Distritos//////////
    function cargar_distritos (){
            let valores_distrito = '<option value="">Todos</option>';
            let select_distritos = $('select[id="filtro-distrito-veh-contratado"]')
            $.ajax({
                url: "{% url 'filtro-para-organizaciones' %}",
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'cargar-distritos'
                },
                dataType: 'json',
            }).done(function (respuesta) {
                if (!respuesta.hasOwnProperty('error')) {
                    $.each(respuesta.datos, function (key, value) {
                        valores_distrito += '<option value="' + value.id + '">' + value.distrito + '</option>';
                    })
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ':' + errorThrown)
            }).always(function (respuesta) {
              select_distritos.html(valores_distrito);
            });
        }
    ///////Change en Distritos para filtrar/////////
    $('select[id="filtro-distrito-veh-contratado"]').on('change', function () {
            comprobarSesion();
            id_distrito = $(this).val();
            RecargarTabla();
        });

    // CRUD de vehiculos contratados
    var MostrarFormularioVehContratado = function () {
        var boton = $(this);
        $.ajax({
            url: boton.attr("data-url"),
            type: "get",
            dataType: "json",
            success: function (data) {
             setTimeout(function () {
                 $('#tipo_veh_cont').select2({
                    theme: "bootstrap4",
                    language: 'es',
                    placeholder: 'Seleccione',
                    allowClear: true,
                });


             },200);
            //Respetar este orden para que funcione select2
            $('#modal-veh-contratado .modal-content').html(data.html_form);
            $('#modal-veh-contratado').modal('show')
            }
        });
    };
    var GuardarFormularioVehContratado = function () {
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('data-url'),
            data: form.serialize(),
            dataType: "json",
            headers: { 'X-CSRFToken': csrftoken },
            success: function (data) {
                if (data.form_es_valido) {
                    $('#modal-veh-contratado').modal('hide');
                    RecargarTabla();
                     Swal.fire({
                         position: 'center',
                         text: data['mensaje'],
                         showConfirmButton: false,
                         timer: 1500
                     });
                }
                else {
                     setTimeout(function () {
                         $('#tipo_veh_cont').select2({
                            theme: "bootstrap4",
                            language: 'es',
                            placeholder: 'Seleccione',
                            allowClear: true,
                        });

                     },200);

                    $('#modal-veh-contratado .modal-content').html(data.html_form);
                }
            }
        })
        return false;
    };
    $('#mostrar-modal-veh-contratado').click(MostrarFormularioVehContratado)
    $("#modal-veh-contratado").on("submit", ".crear-veh-contratado", GuardarFormularioVehContratado)
    $("#modal-veh-contratado").on("submit", ".actualizar-veh-contratado", GuardarFormularioVehContratado)
    $('#tabla tbody').on('click', '#editar-veh-contratado', function () {
        comprobarSesion()
        var id = $(this).attr('id_veh_cont_edit');
        $.ajax({
            url: "{% url 'actualizar-veh-contratado' 15534 %}".replace('15534',id),
            type: "get",
            dataType: "json",
            success: function (data) {
                setTimeout(function () {
                 $('#tipo_veh_cont').select2({
                    theme: "bootstrap4",
                    language: 'es',
                    placeholder: 'Seleccione',
                    allowClear: true,
                });

             },200);
                $('#modal-veh-contratado .modal-content').html(data.html_form);
                $('#modal-veh-contratado').modal('show')
            },
        });
    });
    $('#tabla tbody').on('click', '#eliminar-veh-contratado', function () {
        comprobarSesion()
        let id = $(this).attr('id_veh_cont_del');
        let veh_contratado = $(this).attr('veh_contratado');
        setTimeout(function() {
            Swal.fire({
                text: "Borrar "+veh_contratado+ " ?",
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '',
                confirmButtonText: 'Sí, borrarlo'
            }).then((result) => {
                if (result.value) {
                    $.ajax({
                        url: "{% url 'eliminar-veh-contratado' 1558 %}".replace('1558',id),
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
                            if (!data.borrado){
                                    Swal.fire({
                                        position: 'center',
                                        text: data['mierror'],
                                        showConfirmButton: false,
                                        timer: 7000
                                      })
                                }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                                alert('Error eliminando vehículo contratado');
                        }
                    });
                }
            })
        },200)
    });
    // Fin CRUD de vehículos contratados

});

