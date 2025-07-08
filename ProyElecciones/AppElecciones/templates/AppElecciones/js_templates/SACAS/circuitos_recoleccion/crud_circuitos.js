var csrftoken = Cookies.get('csrftoken');
$(function () {
    var estado_prs = '';
    var tabla_lista_crs = $('#tabla').DataTable({
        rowCallback: function (row, data, index) {
            if (data.id_estado === 0) {
               $(row).find('td:eq(6)').css('color', '#ff8080');
               $(row).find('td:eq(7)').text('--');
           }
            if (data.id_estado === 1 || data.id_estado === 2 || data.id_estado === 3) {
                $(row).find('td:eq(6)').css('color', '#1ac6ff');
               $(row).find('td:eq(7)').css('color', '#1ac6ff')
            }
        },
        //select: true,
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 10], [5, 10]],
        order: [[1, "asc"]],
        //paging: false,
        //bFilter: false,
        ajax: {
            url: "{% url 'listado-circuitos-recoleccion-sacas' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
        },
        columns: [
            {
                data: null,
                defaultContent: '',
                orderable: false,
                className: 'select-checkbox',
            },
            {
                className: 'details-control',
                orderable: false,
                data: null,
                defaultContent: ''
            },
            { data: 'distrito__distrito', orderable: false, search: false },
            { data: 'ctrs', orderable: false, search: false },
            { data: 'cant_personal', orderable: false, search: false },
            { data: 'vehiculo', orderable: false, search: false },
            { data: 'estado', orderable: false, search: false },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                moment.locale('es');
                return moment(row.historial_estados__fecha).format('L LT');
                }
            },
            {
                data: null,
                orderable: false,
                class: 'text-center',
                render: function (data, type, row) {
                    let dato = '<span id="cambiar-estado-crs" id_crs="'+row.id+'" title="Estados: ENTREGÓ SACAS EN LA CNE->INICIÓ REPLIEGUE->REPLEGADO" class="" ><i class="fas fa-arrow-alt-circle-right" style="font-size:15px;color:#99ff99"></i></span>';
                return dato
                }
            },
            {
                data: null,
                class: 'text-center',
                orderable: false,

                render: function (data, type, row) {
                        let buttons = '';
                        let url1='{% url "actualizar-circuito-recoleccion-sacas" 991 %}'.replace('991',row.id)
                        let url2='{% url "eliminar-circuito-recoleccion-sacas" 971 %}'.replace('971',row.id)
                        if (row.editar) {
                            buttons += '<a title="Editar" href="'+url1+'" class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></a> ' + '&nbsp;&nbsp';
                        }
                        if (row.eliminar) {
                            buttons += '<a title="Eliminar" href="'+url2+'" type="button" class=""><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></a>';
                        }
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
                className: 'mipdf',

                action: function (e, dt, button, config) {
                    var lista_id = []
                    lista_id = $.map(dt.rows({ selected: true }).data().toArray(), function (item) {
                        return item.id

                    })
                    let mi_url="{% url 'lista-circuitos-recoleccion-pdf' %}"
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
            emptyTable: "Sin Circuitos que listar",
            info: "Mostrando _START_ a _END_ de _TOTAL_ Puntos",
            infoEmpty: "Mostrando 0 to 0 of 0 Circuitos",
            infoFiltered: "(Filtrado de _MAX_ Circuitos en total)",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ Puntos",
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
        tabla_lista_crs.buttons().container().hide()
      {% endif %}

     //Permite seleccionar todos los chec box juntos para cambiar el estado
     $(".seleccionarTodosPRS").on("click", function (e) {
        if ($(this).is(":checked")) {
        tabla_lista_crs.rows().select()
        } else {
            tabla_lista_crs.rows().deselect();
        }
    });

    function RecargarTabla() {
        tabla_lista_crs.ajax.reload(null, true);
    };
    $('#tabla tbody').on('click', '#cambiar-estado-crs', function () {
        let id = $(this).attr('id_crs');
        Swal.fire({
                text: 'Al cambiar de estado no podrá volver atrás, solo los administradores del sistema pueden hacerlo.',
                showCancelButton: true,
                confirmButtonColor: '',
                cancelButtonColor: '',
                confirmButtonText: 'Cambiar de estado'
            }).then((result) => {
                if (result.value) {
                    $.ajax({
                        url: "{% url 'cambiar-estado-crs' %}",
                        type: "post",
                        headers: { 'X-CSRFToken': csrftoken },
                        dataType: "json",
                        data: { 'id_crs': id },
                        success: function (data) {
                            if (data.cambio_estado) {
                                tabla_lista_crs.ajax.reload(null, true);
//                                alert('si')
                            }
                            else {
                                Swal.fire({
                                    icon: 'error',
                                    title: 'Algo paso',
                                    text: 'Cuando intentaba cambiar el estado del CRS en el servidor!',
                                })
                            }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            alert('Error cambiando de estado de los circuitos de recolección de SACAS');
                        }
                    });
                }
            })

    });

     function Hijos(d) {
        //console.log(d.id)
        id_ctrs = d.id
        var div = $('<div/>')
            .addClass('cargando')
            .text('Cargando...');



        $.ajax({
            url: "{% url 'mostrar-hijos-ctrs' %}",
            type: "post",
            headers: { 'X-CSRFToken': csrftoken },
            dataType: "json",
            data: { 'id_ctrs': id_ctrs },
            success: function (data) {
                console.log(data)

                      let mostrar = '<span class="visor_imagenes">Puntos de reunión</span>' + '<br>';
                      let total_sac = 0;
                    $.each(data, function (i, d) {

                        if (d.estado) {//filtro si hay estado ya que el primero que se le asigna tiene indefinido el estado
                            if (d.estado === 'NO ENTREGADO') {
                                var a = '-----'

                            } else {
                                a = moment(d.estado.fecha).format('L LT')


                            }
                            mostrar += '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">' +
                                '<tr>' +
                                '<td>Puesto:</td>' +
                                '<td>' + d.puesto + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                '<td>Dirección:</td>' +
                                '<td>' + d.direccion + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                '<td>Estado:</td>' +
                                '<td class="visor_imagenes">' + d.estado + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                '<td>SACAS transportadas:</td>' +
                                '<td class="resaltar">' + d.cant_sacas + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                '<td>Fecha:</td>' +
                                '<td class="">' + a + '</td>' +
                                '</tr>' +
                                '</table> <br>'
                                total_sac += d.cant_sacas;
                        }

                    })

                    mostrar += '<span>Total de sacas transportadas: <span class="resaltar">'+  total_sac +'</span> </span>' + '<br>'
                    div.html(mostrar).removeClass('loading');
                    mostrar += 'hola'

                /*
                if (data.hay_datos === 'False') {

                    var mostrar = '<span class="visor_imagenes">Sin puntos de Recolección que mostrar. Agregue los mismos en la opción SACAS->Puntos de recolección</span>' + '<br>';
                    div.html(mostrar).removeClass('loading');
                }*/
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert('Error cargando puntos de recolección  del ctrs');
            }
        });
        return div

    }

    // Agregar un evento para cuando se abra o cierra
    $('#tabla tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = tabla_lista_crs.row(tr);
        if (row.child.isShown()) {
            // Este fila esta abierta - la cerramos
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Abrir la fila
            //row.child(Auxiliares(row.data())).show();
            row.child(Hijos(row.data())).show();
            tr.addClass('shown');
        }
    });

});


