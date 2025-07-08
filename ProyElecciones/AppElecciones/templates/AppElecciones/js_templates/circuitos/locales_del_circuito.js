var csrftoken = Cookies.get('csrftoken');
$(function () {
    var id_circuito = parseInt('{{ object.id }}')
    $.ajax({
        url: '{% url "detalles-del-circuito-ajax" %}',
        type: "post",
        headers: { 'X-CSRFToken': csrftoken },
        dataType: "json",
        data: { 'id': id_circuito },
        success: function (data) {
            //console.log(data)
            var datos = JSON.parse(JSON.stringify(data))
            //console.log(datos)
            let jefe_local = datos.jefe_local
            let auxiliares = datos.auxiliares
            let seg_interna = jefe_local + auxiliares
            let cant_seg_externa = datos.seg_externa
            let cant_novedades = datos.cant_novedades
            let cant_locales = datos.cant_locales

            $('#seg_interna').html(seg_interna)
            $('#seg_externa').html(cant_seg_externa)
            $('#cant_novedades').html(cant_novedades)
            $('#cant_locales').html(cant_locales)


        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert('Error cargando datos de detalles del circuito');
        }
    });
    var tablaLocalesDelCircuito = $('#tabla-locales-del-circuito').DataTable({
        rowCallback: function (row, data, index) {
            if (data.estado__estado == "FINALIZADO") {
                $(row).find('td:eq(6)').css('color', '#1ac6ff');
            }
            if (data.estado__estado == "DESABILITADO") {
                $(row).find('td:eq(6)').css('color', '#ff8080');
            }
            if (data.estado__estado == "HABILITADO") {
                $(row).find('td:eq(6)').css('color', '#99ff99');
            }
            if (data.estado__estado == "INICIADO") {
                //$('td', row).css('background-color', 'pink'); Toda la fila de la tabla
                $(row).find('td:eq(6)').css('color', '#99ff99');
            }
            //Coloreamos el fondo de la celda si la novedad no esta subsanada
            //https://htmlcolorcodes.com/es/tabla-de-colores/
            if (data.nov_subsanada === 1) {
                $(row).find('td:eq(5)').css('background-color', '#f4aba4');
                $(row).find('td:eq(5)').css('color', 'black');
            }

            //console.log(data['tipo_novedad'])
        },
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 50], [5, 50]],
        order: [[0, "des"]],
        ajax: {
            url:'{% url "listar-locales-del-circuito-ajax" %}',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'id_circuito': id_circuito
            },
        },
        columns: [
           {
                data: 'nombre',
                orderable: false,
                fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                    let url='{% url "detalles-local" 99 %}'.replace('99',oData.id)
                    $(nTd).html("<a href='"+ url+ "' data-toggle='tooltip' title='Accede a local'    >" + sData + " </a>");
                },
                orderable: false
            },
            { data: 'jefe_local', orderable: false },
            { data: 'cant_aux', orderable: false },
            { data: 'cant_seg_ext', orderable: false },
            { data: 'cant_mesas', orderable: false },
            { data: 'cant_nov', orderable: false },
            { data: 'estado__estado', orderable: false },
        ],
        language: {
            decimal: "",
            emptyTable: "Este circuito no tiene locales",
            info: "Mostrando _START_ a _END_ de _TOTAL_ locales",
            infoEmpty: "Mostrando 0 to 0 of 0 locales",
            infoFiltered: "(Filtrado de _MAX_ locales en total)",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ locales",
            loadingRecords: "Cargando...",
            processing: "Procesando...",
            search: "Buscar:",
            zeroRecords: "No se encontraron locales",
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