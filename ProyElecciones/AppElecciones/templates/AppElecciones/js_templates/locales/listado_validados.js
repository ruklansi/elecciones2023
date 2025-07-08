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

    var id_distrito_en_local_ = '';
    var id_subdistrito_en_local_ = '';
    var id_seccion_en_local_ ='';
    var id_circuito_en_local_ = '';

    cargar_distritos();

    var tipo_causa_local = '';
    var estado_local = '';
    var mesas_ = '';
    var seg_int_ = '';
    var seg_ext = '';
    var horario_por_votos = '';
    var porcentaje_votos = '';


    cargar_tipo_de_causa_para_mod_local();
    cargar_hora_voto();

    var tabla_locales_validados = $('#tabla').DataTable({
        rowCallback: function (row, data, index) {
            if (data.estado__estado === 'HABILITADO') {
                $(row).find('td:eq(11)').css('color', '#99ff99');
            }
            if (data.estado__estado === 'INICIADO') {
                $(row).find('td:eq(11)').css('color', '#99ff99');
            }
            if (data.estado__estado === 'DESHABILITADO') {
                $(row).find('td:eq(11)').css('color', '#ff8080');
            }
            if (data.estado__causa !== '--') {
                $(row).find('td:eq(12)').css('color', '#ff8080');
            }
            if (data.estado__estado === 'FINALIZADO') {
                $(row).find('td:eq(11)').css('color', '#1ac6ff');
            }
            if (data.porcentaje) {
                $(row).find('td:eq(10)').css('color', 'rgb(255, 153, 0)');
            }

        },
        select: true,
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
            url: '{% url "listado-de-locales-validados" %}',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {
                d.id_distrito_local = id_distrito_en_local_
                d.id_subdistrito_local = id_subdistrito_en_local_
                d.id_seccion_local = id_seccion_en_local_
                d.id_circuito_local = id_circuito_en_local_

                d.estado_local = estado_local
                d.mesas = mesas_
                d.seg_int = seg_int_
                d.seg_ext = seg_ext
            }
        },
        columns: [
            {
                data: null,
                defaultContent: '',
                orderable: false,
                className: 'select-checkbox',
            },
            {
                data: 'nombre',
                orderable: false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    let url='{% url "detalles-local" 99 %}'.replace('99',oData.id)
                    $(nTd).html("<a href='"+ url+ "' data-toggle='tooltip' title='Accede a local'    >" + sData + " </a>");
                },
            },
            { data: 'circuito__seccion__distrito__distrito', orderable: false },
            { data: 'circuito__seccion__subdistrito__subdistrito', orderable: false },
            { data: 'circuito__seccion__seccion', orderable: false },
            { data: 'circuito__circuito', orderable: false },
            { data: 'cant_mesas', orderable: false },
            { data: 'cant_nov', orderable: false },
            { data: 'cant_seg_ext', orderable: false },
            { data: 'cant_seg_int', orderable: false },
            { data: 'porcentaje', orderable: false },
            { data: 'estado__estado', orderable: false },
            { data: 'estado__causa', orderable: false },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    let buttons = '';
                    var url1='{% url "detalles-local" 99 %}'.replace('99',row.id)
                    var url3='{% url "actualizar-local" 99 %}'.replace('99',row.id)
                    let tipo_local;
                    let url4 ='{% url "eliminar-local" 999 666 %}'.replace('999', row.id, '666', tipo_local)
                    buttons += '<a title="Resumen, seguridad, novedades y mesas" href="'+url1 + '" class="raul" ><i class="fas fa-address-card" style="font-size:15px;color:goldenrod"></i></a> ' + '&nbsp;&nbsp';
                    if (row.editar){
                        buttons += '<a title="Editar" href="'+url3+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></a> ' + '&nbsp;&nbsp';
                    }
                    if (row.eliminar){
                        buttons += '<a title="Eliminar" href="'+url4+'" type="button" class=""><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></a>';
                    }
                    return buttons;
                }
            },
        ],
        dom: "<'row'<'col-md-4'B>><'row'<'mt-4 ml-4'l>>frtip",

        buttons: [
            {
                text: 'Ejecutar',
                extend: 'selected',
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
                        'accion': 'ejecutar_accion',
                        'tipo_causa_local': tipo_causa_local,
                        'lista_id': JSON.stringify(lista_id),
                        'horario_por_votos': horario_por_votos
                    }


                    if (!tipo_causa_local) {
                    
                        Swal.fire({
//                            icon: 'warning',
                            text: 'Debe seleccionar una Causa',
                        })

                    } else {
                        $.ajax({
                            url: '{% url "uso-ajax" %}',
                            type: "post",
                            headers: { 'X-CSRFToken': csrftoken },
                            dataType: "json",
                            data: parametros,
                            success: function (data) {
                                //cargar_tipo_de_causa_para_mod_local();
                                tabla_locales_validados.ajax.reload(null, false);
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
            {
                text: 'Registrar % votos',
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
                        'accion': 'registrar_votos',
                        'lista_id': JSON.stringify(lista_id),
                        'horario_por_votos': horario_por_votos,
                        'porcentaje_votos': porcentaje_votos
                    }


                    if (!horario_por_votos || !porcentaje_votos) {
                    
                        Swal.fire({
//                            icon: 'warning',
                            text: 'No ha seleccionado el % de votos o su horario',
                        })
                        
                    } else {
                        $.ajax({
                            url: '{% url "uso-ajax" %}',
                            type: "post",
                            headers: { 'X-CSRFToken': csrftoken },
                            dataType: "json",
                            data: parametros,
		            beforeSend: function () {
                                $.LoadingOverlay("show", 
                                {
                                    background      : "rgba(0, 0, 0, 0.5)",
                                    imageAnimation  : "1.5s fadein",
                                    imageColor      : "#ffcc00",
                                    //text            : "Registrando % de voto...."
                                }
                                );
                            },
                            success: function (data) {
                                //cargar_tipo_de_causa_para_mod_local();
                                tabla_locales_validados.ajax.reload(null, false);
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
    
        //https://datatables.net/extensions/select/integration
        select: {
            style: 'os',
            selector: 'td:first-child'
        },
        drawCallback: function(settings) {
            $.LoadingOverlay("hide");
        },
        language: {
            decimal: "",
            emptyTable: "Sin locales validados.",
            info: "Mostrando _START_ a _END_ de _TOTAL_ locales",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
            infoFiltered: "",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ locales",
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
            //console.log('cargada')
        }
    });

    {% if request.user.rol == 2 %}
//        circuitos.column(0).visible(false); // or true, if you want to show it
        tabla_locales_validados.buttons().container().hide()
        $("#ocultar-user-cge").hide()
    {% endif %}


    function RecargarTabla() {
        comprobarSesion()
        tabla_locales_validados.ajax.reload(null, true);
    };

    //Permite seleccionar todos los chec box juntos para cambiar el estado
    $(".seleccionarTodosLocales").on("click", function (e) {
        if ($(this).is(":checked")) {
            tabla_locales_validados.rows().select()
        } else {
            tabla_locales_validados.rows().deselect();
        }
    });


    function cargar_tipo_de_causa_para_mod_local() {
        var valores = '<option value="">Seleccione</option>';
        var select_tipo_causa_loc = $('select[id="filtro-tipo-causa-no-iniciad-local"]')
        $.ajax({
            url: '{% url "uso-ajax" %}',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'accion': 'cargar-causa-en-local'
            },
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
            select_tipo_causa_loc.html(valores);
        });
    }

    function cargar_hora_voto() {
            let valores_voto = '<option value="">Seleccione</option>';
            let select_horarios = $('select[id="filtro-horario-porcentaje-votos"]')
            $.ajax({
                url: '{% url "uso-ajax" %}',
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'cargar-horario-control-voto'
                },
                dataType: 'json',
            }).done(function (data) {
                if (!data.hasOwnProperty('error')) {
                    $.each(data, function (key, value) {
                        valores_voto += '<option value="' + value.id + '">' + value.hora + '</option>';
                    })
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ':' + errorThrown)
            }).always(function (data) {
                select_horarios.html(valores_voto);
            });
        }


    $('#filtro-porcentaje-votos').on('change', function () {
        comprobarSesion()
        porcentaje_votos = $(this).val();
    });

    $('#filtro-horario-porcentaje-votos').on('change', function () {
        comprobarSesion()
        horario_por_votos  = $(this).val();
    });

    $('#filtro-tipo-causa-no-iniciad-local').on('change', function () {
        comprobarSesion()
        tipo_causa_local = $(this).val();
    });

    $('#filtro-por-estado-locales').on('change', function () {
        comprobarSesion()
        let valor = $(this).val();
        estado_local = valor
        tabla_locales_validados.ajax.reload(null, true);

    });

    $('#filtro-por-mesas').on('change', function () {
        comprobarSesion()
        let valor = $(this).val();
        mesas_ = valor
        tabla_locales_validados.ajax.reload(null, true);
    });

    $('#filtro-por-seg-int').on('change', function () {
       comprobarSesion()
       let valor = $(this).val();
       seg_int_ = valor
       tabla_locales_validados.ajax.reload(null, true);
    });

    $('#filtro-por-seg-ext').on('change', function () {
       comprobarSesion()
       let valor = $(this).val();
       seg_ext = valor
       tabla_locales_validados.ajax.reload(null, true);
    });

    ///////Funcion que carga los Distritos//////////
    function cargar_distritos (){

            var select_subdistritos = '';
            var select_secciones = '';
            var select_circuitos = '';

            var opciones_subdistritos = '';
            var opciones_secciones = '';
            var opciones_circuitos = '';
            let valores_distrito = '<option value="">Todos</option>';
            let select_distritos = $('select[id="filtro-distrito-en-local-validado"]')
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
            let select_sub_distritos_para_mapa = $('select[id="filtro-subdistrito-en-local-validado"]')
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
    $('select[id="filtro-distrito-en-local-validado"]').on('change', function () {
            var id = $(this).val();
            id_distrito_en_local_ = $(this).val();
            id_subdistrito_en_local_ = '';
            id_seccion_en_local_ ='';
            id_circuito_en_local_ = '';

            select_subdistritos = $('select[id="filtro-subdistrito-en-local-validado"]')
            select_secciones = $('select[id="filtro-seccion-para-local-validado"]')
            select_circuitos = $('select[id="filtro-circuito-para-local-validado"]')

            opciones_subdistritos = '<option value="">Todos</option>';
            opciones_secciones = '<option value="">Todas</option>';
            opciones_circuitos = '<option value="">Todos</option>';

            select_subdistritos.html(opciones_subdistritos)
            select_secciones.html(opciones_secciones)
            select_circuitos.html(opciones_circuitos)

            tabla_locales_validados.ajax.reload(null, false);

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
                        $('#filtro-subdistrito-en-local-validado').show();
                        $.each(respuesta.datos, function (key, value) {
                            opciones_subdistritos += '<option value="' + value.id + '">' + value.subdistrito + '</option>';
                        })
                    }
                    if (!respuesta.hay_subdistrito) {
                        $('#sub').hide();
                        $('#filtro-subdistrito-en-local-validado').hide();
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
    $('select[id="filtro-subdistrito-en-local-validado"]').on('change', function () {
            var id = $(this).val();
            id_subdistrito_en_local_ = $(this).val();
            id_seccion_en_local_ ='';
            id_circuito_en_local_ = '';

            select_secciones = $('select[id="filtro-seccion-para-local-validado"]')
            select_circuitos = $('select[id="filtro-circuito-para-local-validad"]')

            opciones_secciones = '<option value="">Todas</option>';
            opciones_circuitos = '<option value="">Todos</option>';

            select_circuitos.html(opciones_circuitos)

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
    $('select[id="filtro-seccion-para-local-validado"]').on('change', function () {
            var id = $(this).val();
            id_seccion_en_local_ = $(this).val();
            id_circuito_en_local_ = '';

            select_circuitos = $('select[id="filtro-circuito-para-local-validado"]')

            opciones_circuitos = '<option value="">Todos</option>';

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

    $('select[id="filtro-circuito-para-local-validado"]').on('change', function (){
              id_circuito_en_local_ = $(this).val();
              tabla_locales_validados.ajax.reload(null, false);
        });
});
