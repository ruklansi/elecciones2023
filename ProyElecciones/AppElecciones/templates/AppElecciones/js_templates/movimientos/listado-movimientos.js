var csrftoken = Cookies.get('csrftoken');
$(function () {
      {% if request.user.rol == 3 %}
        $('#fil').hide()
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

    var tablaMovimientos = $('#tabla').DataTable({
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 10], [5, 10]],
        order: [[1, "asc"]],
        ajax: {
            url: "{% url 'listado-de-movimientos' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {
                d.id_distrito = id_distrito
            }
        },
        columns: [
            {
                data: null,
                defaultContent: '',
                orderable: false,
                className: 'select-checkbox',
            },
            { data: 'distrito__distrito', orderable: false },
            { data: 'tipo__tipo', orderable: false },
            { data: 'efectivos', orderable: false },
            { data: 'vehiculos', orderable: false },
            { data: 'inicio', orderable: false },
            { data: 'fin', orderable: false },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    let buttons = '';
                    var url1='{% url "actualizar-movimiento" 99%}'.replace('99',row.id)
                    var url2='{% url "eliminar-movimiento" 99%}'.replace('99',row.id)
                    if (row.editar){
                        buttons += '<a title="Editar" href="'+ url1+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></a> ' + '&nbsp;&nbsp';
                    }
                    if (row.eliminar){
                        buttons += '<a title="Eliminar" href="'+ url2+'" type="button" class=""><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></a>';
                    }
                    return buttons;
                }
            }
        ],
        columnDefs: [{
            targets: [5, 6], render: function (data1) {
                moment.locale('es');
                //return moment(data).format('MMMM Do YYYY');moment("20111031", "YYYYMMDD").fromNow();
                return moment(data1).format('L LT');
            },
        }],
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
                    let mi_url='{% url "listar-movimientos-pdf" %}'
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
            emptyTable: "No hay movimientos para mostrar",
            info: "Mostrando _START_ a _END_ de _TOTAL_ movimientos",
            infoEmpty: "Mostrando 0 to 0 of 0 movimientos",
            infoFiltered: "(Filtrado de _MAX_ movimientos en total)",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ movimientos",
            loadingRecords: "Cargando...",
            processing: "Procesando...",
            search: "Buscar:",
            zeroRecords: "No hay movimientos para mostrar",
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

    {% if request.user.rol == 2 %}
        tablaMovimientos.buttons().container().hide()
      {% endif %}


    function RecargarTabla() {
        comprobarSesion()
        tablaMovimientos.ajax.reload(null, true);
    };

    //Permite seleccionar todos los chec box juntos para cambiar el estado
    $(".seleccionarTodosMovimientos").on("click", function (e) {
        if ($(this).is(":checked")) {
            tablaMovimientos.rows().select()
            //var loc = locales.rows({ selected: true, page: 'current' }).data();
            //console.log(loc)
        } else {
            tablaMovimientos.rows().deselect();
        }
    });

    ///////Funcion que carga los Distritos//////////
    function cargar_distritos (){
            let valores_distrito = '<option value="">Todos</option>';
            let select_distritos = $('select[id="filtro-distrito-movimientos"]')
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
    $('select[id="filtro-distrito-movimientos"]').on('change', function () {
            id_distrito = $(this).val();
            RecargarTabla();
        });
});

