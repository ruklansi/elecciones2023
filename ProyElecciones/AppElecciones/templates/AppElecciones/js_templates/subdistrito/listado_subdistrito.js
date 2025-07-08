var csrftoken = Cookies.get('csrftoken');
$(function () {
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

    var tablaSubdistritos = $('#tabla').DataTable({
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
        },
        columns: [

            { data: 'subdistrito', orderable: false },
            { data: 'detalle', orderable: false },
            { data: 'distrito__distrito', orderable: false },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var url='{% url "detalles-subdistito" 99 %}'.replace('99',row.id)
                    var buttons = '<a title="Registro de personal, reserva y vehículos" href="'+url+'" class="" ><i class="fas fa-address-card" style="font-size:15px;color:goldenrod"></i></a> ' + '&nbsp;&nbsp';
                    return buttons;
                }
            }
        ],
        language: {
            decimal: "",
            emptyTable: "No hay subdistritos para mostrar",
            info: "Mostrando _START_ a _END_ de _TOTAL_ subdistritos",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
            infoFiltered: "(Filtrado de _MAX_ subdistritos en total)",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ subdistritos",
            loadingRecords: "Cargando...",
            processing: "Procesando...",
            search: "Buscar:",
            zeroRecords: "No hay subdistritos para mostrar",
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

});

