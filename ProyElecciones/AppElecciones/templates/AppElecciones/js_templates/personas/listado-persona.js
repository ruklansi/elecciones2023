var csrftoken = Cookies.get('csrftoken');
$(function () {
    {% if request.user.rol == 3 or request.user.rol == 4 or request.user.rol == 9 or request.user.rol == 10 %}
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

    cargar_fuerzas()

    var puesto = '';
    var fuerza = '';

    var tablaPersonas = $('#tabla').DataTable({
        rowCallback: function (row, data, index) {
            if (data.es_conductor && !data.tiene_cargo) {
                $(row)
                    .find("td:eq(6)")
                    .text('Conductor')
                    .css("color", "#ffb84d");
            }
            if (data.es_conductor && data.tiene_cargo) {
                $(row)
                    .find("td:eq(6)")
                    .html('<span>Conductor </span><br>' + data.puesto)
                    .css("color", "#ffb84d");
            }

        },
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 10], [5, 10]],
        pageLength: 5,
        order: [[0, "asc"]],
        ajax: {
            url: "{% url 'listado-de-personas' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {
                d.id_distrito = id_distrito
                d.fuerza = fuerza
                d.puesto = puesto
            },
//            dataSrc: function(data){
//                $('#mostrar_personal').html(data.pepe)
//                return data.data
//            },
        },
        dom: '<"titulo">lfrtip',
        columns: [
            { data: 'distrito__distrito', orderable: false },
            { data: 'validado_por', orderable: false },
            { data: 'grado__grado', orderable: false },
            { data: 'nombre', orderable: false },
            { data: 'apellido', orderable: true },
            { data: 'dni', orderable: true },
            { data: 'fuerza__fuerza', orderable: false },
            { data: 'puesto', orderable: false},
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    let buttons = '';
                    var url1='{% url "actualizar-persona" 99%}'.replace('99',row.id)
                    var url2='{% url "eliminar-persona" 99%}'.replace('99',row.id)

                    if (data.es_conductor){
                        buttons += '<span id="comisiones" id_persona="'+row.id+'" title="Detalle de las tareas como conductor" class="" ><i class="fas fa-bus" style="font-size:15px;color:#70dbdb"></i></span>' + '&nbsp;&nbsp';
                    }
                    if (row.editar) {

                        buttons += '<a title="Editar" href="'+ url1+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></a> ' + '&nbsp;&nbsp';
                    }
                    if (row.eliminar) {
                         if ((row.puesto === 'Sin puesto') && (!row.es_conductor)){
                            buttons += '<span id="resetear" id_persona_="'+row.id+'" persona="'+row.grado__grado+' '+row.nombre+' '+row.apellido+' DNI: '+row.dni+'" title="Volver al estado Sin validar" class="" ><i class="fas fa-solid fa-person-walking-arrow-loop-left" style="font-size:16px;color:#70dbdb"></i></span>' + '&nbsp;&nbsp';
                        }
                        buttons += '<a title="Eliminar" href="'+ url2+'" type="button" class=""><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></a>';
                    }
                    return buttons;
                }
            }
        ],
