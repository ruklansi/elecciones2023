var csrftoken = Cookies.get('csrftoken');
$(function () {

     //Si tiene el rol de Distrito y no tiene subdistrito oculto el desplegable del filtro de subdistrito
      {% if request.user.rol == 3 and tiene_subdistrito == 'no' %}
        $('#sub').hide()
      {% endif %}
       //Si tiene el rol de Subdistrito oculto el desplegable del filtro de distrito
      {% if request.user.rol == 4  %}
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
    var estado = '';

    cargar_tipo_de_causa_para_mod();
    cargar_filtro_por_estados()

    var id_distrito = '';
    var id_subdistrito = '';
    var id_seccion ='';
    var id_circuito = '';
    var id_local = '';
    var tipo_mesa = '';

    cargar_distritos();


    var tabla_mesas_control_inicio = $('#tabla').DataTable({
        rowCallback: function (row, data, index) {
            if (data.estado__estado === 'HABILITADA') {
                $(row).find('td:eq(7)').css('color', '#99ff99');
            }
            if (data.estado__estado === 'DESHABILITADA') {
                $(row).find('td:eq(7)').css('color', '#ff8080');
                $(row).find('td:eq(8)').css('color', '#ff8080');
            }
            if (data.estado__estado === 'FINALIZADA') {
                $(row).find('td:eq(7)').css('color', '#1ac6ff');
            }
            if (data.estado__estado === 'NO INICIADA') {
                $(row).find('td:eq(7)').css('color', '#ff8080');
                $(row).find('td:eq(8)').css('color', '#ff8080');
            }

        },
        //select: true,
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 10, 20, 50], [5, 10, 20, 50]],
        pageLength: 5,
        order: [[1, "asc"]],
        ajax: {
            url: "{% url 'listado-de-mesas-en-local-para-iniciar' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {
                d.id_distrito = id_distrito
                d.id_subdistrito = id_subdistrito
                d.id_seccion = id_seccion
                d.id_circuito = id_circuito
                d.id_local = id_local
                d.tipo_mesa = tipo_mesa
                d.estado = estado
            },
        },
        columns: [
            {
                data: null,
                defaultContent: '',
                orderable: false,
                className: 'select-checkbox',
            },
            { data: 'mesas', orderable: true, search: true },
            {
                data: 'local__nombre',
                orderable: true,
                search: true,

                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    let url15='{% url "detalles-local" 959 %}'.replace('959',oData.local__id)
                    $(nTd).html("<a href='"+ url15+ "'>" + sData + "</a>");

                },
                orderable: false, search: true
            },
            { data: 'local__circuito__seccion__distrito__distrito', orderable: false },
            { data: 'local__circuito__seccion__subdistrito__subdistrito', orderable: false },
            { data: 'local__circuito__seccion__seccion', orderable: false },
            { data: 'local__circuito__circuito', orderable: false },
            { data: 'estado__estado', orderable: false },
            { data: 'estado__causa', orderable: false },

        ],
        dom: "<'row'<'col-md-3'B>><'row'<'mt-3 ml-3'l>>frtip",
        buttons: [
            {
                text: 'Ejecutar',
                extend: 'selected',
                //className: 'btn-success',
                className: 'estilo_del_boton_ejecutar',

                action: function (e, dt, button, config) {

                    var lista_id = []
                    $.map(dt.rows({ selected: true }).data().toArray(), function (item) {
                        var dict = {};
                        dict['id'] = item.id
                        lista_id.push(dict)

                    })
                    // lista_id es una lista con diccionarios de los id: [{'id': xxxx}]
                    // Debe ir así entonces en el django los proceso con un json.loads(request.POST['lista_id'])
                    // y obtengo un listado para luego con un for obtener el id  lista_id = [x['id'] for x in lista]
                    // console.log(lista_id)
                    var parametros = {
                        'accion': 'ejecutar_accion_en_mesas',
                        'tipo_causa_mesas': tipo_causa_mesas,
                        'lista_id': JSON.stringify(lista_id)
                    }


                    if (!tipo_causa_mesas) {
                        Swal.fire({
                            icon: 'warning',
                            title: 'Debe seleccionar una Acción',
                        })
                    } else {
                        $.ajax({
                            url: "{% url 'uso-ajax-mesas' %}",
                            type: "post",
                            headers: { 'X-CSRFToken': csrftoken },
                            dataType: "json",
                            data: parametros,
                            success: function (data) {
                                //cargar_tipo_de_causa_para_mod();
                                tabla_mesas_control_inicio.ajax.reload(null, false);
                            },
                            error: function (jqXHR, textStatus, errorThrown) {
                                //alert(textStatus + ': ' + errorThrown + ': ' + jqXHR.responseText);
                                var errorMessage = jqXHR.status + ': ' + jqXHR.statusText
                                alert('Error - ' + errorMessage + ' - ' + jqXHR.responseText);
                            }
                        });
                        return false;
                    }
                }
            },
        ],
        select: {
            style: 'os',
            selector: 'td:first-child'
        },
        language: {
            decimal: "",
            emptyTable: "Sin mesas que listar",
            info: "Mostrando _START_ a _END_ de _TOTAL_ Mesas",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
            infoFiltered: "",
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
        initComplete: function (settings, json) {}

    });

     {% if request.user.rol == 2 %}
