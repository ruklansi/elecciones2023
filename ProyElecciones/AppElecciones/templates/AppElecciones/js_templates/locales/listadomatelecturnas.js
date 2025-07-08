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
    var accion = '';

    var estado = '';
    var control_urna = true;

    var id_distrito = '';
    var id_subdistrito = '';
    var id_seccion ='';
    var id_circuito = '';

    cargar_distritos();

    var tabla_locales_mat_elec_urnas = $('#tabla').DataTable({
        rowCallback: function (row, data, index) {
             $(row).find('td:eq(7)').css('color', 'rgb(255, 153, 0)');
            if (!data.recepciono_mat_elec) {
                $(row).find('td:eq(8)').text('No');
                $(row).find('td:eq(8)').css('color', '#ff8080');
            }
            if (data.recepciono_mat_elec) {
                $(row).find('td:eq(8)').text('Si');
                $(row).find('td:eq(8)').css('color', '#99ff99');
            }
            if (data.transmitio === 'Sí') {
               $(row).find('td:eq(9)').css('color', "#99ff99");
            }
           if (!data.transmitio) {
                $(row).find('td:eq(9)').css('color', '#ff8080');
            }
            if (!data.entrego_urna) {
                $(row).find('td:eq(10)').text('No');
                $(row).find('td:eq(10)').css('color', '#ff8080');
            }
            if (data.entrego_urna) {
                $(row).find('td:eq(10)').text('Si');
                $(row).find('td:eq(10)').css('color', '#99ff99');
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
            url: '{% url "listado-de-locales-urnas" %}',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {
                d.id_distrito = id_distrito
                d.id_subdistrito = id_subdistrito
                d.id_seccion = id_seccion
                d.id_circuito = id_circuito

                d.estado = estado
            },
            headers: { 'X-CSRFToken': csrftoken },

        },
        //https://datatables.net/extensions/buttons/examples/
        //dom: 'Blfrtip', //https://datatables.net/reference/option/dom importante para botones y paginado y demas... fr i
        //dom: "<'row'B><'row'<'mt-3 ml-3'>>ftip",
        columns: [
            {
                data: null,
                defaultContent: '',
                orderable: false,
                className: 'select-checkbox',
            },

            {
                data: 'nombre',
                orderable: true,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    let url='{% url "detalles-local" 99 %}'.replace('99',oData.id)
                    $(nTd).html("<a href='"+ url+ "'>" + sData + "</a>");
                },
            },
            { data: 'circuito__seccion__distrito__distrito', orderable: false },
            { data: 'circuito__seccion__subdistrito__subdistrito', orderable: false },
            { data: 'circuito__seccion__seccion', orderable: false },
            { data: 'circuito__circuito', orderable: false },
            { data: 'cant_mesas_1', orderable: false },
            { data: 'transmite_tel_en_local', orderable: false },
            { data: 'recepciono_mat_elec', orderable: false },
            { data: 'transmitio', orderable: false , defaultContent: "No"},
            { data: 'entrego_urna', orderable: false },

        ],
        dom: "<'row'<'col-md-4'B>><'row'<'mt-4 ml-4'l>>frtip",
        buttons: [
            {
                text: 'Ejecutar acción',
                extend: 'selected',
                //className: 'btn-success',
                className: 'estilo_del_boton_ejecutar',

                action: function (e, dt, button, config) {
                    function ejecutar(){
                        let lista_id = []
                        lista_id = $.map(dt.rows({ selected: true }).data().toArray(), function (item) {
                            return item.id
                        })
                        var parametros = {
                            'accion': accion,
                            'lista_id': JSON.stringify(lista_id)
                        }
                            $.ajax({
                                url: "{% url 'uso-ajax-urnas' %}",
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
                                    tabla_locales_mat_elec_urnas.ajax.reload(null, true);
                                },
                                error: function (jqXHR, textStatus, errorThrown) {
                                    //alert(textStatus + ': ' + errorThrown + ': ' + jqXHR.responseText);
                                    var errorMessage = jqXHR.status + ': ' + jqXHR.statusText
                                    alert('Error - ' + errorMessage + ' - ' + jqXHR.responseText);
                                }
                            });
                            return false;
                    }
                    if (!accion) {
                        Swal.fire({
                             text: "Debe seleccionar una acción",
                             confirmButtonText: 'Aceptar'
                        })
                    }
                    if (accion === 'recmatele'){
                                ejecutar()
                    }
                    if (accion === 'transmitiotelegrama'){
                        let a = dt.rows({ selected: true }).data().toArray();
                        console.log(a)
                        function recMatElect(elemento, indice, arrreglo) {
                            return elemento.recepciono_mat_elec ;
                          }
                        if (a.every(recMatElect)){
                            ejecutar()
                        }
                        else{
                            Swal.fire({
                                text: 'Debe haber recibido el material electoral',
                                confirmButtonText: 'Aceptar'
                            })
                        }
                    }
                    if (accion === 'entregarurna'){

                        let b = dt.rows({ selected: true }).data().toArray();

                        function recMatElectYTel(elemento, indice, arrreglo) {

                            return elemento.recepciono_mat_elec && elemento.transmitio === 'Sí';
                          }

                        if (b.every(recMatElectYTel)){

                            ejecutar()

                        }
                        else{
                            Swal.fire({
                                text: 'Debe haber recibido el material electoral y haber enviado el telegrama',
                                confirmButtonText: 'Aceptar'
                            })
                        }
                    }
                    if (accion === 'norecmatele' || accion === 'noentregarurna' || accion === 'notransmitiotelegrama'){
//                        console.clear()
//                        console.log(accion)
                        if (accion === 'norecmatele'){
                            let h = dt.rows({ selected: true }).data().toArray();
                            function evaluar1(elemento) {
                                return !elemento.transmitio;
                              }
                            if (h.every(evaluar1)){
                                ejecutar()
                            }
                            else{
                                Swal.fire({
                                    text: 'Debe haber no entregado el telegrama y las urnas para no recibir el mate electoral',
                                    confirmButtonText: 'Aceptar'
                                })
                            }
                        }
                        if (accion === 'notransmitiotelegrama'){
                            let z = dt.rows({ selected: true }).data().toArray();
                            function evaluar(elemento) {
                                return !elemento.entrego_urna ;
                              }
                            if (z.every(evaluar)){
                                ejecutar()
                            }
                            else{
                                Swal.fire({
                                    text: 'Debe haber no entregado las urnas para no transmitir telegrama',
                                    confirmButtonText: 'Aceptar'
                                })
                            }
                        }
                        if (accion === 'noentregarurna'){
                            ejecutar()
                        }
                    }
                }
            },
        ],
        drawCallback: function(settings) {
            $.LoadingOverlay("hide");
        },
        //https://datatables.net/extensions/select/integration
        select: {
            style: 'os',
            selector: 'td:first-child'
        },
        //https://datatables.net/extensions/select/integration

        language: {
            decimal: "",
            emptyTable: "Sin locales para visualizar.",
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
            //console.log(json.data)
        }
    });

    {% if request.user.rol == 2 %}