//        drawCallback: function(settings) {
//            $.LoadingOverlay("hide");
//        },
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

    function RecargarTabla() {
        comprobarSesion()
        tablaPersonas.ajax.reload(null, true);
    };

    // Volver al estado de no validado a la persona via ajax
    $('#tabla tbody').on('click', '#resetear', function () {
        comprobarSesion()
        let id_persona = $(this).attr('id_persona_');
        let persona = $(this).attr('persona');

        Swal.fire({
                text: 'Confirma volver al estado de no validado al '+ persona,
                showCancelButton: true,
                confirmButtonColor: '',
                cancelButtonColor: '',
                confirmButtonText: 'Confirmar'
            }).then((result) => {
                if (result.value) {
                    $.ajax({
                        url: "{% url 'validar_informacion' %}",
                        type: "POST",
                        headers: { 'X-CSRFToken': csrftoken },
                        dataType: "json",
                        data: {'accion':'resetear_personal', 'id_persona': id_persona},
//                          beforeSend: function () {
//                            $.LoadingOverlay("show",
//                            {
//                                background      : "rgba(0, 0, 0, 0.5)",
//                                imageAnimation  : "1.5s fadein",
//                                imageColor      : "#ffcc00",
//                                //text            : "Registrando % de voto...."
//                            }
//                            );
//                        },
                        success: function (data) {
                            if (data.reseteado) {
                                RecargarTabla();
//                                Swal.fire({
//                                  position: 'center',
//                                  text: data['mensaje'],
//                                  showConfirmButton: true,
//                                });
                            }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                                alert('Error reseteando la persona a no validada');
                        }
                    });
                }
            })
    });


    function cargar_fuerzas() {
        var valores_fuerzas = '<option value="">Todos</option>';
        var select_fuerzas = $('select[id="filtro-fuerza-para-personal"]')
        $.ajax({
            url: "{% url 'filtros-para-personas' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'accion': 'cargar-fuerzas-pers-validado'
            },
            dataType: 'json',
        }).done(function (data) {
            if (!data.hasOwnProperty('error')) {
                if (data.hay_fuerza) {
                    $.each(data.datos, function (key, value) {
                        valores_fuerzas += '<option value="' + value.id + '">' + value.fuerza + '</option>';
                    })
                }
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(textStatus + ':' + errorThrown)
        }).always(function (data) {
            select_fuerzas.html(valores_fuerzas);
        });
    }

    ///////Funcion que carga los Distritos//////////
    function cargar_distritos (){
            let valores_distrito = '<option value="">Todos</option>';
            let select_distritos = $('select[id="filtro-distrito-persona-validada"]')
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
    $('select[id="filtro-distrito-persona-validada"]').on('change', function () {
            comprobarSesion();
            id_distrito = $(this).val();
            RecargarTabla();
        });

    $('#filtro-con-sin-puesto-para-personal').on('change', function () {
        comprobarSesion()
        let valor = $(this).val();
        puesto = valor
        RecargarTabla();
    });

    $('#filtro-fuerza-para-personal').on('change', function () {
        comprobarSesion()
        fuerza = $(this).val();
        RecargarTabla();
    });

    $("#buscar_persona_dni").submit(function() {
        comprobarSesion()
        let url = $(this).attr('data-url')
        let dni = $("#id_dni").val();
        $.ajax({
                url: url,
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'dni': dni
                },
                dataType: 'json',
            }).done(function (resultado) {
                if (!resultado.hasOwnProperty('error')) {
                     if (!resultado.hay_error) {
                        $("#id_dni").focus();
                         Swal.fire({
                                html: '<div class="form-row"><div class="form-group col-md-4 mb-0 d-flex p-2"><div class="control-group "><span class="tx-black ">Grado: </span></div></div>'+
                                      '<div class="form-group col-md-8 mb-0 d-flex p-2"><div class="control-group">'+resultado.datos[0].grado__grado+'</div></div></div>'+
                                      '<div class="form-row"><div class="form-group col-md-4 mb-0 d-flex p-2"><div class="control-group"><span class="tx-black">Nombre: </span></div></div>'+
                                      '<div class="form-group col-md-8 mb-0 d-flex p-2"><div class="control-group">'+resultado.datos[0].nombre+'</div></div></div>'+
                                      '<div class="form-row"><div class="form-group col-md-4 mb-0 d-flex p-2"><div class="control-group"><span class="tx-black">Apellido: </span></div></div>'+
                                      '<div class="form-group col-md-8 mb-0 d-flex p-2"><div class="control-group">'+resultado.datos[0].apellido+'</div></div></div>'+
                                      '<div class="form-row"><div class="form-group col-md-4 mb-0 d-flex p-2"><div class="control-group"><span class="tx-black">DNI: </span></div></div>'+
                                      '<div class="form-group col-md-8 mb-0 d-flex p-2"><div class="control-group">'+resultado.datos[0].dni+'</div></div></div>'+
                                      '<div class="form-row"><div class="form-group col-md-4 mb-0 d-flex p-2"><div class="control-group"><span class="tx-black">Puesto: </span></div></div>'+
                                      '<div class="form-group col-md-8 mb-0 d-flex p-2"><div class="control-group">'+resultado.datos[0].puesto+'</div></div></div>',
                            })
                     }
                     else {
                          $("#id_dni").focus();
                          Swal.fire({
                            text: resultado.datos
                          })
                     }
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ':' + errorThrown)
            }).always(function (resultado) {

            });
        return false;
    });

     // Modal para visualizar donde se empleó este conductor
    $('#tabla tbody').on('click', '#comisiones', function () {
        comprobarSesion()
        let id = $(this).attr('id_persona');
        $.ajax({
            url: "{% url 'detalles-persona-como-conductor' 1555 %}".replace('1555',id),
            type: "POST",
            headers: { 'X-CSRFToken': csrftoken },
            dataType: "json",
            success: function (data) {
                $('#modal-detalle-persona-como-conductor .modal-content').html(data.resultado);
                $('#modal-detalle-persona-como-conductor').modal('show')
            },
            error: function (jqXHR, textStatus, errorThrown) {
                       alert('Error mostrando detalle de la persona como conductor');
                   }
            });
    });

});