//        circuitos.column(0).visible(false); // or true, if you want to show it
        tabla_mesas_control_inicio.buttons().container().hide()
        $("#accion").hide()
    {% endif %}


    function RecargarTabla() {
        comprobarSesion()
        tabla_mesas_control_inicio.ajax.reload(null, true);
    };

    //Permite seleccionar todos los chec box juntos para cambiar el estado
    $(".seleccionarTodasLasMesas").on("click", function (e) {
        if ($(this).is(":checked")) {
            tabla_mesas_control_inicio.rows().select()
            //var loc = locales.rows({ selected: true, page: 'current' }).data();
            //console.log(loc)

        } else {
            tabla_mesas_control_inicio.rows().deselect();
        }
    });

    function cargar_tipo_de_causa_para_mod() {
        var valores = '<option value="">Seleccione</option>';
        var select_tipo_causa = $('select[id="filtro-tipo-causa-no-iniciada"]')
        $.ajax({
            url: "{% url 'cargar-causas-noinicio-para-filtro' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            dataType: 'json',
        }).done(function (data) {

            if (!data.hasOwnProperty('error')) {
                $.each(data, function (key, value) {
                    if (value.causa == '--') {
                        value.causa = '';
                    }
                    valores += '<option value="' + value.id + '">' + value.estado + ' ' + value.causa + '</option>';
                })
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(textStatus + ':' + errorThrown)
        }).always(function (data) {
            select_tipo_causa.html(valores);
        });
    }

    function cargar_filtro_por_estados(){
        var valores = '<option value="">Todas</option>';
        var select_tipo_causa_filtro = $('select[id="filtro-por-estado-mesas"]')
        $.ajax({
            url: "{% url 'cargar-causas-noinicio-para-filtro' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            dataType: 'json',
        }).done(function (data) {
            if (!data.hasOwnProperty('error')) {
                $.each(data, function (key, value) {
                     if (value.causa === '--') {
                        value.causa = '';
                    }
                    valores += '<option value="' + value.id + '">' + value.estado + ' ' + value.causa + '</option>';
                })
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(textStatus + ':' + errorThrown)
        }).always(function (data) {
            select_tipo_causa_filtro.html(valores);
        });
    };

    $('#filtro-tipo-causa-no-iniciada').on('change', function () {
        comprobarSesion()
        let id = $(this).val();
        tipo_causa_mesas = id;
        //tabla_mesas_control_inicio.ajax.reload(null, true);
    });

    $('#filtro-locales-para-mesas').on('change', function () {
        comprobarSesion()
        let id = $(this).val();
        id_local_ = id;
        tabla_mesas_control_inicio.ajax.reload(null, true);
    });

    $('#filtro-por-estado-mesas').on('change', function () {
        comprobarSesion()
        estado = $(this).val();
        RecargarTabla();
    });

      $('#filtro-por-mesas').on('change', function () {
        comprobarSesion()
        tipo_mesa = $(this).val();
        RecargarTabla();
    });




    ///////Funcion que carga los Distritos//////////
    function cargar_distritos (){

            var select_subdistritos = '';
            var select_secciones = '';
            var select_circuitos = '';
            var select_locales = '';

            var opciones_subdistritos = '';
            var opciones_secciones = '';
            var opciones_circuitos = '';
            var opciones_locales = '';

            let valores_distrito = '<option value="">Todos</option>';
            let select_distritos = $('select[id="filtro-distrito-controlmesas"]')
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

    ///////Desplegable de Subdistritos - se carga solo para un usuario logueado como Subdistrito//////////
            let valores_sub_distrito = '<option value="">Todos</option>';
            let select_sub_distritos_para_mapa = $('select[id="filtro-subdistrito-controlmesas"]')
            $.ajax({
                url: '{% url 'filtro-para-organizaciones' %}',
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'cargar-subdistritos'
                },
                dataType: 'json',
            }).done(function (respuesta) {
                if (!respuesta.hasOwnProperty('error')) {

                    $.each(respuesta.datos, function (key, value) {

                        valores_sub_distrito += '<option value="' + value.id + '">' + value.subdistrito + '</option>';
                    })
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ':' + errorThrown)
            }).always(function (respuesta) {
              select_sub_distritos_para_mapa.html(valores_sub_distrito);
            });
        ///////Fin desplegable de Subdistritos/////////

    ///////Change en Distritos para cargar subdistritos o secciones/////////
    $('select[id="filtro-distrito-controlmesas"]').on('change', function () {
            var id = $(this).val();
            id_distrito = $(this).val();
            id_subdistrito = '';
            id_seccion ='';
            id_circuito = '';
            id_local = '';

            select_subdistritos = $('select[id="filtro-subdistrito-controlmesas"]')
            select_secciones = $('select[id="filtro-seccion-controlmesas"]')
            select_circuitos = $('select[id="filtro-circuito-controlmesas"]')
            select_locales = $('select[id="filtro-locales-controlmesas "]')

            opciones_subdistritos = '<option value="">Todos</option>';
            opciones_secciones = '<option value="">Todas</option>';
            opciones_circuitos = '<option value="">Todos</option>';
            opciones_locales = '<option value="">Todos</option>';

            select_subdistritos.html(opciones_subdistritos)
            select_secciones.html(opciones_secciones)
            select_circuitos.html(opciones_circuitos)
            select_locales.html(opciones_locales)

            RecargarTabla();

            if (id === '') {
                select_subdistritos.html(opciones_subdistritos);
                return false;
            }
            $.ajax({
                url: "{% url 'filtro-para-organizaciones' %}",
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'filtrar-subdistritos',
                    'id': id
                },
                dataType: 'json',
            }).done(function (respuesta) {
//                console.log(respuesta)
                if (!respuesta.hasOwnProperty('error')) {
                    if (respuesta.hay_subdistrito) {
                        $('#sub').show();
                        $('#filtro-subdistrito-controlmesas').show();
                        $.each(respuesta.datos, function (key, value) {
                            opciones_subdistritos += '<option value="' + value.id + '">' + value.subdistrito + '</option>';
                        })
                    }
                    if (!respuesta.hay_subdistrito) {
                        $('#sub').hide();
                        $('#filtro-subdistrito-controlmesas').hide();
                        $.each(respuesta.datos, function (key, value) {
                            opciones_secciones += '<option value="' + value.id + '">' + value.seccion + '</option>';
                        })
                    }
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ':' + errorThrown)
            }).always(function (respuesta) {
                select_subdistritos.html(opciones_subdistritos);
                select_secciones.html(opciones_secciones);
            })
        });

    //////Change en Subdistritos para cargar secciones/////////
    $('select[id="filtro-subdistrito-controlmesas"]').on('change', function () {
            var id = $(this).val();
            id_subdistrito = $(this).val();
            id_seccion ='';
            id_circuito = '';
            id_local = '';

            select_secciones = $('select[id="filtro-seccion-controlmesas"]')
            select_circuitos = $('select[id="filtro-circuito-controlmesas"]')
            select_locales = $('select[id="filtro-locales-controlmesas"]')

            opciones_secciones = '<option value="">Todas</option>';
            opciones_circuitos = '<option value="">Todos</option>';
            opciones_locales = '<option value="">Todos</option>';

            select_circuitos.html(opciones_circuitos)
            select_locales.html(opciones_locales)

            RecargarTabla();

            if (id === '') {
                select_secciones.html(opciones_secciones);
                return false;
            }
            $.ajax({
                url: "{% url 'filtro-para-organizaciones' %}",
                type: 'POST',
                 headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'filtrar-seccion',
                    'id': id
                },
                dataType: 'json',
            }).done(function (respuesta) {
                if (!respuesta.hasOwnProperty('error')) {
                    //console.log(respuesta)
                    if (respuesta.hay_secciones) {
                        //console.log(respuesta.datos)
                        $.each(respuesta.datos, function (key, value) {
                            opciones_secciones += '<option value="' + value.id + '">' + value.seccion + '</option>';
                        })
                    }
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ':' + errorThrown)
            }).always(function (respuesta) {
                //console.log(opciones_sec_en_circuito)
                select_secciones.html(opciones_secciones);
            })
        });

    //////Change en Secciones para cargar circuitos/////////
    $('select[id="filtro-seccion-controlmesas"]').on('change', function () {
            var id = $(this).val();
            id_seccion = $(this).val();
            id_circuito = '';
            id_local = '';


            select_circuitos = $('select[id="filtro-circuito-controlmesas"]')
            select_locales = $('select[id="filtro-locales-controlmesas"]')

            opciones_circuitos = '<option value="">Todos</option>';
            opciones_locales = '<option value="">Todos</option>';

            RecargarTabla();
            if (id === '') {
                select_circuitos.html(opciones_circuitos);
                return false;
            }
            $.ajax({
                url: "{% url 'filtro-para-organizaciones' %}",
                type: 'POST',
                 headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'filtrar-circuito',
                    'id': id
                },
                dataType: 'json',
            }).done(function (respuesta) {
                if (!respuesta.hasOwnProperty('error')) {
                    //console.log(respuesta)

                    if (respuesta.hay_circuitos) {
                        //console.log(respuesta.datos)
                        $.each(respuesta.datos, function (key, value) {
                            opciones_circuitos += '<option value="' + value.id + '">' + value.circuito + '</option>';
                        })
                    }
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ':' + errorThrown)
            }).always(function (respuesta) {
                //console.log(opciones_sec_en_circuito)
                select_circuitos.html(opciones_circuitos);
            })
        });

    $('select[id="filtro-circuito-controlmesas"]').on('change', function (){
            var id = $(this).val();
            id_circuito = $(this).val();
            id_local = '';


            select_locales = $('select[id="filtro-locales-controlmesas"]')

            opciones_locales = '<option value="">Todos</option>';

            RecargarTabla();

            if (id === '') {
                select_locales.html(opciones_locales);
                return false;
            }
            $.ajax({
                url: "{% url 'filtro-para-organizaciones' %}",
                type: 'POST',
                 headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'filtrar-local',
                    'id': id
                },
                dataType: 'json',
            }).done(function (respuesta) {

                if (!respuesta.hasOwnProperty('error')) {
                    if (respuesta.hay_locales) {
                        $.each(respuesta.datos, function (key, value) {
                            opciones_locales += '<option value="' + value.id + '">' + value.local + '</option>';
                        })
                    }
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ':' + errorThrown)
            }).always(function (respuesta) {
//                console.log(opciones_locales)
                select_locales.html(opciones_locales);
            })
        });

    $('select[id="filtro-locales-controlmesas"]').on('change', function (){
            id_local = $(this).val();
            RecargarTabla();

        });



});
