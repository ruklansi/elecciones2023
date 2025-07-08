var csrftoken = Cookies.get('csrftoken');
$(function () {
    var tablaDistritos = $('#tabla').DataTable({
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
            { data: 'distrito', orderable: false },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var url='{% url "detalles-distito" 9 %}'.replace('9',row.id)
                    var buttons = '<a title="Registro de personal, reserva y vehículos" href="'+url+'" class="" ><i class="fas fa-address-card" style="font-size:15px;color:goldenrod"></i></a> ' + '&nbsp;&nbsp';
                    return buttons;
                }
            }
        ],
        language: {
            decimal: "",
            emptyTable: "No hay distritos para mostrar",
            info: "Mostrando _START_ a _END_ de _TOTAL_ distritos",
            infoEmpty: "Mostrando 0 to 0 of 0 distritos",
            infoFiltered: "(Filtrado de _MAX_ distritos en total)",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ distritos",
            loadingRecords: "Cargando...",
            processing: "Procesando...",
            search: "Buscar:",
            zeroRecords: "No hay distritos para mostrar",
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