//        circuitos.column(0).visible(false); // or true, if you want to show it
        tabla_locales_mat_elec_urnas.buttons().container().hide()
        $("#accion_urnas").hide()
    {% endif %}

    function RecargarTabla() {
        comprobarSesion()
        tabla_locales_mat_elec_urnas.ajax.reload(null, true);
    };

    //Permite seleccionar todos los chec box juntos para cambiar el estado
    $(".seleccionarTodosLocales1").on("click", function (e) {
        if ($(this).is(":checked")) {
            tabla_locales_mat_elec_urnas.rows().select()
            //var loc = locales.rows({ selected: true, page: 'current' }).data();
            //console.log(loc)
        } else {
            tabla_locales_mat_elec_urnas.rows().deselect();
        }
    });

     $('#accion-urnas').on('change', function () {
        comprobarSesion()
        let valor = $(this).val();
        accion = valor
    });

    $('#filtro-por-estado-urnas').on('change', function () {
        comprobarSesion()
        estado = $(this).val();
        tabla_locales_mat_elec_urnas.ajax.reload(null, true);
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
            let select_distritos = $('select[id="filtro-distrito-recmatele"]')
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
            let select_sub_distritos_para_mapa = $('select[id="filtro-subdistrito-recmatele"]')
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
    $('select[id="filtro-distrito-recmatele"]').on('change', function () {
            var id = $(this).val();
            id_distrito = $(this).val();
            id_subdistrito = '';
            id_seccion ='';
            id_circuito = '';

            select_subdistritos = $('select[id="filtro-subdistrito-recmatele"]')
            select_secciones = $('select[id="filtro-seccion-recmatele"]')
            select_circuitos = $('select[id="filtro-circuito-recmatele"]')

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
//                console.log(respuesta)
                if (!respuesta.hasOwnProperty('error')) {
                    if (respuesta.hay_subdistrito) {
                        $('#sub').show();
                        $('#filtro-subdistrito-recmatele').show();
                        $.each(respuesta.datos, function (key, value) {
                            opciones_subdistritos += '<option value="' + value.id + '">' + value.subdistrito + '</option>';
                        })
                    }
                    if (!respuesta.hay_subdistrito) {
                        $('#sub').hide();
                        $('#filtro-subdistrito-recmatele').hide();
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
    $('select[id="filtro-subdistrito-recmatele"]').on('change', function () {
            var id = $(this).val();
            id_subdistrito = $(this).val();
            id_seccion ='';
            id_circuito = '';

            select_secciones = $('select[id="filtro-seccion-recmatele"]')
            select_circuitos = $('select[id="filtro-circuito-recmatele"]')

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
//                    console.log(respuesta)
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
    $('select[id="filtro-seccion-recmatele"]').on('change', function () {
            var id = $(this).val();
            id_seccion = $(this).val();
            id_circuito = '';

            select_circuitos = $('select[id="filtro-circuito-recmatele"]')

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

    $('select[id="filtro-circuito-recmatele"]').on('change', function (){
            id_circuito = $(this).val();
            RecargarTabla();
        });
});
