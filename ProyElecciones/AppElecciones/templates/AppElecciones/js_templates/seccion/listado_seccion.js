var csrftoken = Cookies.get('csrftoken');
$(function () {

    //Si tiene el rol de Distrito y no tiene subdistrito oculto el desplegable del filtro de subdistrito
      {% if request.user.rol == 3 and tiene_subdistrito == 'no' %}
        $('#sub').hide()
      {% endif %}
       //Si tiene el rol de Subdistrito oculto el desplegable del filtro de distrito
      {% if request.user.rol == 4  %}
        $('#field_subdistritos').hide()
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

    var id_distrito_ = '';
    var id_subdistrito_ = '';

    cargar_distritos();

    var tablaSecciones = $('#tabla').DataTable({
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
            url: window.location.pathname,
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {
                d.id_distrito = id_distrito_
                d.id_subdistrito = id_subdistrito_
            }
        },

        columns: [

            { data: 'seccion', orderable: false },
            { data: 'subdistrito__subdistrito', orderable: false },
            { data: 'distrito__distrito', orderable: false },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var url2='{% url "detalles-seccion" 99 %}'.replace('99',row.id);
                    var buttons = '<a title="Registro de personal, reserva y vehículos" href="'+url2+'" class="" ><i class="fas fa-address-card" style="font-size:15px;color:goldenrod"></i></a> ' + '&nbsp;&nbsp';
                    return buttons;
                }
            }
        ],
        language: {
            decimal: "",
            emptyTable: "No hay secciones",
            info: "Mostrando _START_ a _END_ de _TOTAL_ secciones",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
            infoFiltered: "(Filtrado de _MAX_ secciones en total)",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ secciones",
            loadingRecords: "Cargando...",
            processing: "Procesando...",
            search: "Buscar:",
            zeroRecords: "No hay secciones",
            paginate: {
                first: "Primero",
                last: "Ultimo",
                next: "Siguiente",
                previous: "Anterior"
            }
        },
        initComplete: function (settings, json) {
        }
    });

    function RecargarTabla(){
        tablaSecciones.ajax.reload(null, false);
    }

    ///////Funcion que carga los Distritos//////////
    function cargar_distritos (){

            var select_subdistritos = '';
            var select_secciones = '';
            var select_circuitos = '';

            var opciones_subdistritos = '';


            let valores_distrito = '<option value="">Todos</option>';
            let select_distritos = $('select[id="filtro-distrito-en-seccion"]')
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
            let select_sub_distritos_para_mapa = $('select[id="filtro-subdistrito-en-seccion"]')
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
    $('select[id="filtro-distrito-en-seccion"]').on('change', function () {
            var id = $(this).val();
            id_distrito_ = $(this).val();
            id_subdistrito_ = '';

            select_subdistritos = $('select[id="filtro-subdistrito-en-seccion"]')

            opciones_subdistritos = '<option value="">Todos</option>';

            select_subdistritos.html(opciones_subdistritos)

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

                    }

                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ':' + errorThrown)
            }).always(function (respuesta) {
                select_subdistritos.html(opciones_subdistritos);
            })
        });

    //////Change en Subdistritos para cargar secciones/////////
    $('select[id="filtro-subdistrito-en-seccion"]').on('change', function () {
            id_subdistrito_ = $(this).val();
            RecargarTabla();
    });


});

