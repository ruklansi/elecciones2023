var csrftoken = Cookies.get('csrftoken');
$(function () {
     {% if request.user.rol == 3 or request.user.rol == 4 %}
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
    var tipo_novedad = '';
    var subsanada = '';

    cargar_distritos();
    cargar_tipo_novedad()

    var tabla_novedades_en_locales = $('#tabla').DataTable({
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[6, 10, 50, 100], [6, 10, 50, 100]],
        order: [[1, "asc"]],
        ajax: {
            url: "{% url 'listado-de-todas-novedades-en-locales' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {

            d.id_distrito = id_distrito
            d.tipo_novedad = tipo_novedad
            d.subsanada = subsanada

            }
        },
        columns: [
            {data: 'local__circuito__seccion__distrito__distrito', orderable: false},
            {data: 'local_enlace',orderable: false},
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data) {
                moment.locale('es');
                //return moment(data).format('MMMM Do YYYY');moment("20111031", "YYYYMMDD").fromNow();
                return moment(data).format('L');
            }
             },
            { data: 'tipo__tipo', orderable: false },
            { data: 'detalle', orderable: false },
            { data: 'subsanada', orderable: false },
            { data: 'medidas_adoptadas', orderable: false },
        ],
//        dom: "<'row'<'col-md-3'B>><'row'<'mt-3 ml-3'l>>frtip",
//        buttons: [
//            {
//                text: 'Exportar en PDF',
//                extend: 'selected',
//                //className: 'btn-success',
//                className: 'mipdf',
//                action: function (e, dt, button, config) {
//                    var dic = { 'novedad': [] }
//
//                    $.map(dt.rows({ selected: true }).data().toArray(), function (item) {
//                        dic['novedad'].push(item.id)
//                    })
//                    window.location = window.location.origin + '/elecciones23/pdfnov/' + '?lista_id=' + JSON.stringify(dic);
//                }
//            },
//        ],
//        select: {
//            style: 'os',
//            selector: 'td:first-child'
//        },
        language: {
            decimal: "",
            emptyTable: "Sin novedades",
            info: "Mostrando _START_ a _END_ de _TOTAL_ novedades",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
            infoFiltered: "",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ novedades",
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

//            select: {
//                rows: {
//                    _: "Seleccionadas %d filas",
//                    0: "",
//                    1: " %d fila seleccionada"
//                }
//            }
        },
        initComplete: function (settings, json) {
        }
    });


    function RecargarTabla() {
        comprobarSesion()
        tabla_novedades_en_locales.ajax.reload(null, true);
   };

    function cargar_tipo_novedad() {
        var valores = '<option value="">Todos</option>';
        var select_tipo_novedad = $('select[id="filtro-tipo-nov-local"]')
        $.ajax({
            url: "{% url 'cargar-nov-para-filtros' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            dataType: 'json',
             data : {
                'accion': 'filtrar_desde_novedades_en_locales'
            },
        }).done(function (data) {
            if (!data.hasOwnProperty('error')) {
                $.each(data, function (key, value) {
                    valores += '<option value="' + value.id + '">' + value.tipo_novedad + '</option>';
                })
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(textStatus + ':' + errorThrown)
        }).always(function (data) {
            select_tipo_novedad.html(valores);
        });
    }

    ///////Funcion que carga los Distritos//////////
    function cargar_distritos (){
            let valores_distrito = '<option value="">Todos</option>';
            let select_distritos = $('select[id="filtro-distrito-novedad-local"]')
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
    $('select[id="filtro-distrito-novedad-local"]').on('change', function () {
            comprobarSesion();
            id_distrito = $(this).val();
            RecargarTabla();
        });

    $('#filtro-tipo-nov-local').on('change', function () {
        comprobarSesion()
        let id = $(this).val();
        tipo_novedad = id;
        RecargarTabla();
    });

    $('#filtro-subsanada-nov-local').on('change', function () {
        comprobarSesion()
        let valor = $(this).val();
        subsanada = valor;
        RecargarTabla();
    });

});
