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

    var tabla_locales_no_validados = $('#tabla').DataTable({
        rowCallback: function (row, data, index) {
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
        order: [[0, "asc"]],
        ajax: {
            url: '{% url "listado-de-locales-novalidados" %}',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {
                d.id_distrito_local = id_distrito_en_local_
                d.id_subdistrito_local = id_subdistrito_en_local_
                d.id_seccion_local = id_seccion_en_local_
                d.id_circuito_local = id_circuito_en_local_
            },
//            dataSrc: function(data){
//                $('#mostrar_cant_locales_no_validados').html(data.locales_no_validados)
//                return data.data
//            },
        },
        columns: [
            { data: 'nombre', orderable: false },
            { data: 'direccion', orderable: false },
            { data: 'localidad', orderable: false },
            { data: 'circuito__seccion__distrito__distrito', orderable: false },
            { data: 'circuito__seccion__subdistrito__subdistrito', orderable: false },
            { data: 'circuito__seccion__seccion', orderable: false },
            { data: 'circuito__circuito', orderable: false },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    let buttons = '';
                    let tipo_local;
                    let url4 ='{% url "eliminar-local" 999 777 %}'.replace('999', row.id, '777', tipo_local)
                    if (row.editar){
                        buttons = '<span id="validar_local" id_local="'+row.id+'" distrito="'+row.circuito__seccion__distrito__distrito+'" nombre="'+row.nombre+'" direccion="'+row.direccion+'"  localidad="'+row.localidad+'"title="Validar local" class="" ><i class="fas fa-solid fa-school-circle-check" style="font-size:15px;color:#70dbdb"></i></span>' + '&nbsp;&nbsp';
                    }
                     if (row.eliminar){
                        buttons += '<a title="Eliminar" href="'+url4+'" type="button" class=""><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></a>';
                    }
                    return buttons;
                }
            },
        ],
        //https://datatables.net/extensions/select/integration
        language: {
            decimal: "",
            emptyTable: "Sin locales para validar.",
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
        },
        initComplete: function (settings, json) {
        }
    });

    function RecargarTabla() {
        comprobarSesion()

        tabla_locales_no_validados.ajax.reload(null, true);
    };

    // Validar el local via ajax
    $('#tabla tbody').on('click', '#validar_local', function () {
        comprobarSesion()
        let id_local = $(this).attr('id_local');
        let nombre = $(this).attr('nombre');
        let direccion = $(this).attr('direccion');
        let localidad = $(this).attr('localidad');
        let distrito = $(this).attr('distrito');

        let url__= "{% url 'actualizar-local' 0 %}"

        Swal.fire({
                 title: '<strong>Seleccionar local</strong>',
                 html:
                    '<p>Confirma que este local será utilizado durante las elecciones:</p> ' +
                    '<p>Nombre: '+nombre+'</p> ' +
                    '<p>Dirección: '+direccion+'</p> ' +
                    '<p>Localidad: '+localidad+'</p> ' +
                    '<p>Distrito: '+distrito+'</p> ' +
                    'Puede editar los datos desde <a href="'+url__.replace(0, id_local)+'?validado=no">aquí</a> '+
                    'o hacerlo desde la lista de Locales validados una vez confirmado',
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
                        data: {'accion':'validar_local', 'id_local': id_local},
                        success: function (data) {
                            if (data.validado) {
                                RecargarTabla();
                            }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                                alert('Error eliminando vehículo contratado');
                        }
                    });
                }
            })
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
            let select_distritos = $('select[id="filtro-distrito-en-local-no-validado"]')
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
            let select_sub_distritos_para_mapa = $('select[id="filtro-subdistrito-en-local-no-validado"]')
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
    $('select[id="filtro-distrito-en-local-no-validado"]').on('change', function () {
            var id = $(this).val();
            id_distrito_en_local_ = $(this).val();
            id_subdistrito_en_local_ = '';
            id_seccion_en_local_ ='';
            id_circuito_en_local_ = '';


            select_subdistritos = $('select[id="filtro-subdistrito-en-local-no-validado"]')
            select_secciones = $('select[id="filtro-seccion-para-local-no-validado"]')
            select_circuitos = $('select[id="filtro-circuito-para-local-no-validado"]')

            opciones_subdistritos = '<option value="">Todos</option>';
            opciones_secciones = '<option value="">Todas</option>';
            opciones_circuitos = '<option value="">Todos</option>';

            select_subdistritos.html(opciones_subdistritos)
            select_secciones.html(opciones_secciones)
            select_circuitos.html(opciones_circuitos)

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
               //console.log(respuesta)
                if (!respuesta.hasOwnProperty('error')) {
                    if (respuesta.hay_subdistrito) {
                        $('#sub').show();
                        $('#filtro-subdistrito-en-local-no-validado').show();
                        $.each(respuesta.datos, function (key, value) {
                            opciones_subdistritos += '<option value="' + value.id + '">' + value.subdistrito + '</option>';
                        })
                    }
                    if (!respuesta.hay_subdistrito) {
                        $('#sub').hide();
                        $('#filtro-subdistrito-en-local-no-validado').hide();
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
    $('select[id="filtro-subdistrito-en-local-no-validado"]').on('change', function () {
            var id = $(this).val();
            id_subdistrito_en_local_ = $(this).val();
            id_seccion_en_local_ ='';
            id_circuito_en_local_ = '';

            select_secciones = $('select[id="filtro-seccion-para-local-no-validado"]')
            select_circuitos = $('select[id="filtro-circuito-para-local-no-validad"]')

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
    $('select[id="filtro-seccion-para-local-no-validado"]').on('change', function () {
            var id = $(this).val();
            id_seccion_en_local_ = $(this).val();
            id_circuito_en_local_ = '';

            select_circuitos = $('select[id="filtro-circuito-para-local-no-validado"]')

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

    $('select[id="filtro-circuito-para-local-no-validado"]').on('change', function (){
              id_circuito_en_local_ = $(this).val();
              RecargarTabla();
        });


});
