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

    var tabla_led = $('#tabla').DataTable({
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 10], [5, 10]],
        order: [[0, "asc"]],
        ajax: {
            url: "{% url 'listado-de-led' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
             data: function (d) {
                d.id_distrito = id_distrito
            }
        },
        columns: [
            { data: 'distrito__distrito', orderable: false },
            { data: 'direccion', orderable: false },
            { data: 'tipo__tipo', orderable: false },
            { data: 'obs', orderable: false },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    let buttons = '';
                    let url1='{% url "actualizar-led" 99%}'.replace('99',row.id)
                    let url2='{% url "eliminar-led" 99%}'.replace('99',row.id)
                    let url3='{% url "detalles-led" 99%}'.replace('99',row.id)
                    if (row.editar){
                        buttons += '<a title="Editar" href="'+ url1+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></a> '+ '&nbsp;&nbsp';
                    }
                    if (row.eliminar){
                        buttons += '<a title="Eliminar" href="'+ url2+'" type="button" class=""><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></a> ' + '&nbsp;&nbsp';
                    }
                    buttons += '<a title="Detalle y registro de seguridad en el LED" href="'+ url3+'" class=""><i class="fas fa-address-card" style="font-size:15px;color:goldenrod"></i></a>';

                    return buttons;
                }
            }
        ],
        language: {
            decimal: "",
            emptyTable: "Sin registros de LED",
            info: "Mostrando _START_ a _END_ de _TOTAL_ LED",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
            infoFiltered: "(Filtrado de _MAX_ LED en total)",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ LED",
            loadingRecords: "Cargando...",
            processing: "Procesando...",
            search: "Buscar:",
            zeroRecords: "Sin registros de LED",
            paginate: {
                first: "Primero",
                last: "Ultimo",
                next: "Siguiente",
                previous: "Anterior"
            },
        },
        initComplete: function (settings, json) {
        }
    });

    function RecargarTabla() {
        comprobarSesion()
        tabla_led.ajax.reload(null, true);
    };

    ///////Funcion que carga los Distritos//////////
    function cargar_distritos (){
            let valores_distrito = '<option value="">Todos</option>';
            let select_distritos = $('select[id="filtro-distrito-led"]')
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
    $('select[id="filtro-distrito-led"]').on('change', function () {
            comprobarSesion();
            id_distrito = $(this).val();
            RecargarTabla();
        });
});
