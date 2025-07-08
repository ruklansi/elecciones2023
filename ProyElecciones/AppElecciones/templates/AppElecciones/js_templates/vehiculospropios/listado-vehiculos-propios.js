var csrftoken = Cookies.get('csrftoken');
$(function () {


     {% if request.user.rol == 3 or request.user.rol == 4 or request.user.rol == 10 %}
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

//    cargar_fuerzas()

    var puesto = '';
    var fuerza = '';

    var tablaVehPropios = $('#tabla').DataTable({
        rowCallback: function (row, data, index) {
            $(row).find('td:eq(4)').css('color', 'rgb(255, 153, 0)');
            $(row).find('td:eq(6)').css('color', 'rgb(255, 153, 0)');
            if (data.puesto === "Si") {
                $(row).find("td:eq(7)").css("color", "#70dbdb");
            }
            if (data.puesto === "No") {
                $(row).find("td:eq(7)").css("color", "#ffb84d");
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
            url: "{% url 'listado-de-vehiculos-propios' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {
                d.id_distrito = id_distrito
                d.puesto = puesto
                d.fuerza = fuerza

            }
        },
        columns: [
            { data: 'distrito__distrito', orderable: false },
            { data: 'tipo_vehiculo_provisto__tipo_vehiculo_provisto', orderable: false },
            { data: 'ni_patente_matricula', orderable: false },
            { data: 'unidad__nombre', orderable: false },
            { data: 'sensor_rastreo', orderable: false },
            { data: 'troncal_', orderable: false },
            { data: 'puesto', orderable: false },
            {
                data: null,
                class: 'text-center',
                orderable: false,
            render: function (data, type, row) {
                    let buttons = '';
                    let url1='{% url "actualizar-vehiculo-propio" 99%}'.replace('99',row.id)
                    let url2='{% url "eliminar-vehiculo-propio" 99%}'.replace('99',row.id)
                    let url3='{% url "detalles-vehiculo-propio" 99%}'.replace('99',row.id)
                    if (data.puesto === 'Si'){
                        buttons = '<span id="tareas" id_vehiculo="'+row.id+'" title="Tareas donde se emplea el vehículo" class="" ><i class="fas fa-bus" style="font-size:15px;color:#70dbdb"></i></span>' + '&nbsp;&nbsp';
                    }
                    if (row.editar){
                        buttons += '<a title="Editar" href="'+ url1+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></a>'+ '&nbsp;&nbsp'
                    }
                    if (row.eliminar) {
                        buttons += '<a title="Eliminar" href="'+ url2+'" type="button" class=""><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></a> ';
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

        initComplete: function (settings, json) {
//            var vehcondestino = json.recordsTotal
//            $("#vehcondestino").html(vehcondestino)
        }
    });

    function RecargarTabla(){
        tablaVehPropios.ajax.reload(null, true);
    }

    ///////Funcion que carga los Distritos//////////
    function cargar_distritos (){
            let valores_distrito = '<option value="">Todos</option>';
            let select_distritos = $('select[id="filtro-distrito-veh-propio"]')
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
    ///////Change en Distritos para cargar subdistritos o secciones/////////
    $('select[id="filtro-distrito-veh-propio"]').on('change', function () {
            comprobarSesion();
            id_distrito = $(this).val();
            RecargarTabla();
        });

    // Modal para visualizar donde se emplea de los vehículos
    $('#tabla tbody').on('click', '#tareas', function () {
        comprobarSesion()
        let id = $(this).attr('id_vehiculo');
        $.ajax({
            url: "{% url 'detalles-vehiculo-propio' 1558 %}".replace('1558',id),
            type: "POST",
            headers: { 'X-CSRFToken': csrftoken },
            dataType: "json",
            success: function (data) {
                $('#modal-detalle-veh-propio .modal-content').html(data.resultado);
                $('#modal-detalle-veh-propio').modal('show')
            },
            error: function (jqXHR, textStatus, errorThrown) {
                       alert('Error mostrando detalle de las tareas del vehículo propio');
                   }
            });
    });

    //Carga el select de fuerza para filtrar
//    function cargar_fuerzas() {
//        var valores = '<option value="">Todos</option>';
//        var select_fuerzas = $('select[id="filtro-fuerza-para-vhpropio"]')
//        $.ajax({
//         url: "{% url 'filtros-para-vehpropios' %}",
//            type: 'POST',
//            headers: { 'X-CSRFToken': csrftoken },
//            data: {
//                'accion': 'cargar-fuerzas'
//            },
//            dataType: 'json',
//        }).done(function (data) {
//            if (!data.hasOwnProperty('error')) {
//                if (data.hay_fuerza) {
//                    //sub.show();
//                    //console.log(data)
//                    $.each(data.datos, function (key, value) {
//                        valores += '<option value="' + value.id + '">' + value.fuerza + '</option>';
//                    })
//                }
//            }
//        }).fail(function (jqXHR, textStatus, errorThrown) {
//            alert(textStatus + ':' + errorThrown)
//        }).always(function (data) {
//            select_fuerzas.html(valores);
//        });
//    };

    $('#filtro-con-sin-destino-para-vhpropio').on('change', function () {
        comprobarSesion()
        puesto = $(this).val();;
        RecargarTabla();
    });

    $('#filtro-fuerza-para-vhpropio').on('change', function () {
        comprobarSesion()
        fuerza = $(this).val();
        RecargarTabla();
    });

});

