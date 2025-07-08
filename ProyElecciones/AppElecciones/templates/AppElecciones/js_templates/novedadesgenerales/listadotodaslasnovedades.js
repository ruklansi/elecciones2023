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

    cargar_tipo_novedad();
    cargar_distritos();

    //para filtrar en el servidor el datatable
    var tipo_novedad = '';
    var subsanada = '';

    var tabla_novedades_generales = $('#tabla').DataTable({
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[6, 10, 50, 100], [6, 10, 50, 100]],
        order: [[1, "asc"]],
        ajax: {
            url: "{% url 'listado-de-novedades-generales' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {
                d.id_distrito = id_distrito
                d.tipo_novedad = tipo_novedad
                d.subsanada = subsanada
            }
        },
        columns: [
             {
                data: null,
                defaultContent: '',
                orderable: false,
                className: 'select-checkbox',
            },

            { data: 'distrito__distrito' },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                moment.locale('es');
                return moment(row.fecha).format('L LT');
                }
            },
            { data: 'tipo__tipo', orderable: false },
            { data: 'detalle', orderable: false },
            { data: 'subsanada', orderable: false },
            { data: 'medidas_adoptadas', orderable: false },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                        var buttons = '';
                        var url1='{% url "actualizar-novedades-generales" 99%}'.replace('99',row.id)
                        var url2='{% url "eliminar-novedades-generales" 99%}'.replace('99',row.id)
                        var url3='{% url "detalles-novedades-generales" 99%}'.replace('99',row.id)
                        if (row.editar){
                            buttons += '<a title="Editar" href="'+ url1+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></a> ' + '&nbsp;&nbsp';
                        }
                        if (row.eliminar){
                            buttons += '<a title="Eliminar" href="'+ url2+'" type="button" class=""><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></a> ' + '&nbsp;&nbsp' ;
                        }
                        buttons += '<a title="Detalle de la novedad" href="'+ url3+'" type="button" class=""><i class="fas fa-address-card" style="font-size:15px;color:goldenrod"></i></a>';
                        return buttons;

               }
            },
        ],
        dom: "<'row'<'col-md-3'B>><'row'<'mt-3 ml-3'l>>frtip",
        buttons: [
            {
                text: 'Exportar en PDF',
                extend: 'selected',
                //className: 'btn-success',
                className: ' mipdf',

                action: function (e, dt, button, config) {
                    var lista_id = []
                    $.map(dt.rows({ selected: true }).data().toArray(), function (item) {
                        var dict = {};
                        dict['id'] = item.id
                        lista_id.push(dict)
                    })
                    let mi_url='{% url "listar-novedades-pdf" %}'
                    window.open(window.location.origin + mi_url + '?lista_id=' + JSON.stringify(lista_id))
                }
            },
        ],
        select: {
            style: 'os',
            selector: 'td:first-child'
        },
        language: {
            decimal: "",
            emptyTable: "Sin novedades",
            info: "Mostrando _START_ a _END_ de _TOTAL_ novedades",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
            infoFiltered: "(Filtrado de _MAX_ novedades en total)",
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
            tabla_novedades_generales.rows().select()
        } else {
            tabla_novedades_generales.rows().deselect();
        }
    });

    {% if request.user.rol == 2 %}
        tabla_novedades_generales.buttons().container().hide()
      {% endif %}


    function RecargarTabla() {
        comprobarSesion()
        tabla_novedades_generales.ajax.reload(null, true);
    };

    function cargar_tipo_novedad() {
        var valores = '<option value="">Todas</option>';
        var select_tipo_novedad = $('select[id="filtro-tipo-nov-generales"]')
        $.ajax({
            url: "{% url 'cargar-nov-para-filtros' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            dataType: 'json',
            data : {
                'accion': 'filtrar_desde_novedades_generales'
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
            let select_distritos = $('select[id="filtro-distrito-nov-generales"]')
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
    $('select[id="filtro-distrito-nov-generales"]').on('change', function () {
            id_distrito = $(this).val();
            RecargarTabla();
        });

    $('#filtro-tipo-nov-generales').on('change', function () {
        comprobarSesion()
        let id = $(this).val();
        tipo_novedad = id;
        tabla_novedades_generales.ajax.reload(null, true);
    });

    $('#filtro-subsanada-nov-generales').on('change', function () {
        comprobarSesion()
        let valor = $(this).val();
        subsanada = valor;
        tabla_novedades_generales.ajax.reload(null, true);
    });
});
