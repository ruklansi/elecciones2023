var csrftoken = Cookies.get('csrftoken');
$(function () {
    var estado_prs = '';
    var tabla_lista_prs = $('#tabla').DataTable({
        rowCallback: function (row, data, index) {
            if (data.estado_prs__estado === 0) {
                $(row).find('td:eq(6)').css('color', '#ff8080');
                $(row).find('td:eq(7)').text('--');
            }
            if (data.estado_prs__estado === 1) {
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
            url: "{% url 'listado-puntos-recoleccion-sacas' %}",
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
            { data: 'distrito__distrito', orderable: false, search: false },
            { data: 'direccion', orderable: false, search: false },
            { data: 'denominacion_puesto', orderable: false, search: false },
            { data: 'cant_sacas', orderable: false, search: false },
            { data: 'cant_uupp', orderable: false, search: false },
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
                    let dato = '';
                    if (row.estado_prs__estado === 0){
                        dato = '<span id="cambiar-estado-prs" id_prs="'+row.id+'" title="Estados: No entregado -> Entregado" class="" ><i class="fas fa-arrow-alt-circle-right" style="font-size:15px;color:#99ff99"></i></span>'
                    }
                    if (row.estado_prs__estado === 1){
                        dato = '--'
                    }
                return dato
                }
            },
            {
                data: null,
                class: 'text-center',
                orderable: false,

                render: function (data, type, row) {
                        let buttons = '';
                        let url1='{% url "actualizar-punto-recoleccion-sacas" 99 %}'.replace('99',row.id)
                        let url2='{% url "eliminar-punto-recoleccion-sacas" 979 %}'.replace('979',row.id)
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
                    let mi_url="{% url 'lista-puntos-recoleccion-pdf' %}"
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
            emptyTable: "Sin Puntos que listar",
            info: "Mostrando _START_ a _END_ de _TOTAL_ Puntos",
            infoEmpty: "Mostrando 0 to 0 of 0 Puntos",
            infoFiltered: "(Filtrado de _MAX_ Puntos en total)",
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
        tabla_lista_prs.buttons().container().hide()
      {% endif %}

     //Permite seleccionar todos los chec box juntos para cambiar el estado
     $(".seleccionarTodosPRS").on("click", function (e) {
        if ($(this).is(":checked")) {
        tabla_lista_prs.rows().select()
        } else {
            tabla_lista_prs.rows().deselect();
        }
    });

    function RecargarTabla() {
        tabla_lista_prs.ajax.reload(null, true);
    };
    $('#tabla tbody').on('click', '#cambiar-estado-prs', function () {
        let id = $(this).attr('id_prs');
        Swal.fire({
                text: 'Al cambiar de estado no podrá volver atrás, solo los administradores del sistema pueden hacerlo.',
                showCancelButton: true,
                confirmButtonColor: '',
                cancelButtonColor: '',
                confirmButtonText: 'Cambiar de estado'
            }).then((result) => {
                if (result.value) {
                    $.ajax({
                        url: "{% url 'cambiar-estado-prs' %}",
                        type: "post",
                        headers: { 'X-CSRFToken': csrftoken },
                        dataType: "json",
                        data: { 'id_prs': id },
                        success: function (data) {
                            tabla_lista_prs.ajax.reload(null, true);
                            if (data.cambio_estado) {
                                //alert('si')
                            }
                            else {
                                Swal.fire({
                                    icon: 'error',
                                    title: 'Algo paso',
                                    text: 'Cuando intentaba cambiar el estado del PRS en el servidor!',
                                })
                            }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            alert('Error cambiando de estado de los puntos de recolección de SACAS');
                        }
                    });
                }
            })
    });

});


