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

    var id_distrito = '';
    var id_subdistrito = '';
    var id_seccion ='';


    cargar_distritos();


    var situacion_ = '';
    var tienelocal_ = '';
    var urnasentregadas_ = '';

    var circuitos = $('#tabla').DataTable({
        //dom: 'lfrtip',
        //dom: 'lfrtip',//Sacando letra f quito el filtro
        rowCallback: function (row, data, index) {
//            if (!data.editar){
//                 $(row).find('td:eq(0)').hide();
//            }
            if (data['situacion'] == "Replegado") {
                $(row)
                    .find("td:eq(1)")
                    .css("background-color", "#CCE6FF");
                $(row).find('td:eq(1)').css('color', 'black');

                $(row)
                    .find("#avanzar")
                    .hide();
            }
            if (data['situacion'] == "Desplegado") {
                $(row)
                    .find("td:eq(1)")
                    .css("background-color", "#B3E5B3");
                $(row).find('td:eq(1)').css('color', 'black');
            }
            if (data['situacion'] == "Inicio repliegue") {
                $(row)
                    .find("td:eq(1)")
                    .css("background-color", "#ffffcc");
                $(row).find('td:eq(1)').css('color', 'black');
            }
            if (data['situacion'] == "Inicio despliegue") {
                $(row)
                    .find("td:eq(1)")
                    .css("background-color", "#FFDDCC");
                $(row).find('td:eq(1)').css('color', 'black');
            }
            if (data['entrego_urna_en_led']) {
                $(row)
                    .find("td:eq(2)")
                    .css("background-color", "#17A2B8");
                $(row).find('td:eq(2)').css('color', 'black');
                $(row).find('td:eq(2)').text('Entregadas');
            }
            if (!data['entrego_urna_en_led']) {
                $(row).find('td:eq(2)').text('No entregadas');
            }
            if (data['situacion'] == "Actividades no iniciadas") {
                $(row)
                    .find("#reset")
                    .hide();
            }
        },
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 10, 20, 50], [5, 10, 20, 50]],
        pageLength: 5,
        order: [[1, "asc"]],
        //dom: "<'row'<'col-md-3'B>><'row'<'mt-3 ml-3'l>>tip",
        dom: "<'row'B><'row'<'mt-3 ml-3'l>>frtip",
        //deferLoading: 0,//inicializa una datatable vacia
        ajax: {
            url: '{% url "listado-de-circuitos-filtrados" %}',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {

                d.id_distrito= id_distrito
                d.id_subdistrito = id_subdistrito
                d.id_seccion = id_seccion


                d.situacion = situacion_
                d.tienelocal = tienelocal_
                d.urnasentregadas = urnasentregadas_
            }
        },
        columns: [
            {
                data: null,
                defaultContent: '',
                orderable: false,
                className: 'select-checkbox',
            },
            { data: 'situacion', orderable: false },
            { data: 'entrego_urna_en_led', orderable: false },
            { data: 'seccion__distrito__distrito', orderable: false },
            { data: 'seccion__subdistrito__subdistrito', orderable: false },
            { data: 'seccion__seccion', orderable: false },
            { data: 'circuito', orderable: false },
            { data: 'total_locales', orderable: true },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {

                    let buttons = '';
                    var url1='{% url "detalles-circuito" 99%}'.replace('99',row.id)
                    var url2='{% url "actualizar-circuito" 99%}'.replace('99',row.id)
                    var url3='{% url "eliminar-circuito" 99%}'.replace('99',row.id)

                    buttons += '<a title="Registro de personal, reserva y vehículos" href="'+ url1+'" class="" ><i class="fas fa-address-card" style="font-size:15px;color:goldenrod"></i></a> ' + '&nbsp;&nbsp';

                    if (row.editar){
                        buttons += '<a title="Editar" href="'+ url2+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></a> ' + '&nbsp;&nbsp';
                    }
                    if (row.eliminar){
                        buttons += '<a title="Eliminar" href="'+ url3+'" type="button" class=""><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></a>';
                    }
                    return buttons;
                }
            }
        ],
        select: {
            style: 'os',
            selector: 'td:first-child'
        },

        buttons: [
            {   //repliegue:  Inicio Repliegue -> Replegado
                //text: '<<<<-Replegar-<<<<',

                text: ' <i style="color:white; font-size:15px;" class="fas fa-arrow-left"></i> Retroceder situación',
                extend: 'selected',
                // className: 'btn-success',
                titleAttr: 'Retrocede situación',
                className: 'color_botones_situacion',
                action: function (e, dt, node, config) {


                    //$(".dt-buttons").find(".blue").removeClass("blue");
                    //node.addClass("blue");

                    var lista_id = []
                    $.map(dt.rows({ selected: true }).data().toArray(), function (item) {
                        var dict = {};
                        dict['id'] = item.id
                        lista_id.push(dict)
                    })
                    // lista_id es una lista con diccionarios de los id de los locales ejemplo: [{'id': xxxx}]
                    // Debe ir así entonces en el django los proceso con un json.loads(request.POST['lista_id'])
                    // y obtengo un listado para luego con un for obtener el id  lista_id = [x['id'] for x in lista]
                    var parametros = {
                        'accion': 'replegar',
                        'lista_id': JSON.stringify(lista_id)
                    }
                    $.ajax({
                        url: '{% url "desplegar-circuito" %}',
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
                            circuitos.ajax.reload(null, false);
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            //alert(textStatus + ': ' + errorThrown + ': ' + jqXHR.responseText);
                            var errorMessage = jqXHR.status + ': ' + jqXHR.statusText
                            alert('Error - ' + errorMessage + ' - ' + jqXHR.responseText);
                        }
                    });
                }
            },
            {   //despliegue: Iniciar despliegue -> Desplegado -> Inicio repliegue -> Replegado
                //text: '>>>>Desplegar->>>>',
                text: 'Avanzar situación <i style="color:white; font-size:15px;" class="fas fa-arrow-right"></i>',
                extend: 'selected',
                //className: 'btn-success',
                titleAttr: 'Inicio despliegue -> Desplegado -> Inicio repliegue -> Replegado',
                className: 'color_botones_situacion',
                action: function (e, dt, node, config) {
                    //var rows = dt.rows({ selected: true }).count();
                    var lista_id = []
                    $.map(dt.rows({ selected: true }).data().toArray(), function (item) {
                        var dict = {};
                        dict['id'] = item.id
                        dict['locales'] = item.total_locales
                        lista_id.push(dict)

                    })
                    var parametros = {
                        'accion': 'desplegar',
                        'lista_id': JSON.stringify(lista_id)
                    }
                   function hasNullValueInList(list) {
                      for (var i = 0; i < list.length; i++) {
                        var obj = list[i];
                        for (var key in obj) {
                          if (obj[key] === null) {
                            return true;
                          }
                        }
                      }
                      return false;
                   }

                    if (hasNullValueInList(lista_id)) {
                        Swal.fire({
                            text: 'El Circuitos debe tener locales asignados',
                       })
                   } else {
                      $.ajax({
                      url: '{% url "desplegar-circuito" %}',
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
                            circuitos.ajax.reload(null, false);
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
            {   //Resetear: Actividades no iniciadas
                text: 'Resetear situación',
                extend: 'selected',
                //className: 'btn-success',
                titleAttr: 'Vuelve la situación a "Actividades no iniciadas',
                className: 'color_botones_situacion',
                action: function (e, dt, node, config) {
                    //var rows = dt.rows({ selected: true }).count();

                    var lista_id = []
                    $.map(dt.rows({ selected: true }).data().toArray(), function (item) {
                        var dict = {};
                        dict['id'] = item.id
                        lista_id.push(dict)
                    })
                    // lista_id es una lista con diccionarios de los id de los locales ejemplo: [{'id': xxxx}]
                    // Debe ir así entonces en el django los proceso con un json.loads(request.POST['lista_id'])
                    // y obtengo un listado para luego con un for obtener el id  lista_id = [x['id'] for x in lista]
                    // console.log(lista_id)
                    var parametros = {
                        'accion': 'resetear',
                        'lista_id': JSON.stringify(lista_id)
                    }

                    $.ajax({
                        url: '{% url "desplegar-circuito" %}',
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
                            circuitos.ajax.reload(null, false);
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            //alert(textStatus + ': ' + errorThrown + ': ' + jqXHR.responseText);
                            var errorMessage = jqXHR.status + ': ' + jqXHR.statusText
                            alert('Error - ' + errorMessage + ' - ' + jqXHR.responseText);
                        }
                    });

                }
            },
            {   //Urnas entregadas en el led
                text: 'Entregar urnas al LED',
                extend: 'selected',
                //className: 'btn-success',
                titleAttr: 'Entregar las urnas en el LED',
                className: 'color_botones_situacion',
                action: function (e, dt, node, config) {
                    //var rows = dt.rows({ selected: true }).count();

                    var lista_id = []
                    $.map(dt.rows({ selected: true }).data().toArray(), function (item) {
                        var dict = {};
                        dict['id'] = item.id
                        dict['locales'] = item.total_locales
                        lista_id.push(dict)
                    })
                    // lista_id es una lista con diccionarios de los id de los locales ejemplo: [{'id': xxxx}]
                    // Debe ir así entonces en el django los proceso con un json.loads(request.POST['lista_id'])
                    // y obtengo un listado para luego con un for obtener el id  lista_id = [x['id'] for x in lista]
                    // console.log(lista_id)
                    var parametros = {
                        'accion': 'entregar_urnas_led',
                        'lista_id': JSON.stringify(lista_id)
                    }

                    function hasNullValueInList(list) {
                      for (var i = 0; i < list.length; i++) {
                        var obj = list[i];
                        for (var key in obj) {
                          if (obj[key] === null) {
                            return true;
                          }
                        }
                      }
                      return false;
                   }

                    if (hasNullValueInList(lista_id)) {
                        Swal.fire({
                            text: 'El Circuitos debe tener locales asignados',
                       })
                   } else {
                      $.ajax({
                      url: '{% url "desplegar-circuito" %}',
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
                            circuitos.ajax.reload(null, false);
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
            {   //Urnas entregadas en el led
                text: 'No entregar urnas al LED',
                extend: 'selected',
                //className: 'btn-success',
                titleAttr: 'No entregar las urnas en el LED',
                className: 'color_botones_situacion',
                action: function (e, dt, node, config) {
                    //var rows = dt.rows({ selected: true }).count();

                    var lista_id = []
                    $.map(dt.rows({ selected: true }).data().toArray(), function (item) {
                        var dict = {};
                        dict['id'] = item.id
                        lista_id.push(dict)
                    })
                    // lista_id es una lista con diccionarios de los id de los locales ejemplo: [{'id': xxxx}]
                    // Debe ir así entonces en el django los proceso con un json.loads(request.POST['lista_id'])
                    // y obtengo un listado para luego con un for obtener el id  lista_id = [x['id'] for x in lista]
                    // console.log(lista_id)
                    var parametros = {
                        'accion': 'no_entregar_urnas_led',
                        'lista_id': JSON.stringify(lista_id)
                    }

                    $.ajax({
                        url: '{% url "desplegar-circuito" %}',
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
                            circuitos.ajax.reload(null, false);
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            //alert(textStatus + ': ' + errorThrown + ': ' + jqXHR.responseText);
                            var errorMessage = jqXHR.status + ': ' + jqXHR.statusText
                            alert('Error - ' + errorMessage + ' - ' + jqXHR.responseText);
                        }
                    });

                }
            },
        ],

        drawCallback: function(settings) {
            $.LoadingOverlay("hide");
        },
        language: {
            decimal: "",
            emptyTable: "No hay circuitos para mostrar",
            info: "Mostrando _START_ a _END_ de _TOTAL_ circuitos",
            infoEmpty: "Mostrando 0 to 0 of 0 circuitos",
//            infoFiltered: "(Filtrado de _MAX_ circuitos en total)",
            infoFiltered: "",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ circuitos",
            loadingRecords: "Cargando...",
            processing: "Procesando...",
            search: "Buscar:",
            searchPlaceholder: '',
            zeroRecords: "No hay circuitos para mostrar",
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
        initComplete: function (settings, json) { }
    });
    {% if request.user.rol == 2 %}
        circuitos.buttons().container().hide();
    {% endif %}

    function RecargarTabla(){
        circuitos.ajax.reload(null, false);
    }

    ///////Funcion que carga los Distritos//////////
    function cargar_distritos (){

            var select_subdistritos = '';
            var select_secciones = '';

            var opciones_subdistritos = '';
            var opciones_secciones = '';

            let valores_distrito = '<option value="">Todos</option>';
            let select_distritos = $('select[id="filtro-distrito-en-circuito"]')

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
            let select_sub_distritos_para_mapa = $('select[id="filtro-subdistrito-en-circuito"]')
            $.ajax({
                url: "{% url 'filtro-para-organizaciones' %}",
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
    $('select[id="filtro-distrito-en-circuito"]').on('change', function () {
            var id = $(this).val();
            id_distrito = $(this).val();
            id_subdistrito = '';
            id_seccion ='';

            select_subdistritos = $('select[id="filtro-subdistrito-en-circuito"]')
            select_secciones = $('select[id="filtro-seccion-en-circuito"]')

            opciones_subdistritos = '<option value="">Todos</option>';
            opciones_secciones = '<option value="">Todas</option>';

            select_subdistritos.html(opciones_subdistritos)
            select_secciones.html(opciones_secciones)

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
    $('select[id="filtro-subdistrito-en-circuito"]').on('change', function () {
            var id = $(this).val();
            id_subdistrito = $(this).val();
            id_seccion ='';

            select_secciones = $('select[id="filtro-seccion-en-circuito"]')


            opciones_secciones = '<option value="">Todas</option>';
            opciones_circuitos = '<option value="">Todos</option>';

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
    $('select[id="filtro-seccion-en-circuito"]').on('change', function () {
            var id = $(this).val();
            id_seccion = $(this).val();


            select_circuitos = $('select[id="filtro-circuito-en-circuito"]')

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

    //Filtra los circuitos si tinen o no locales asignados
    $('select[id="filtro-por-cantlocal"]').on('change', function (){
              tienelocal_ = $(this).val();
              RecargarTabla();
    });

    //Filtra los circuitos si tinen o no las urnas entregadas en el LED
    $('select[id="filtro-por-urnas-enled"]').on('change', function (){
              urnasentregadas_ = $(this).val();
              RecargarTabla();
    });

     //Filtra los circuitos por situación
    $('select[id="filtro-circuito-por-situacion"]').on('change', function (){
              situacion_ = $(this).val();
              RecargarTabla();
    });

    //Permite seleccionar todos los chec box juntos para cambiar la situación
    $(".seleccionarTodosCircuitos").on("click", function (e) {
        if ($(this).is(":checked")) {
            circuitos.rows().select()
        } else {
            circuitos.rows().deselect();
        }
    });


});





