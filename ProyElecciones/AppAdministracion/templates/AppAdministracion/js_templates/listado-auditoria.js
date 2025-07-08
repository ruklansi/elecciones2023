var csrftoken = Cookies.get('csrftoken');
$(function () {
    $.ajaxSetup({
        statusCode: {
          403: function (xhr, errmsg, err) {
            window.location = xhr.responseJSON.redirect_to;
          }
        },
      });
      function comprobarSesion() {
        $.ajax({
          url: window.location.pathname,
          type: "get",
          dataType: "json",
        });
      };

    var rango_fechas = null;
    var fecha_inicio_de_hoy = new moment().format('YYYY-MM-DD 00:00:00');
    var fecha_fin_de_hoy = new moment().format('YYYY-MM-DD 23:59:59');
    var fecha_inicio = fecha_inicio_de_hoy;
    var fecha_fin = fecha_fin_de_hoy;


    var pe = $('#id_rango_fechas').daterangepicker({
        cancelButtonClasses: 'btn-danger',
        applyButtonClasses: 'btn-success',
        locale :{
            //format: 'YYYY-MM-DD',
            applyLabel:  '<i class="fas fa-chart-pie"></i> Aplicar',
            cancelLabel: '<i class="fas fa-times"></i> Cancelar',
        }

    }).on('apply.daterangepicker', function (ev, picker){
        rango_fechas = picker;
        if (rango_fechas != null){
            fecha_inicio = rango_fechas.startDate.format('YYYY-MM-DD HH:mm:ss')
            fecha_fin = rango_fechas.endDate.format('YYYY-MM-DD HH:mm:ss')
            tablaAuditoria.ajax.reload(null, true);
        }
        //console.log(picker.startDate.format('MM/DD/YYYY'))
    }).on('cancel.daterangepicker', function(ev, picker){
        if (rango_fechas != null){
            $(this).val('');
            //  $(this).data('daterangepicker').setStartDate(new moment().format('YYYY-MM-DD'));
            //  $(this).data('daterangepicker').setEndDate(new moment().format('YYYY-MM-DD'));
        }
        fecha_inicio = fecha_inicio_de_hoy;
        fecha_fin = fecha_fin_de_hoy;
         tablaAuditoria.ajax.reload(null, true);
    });

    //console.log(window.location.pathname)
    var tablaAuditoria = $('#tabla').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[50, 100], [50, 100]],
        order: [[0, "asc"]],
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            error: function(jqXHR) {
                if(jqXHR.status == 403) {
                    window.location = jqXHR.responseJSON.redirect_to;
                }
            },
           // data: parametros,
           data: function (d) {
            d.fecha_inicio = fecha_inicio,
            d.fecha_fin = fecha_fin

        },
            /*
            dataSrc: function(data){
                $('#mostrar_personal').html(data.pepe)
                return data.data
            },*/
        },
        //dom: '<"titulo">lfrtip',
        columns: [
           {    class: 'text_center',
                orderable: true,
                render: function (data, type, row) {
                    moment.locale("es");
                    return moment(row.timestamp).format("DD/MM/YYYY HH:mm");
                }
           },
           { class: 'text_center',
                orderable: false,
                render: function (data, type, row) {
                    let nombre = '';
                    nombre = row.actor_id__first_name +' '+ row.actor_id__last_name
                    return nombre
                },
           },
           {    class: 'text_center',
                orderable: false,
                render: function (data, type, row) {
                    let accion = '';
                    if (row.action === 1){
                        accion = 'Actualizó el registro'
                    }
                    if (row.action === 2){
                        accion = 'Eliminó el registro'
                    }
                    if (row.action === 0){
                        accion = 'Creó un nuevo registro'
                    }
                    return accion
                }
           },
           { data: 'object_repr', orderable: false },
           { data: 'content_type__model', orderable: false },


        ],
        language: {
            decimal: "",
            emptyTable: "Sin resultados encontrados",
            info: "Mostrando _START_ a _END_ de _TOTAL_ Registros",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
            infoFiltered: "",
            infoPostFix: "",
            thousands: ",",
            lengthMenu: "Mostrar _MENU_ Registros",
            loadingRecords: "Cargando...",
            processing: "Procesando...",
            search: "Buscar:",
            zeroRecords: "Sin resultados encontrados",
            paginate: {
                first: "Primero",
                last: "Ultimo",
                next: "Siguiente",
                previous: "Anterior"
            }
        },
        initComplete: function (settings, json) {}
    });
    var Recargartabla = function () {
        comprobarSesion()
        pe.data('daterangepicker').setStartDate(fecha_inicio_de_hoy);
        pe.data('daterangepicker').setEndDate(fecha_fin_de_hoy);
        fecha_inicio = new moment().format('YYYY-MM-DD 00:00:00');
        fecha_fin = new moment().format('YYYY-MM-DD 23:59:59');
        tablaAuditoria.ajax.reload(null, true);
    };
    $('#mostrar-auditoria-de-hoy').click(Recargartabla)

});