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



    var tablaPersonas = $('#tabla').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 10], [5, 10]],
        order: [[0, "asc"]],
        ajax: {
            url: "{% url 'listado-de-usuarios' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            error: function(jqXHR) {
                if(jqXHR.status == 403) {
                    window.location = jqXHR.responseJSON.redirect_to;
                }
            }
        },
        //dom: '<"titulo">lfrtip',
        columns: [
            { data: 'username', orderable: true },
            { data: 'first_name', orderable: true },
            { data: 'last_name', orderable: true },
            { data: 'dni', orderable: true },
            { data: 'nro_tel', orderable: true },
            {
                class: 'text_center',
                orderable: false,
                render: function (data, type, row) {

                    let html = '';
                    let rol = ''
                    if (row.rol === 1){
//                        console.log(row.rol)
                        rol = 'adminsistema'
                        html += '<span class="badge badge-warning">' + rol + '</span> ';
                    }
                    if (row.rol === 2){
//                        console.log(row.rol)
                        rol = 'Lector-CGE'
                        html += '<span class="badge badge-warning">' + rol + '</span> ';
                    }
                    if (row.rol === 3){
//                        console.log(row.rol)
                        rol = 'Distrito'
                        html += '<span class="badge badge-warning">' + rol + '</span> ';
                    }
                     if (row.rol === 4){
//                        console.log(row.rol)
                        rol = 'Subdistrito'
                        html += '<span class="badge badge-warning">' + rol + '</span> ';
                    }
                     if (row.rol === 5){
//                        console.log(row.rol)
                        rol = 'Seccion'
                        html += '<span class="badge badge-warning">' + rol + '</span> ';
                    }
                     if (row.rol === 6){
//                        console.log(row.rol)
                        rol = 'Circuito'
                        html += '<span class="badge badge-warning">' + rol + '</span> ';
                    }
                     if (row.rol === 7){
//                        console.log(row.rol)
                        rol = 'Personal'
                        html += '<span class="badge badge-warning">' + rol + '</span> ';
                    }
                     if (row.rol === 8){
//                        console.log(row.rol)
                        rol = 'Logística'
                        html += '<span class="badge badge-warning">' + rol + '</span> ';
                    }
                     if (row.rol === 9){
//                        console.log(row.rol)
                        rol = 'personal-CGE'
                        html += '<span class="badge badge-warning">' + rol + '</span> ';
                    }
                    if (row.rol === 10){
//                        console.log(row.rol)
                        rol = 'material-CGE'
                        html += '<span class="badge badge-warning">' + rol + '</span> ';
                    }
                    return html
                }
           },
            {
                class: 'text_center',
                orderable: false,
                render: function (data, type, row) {
                     let html = '';
                     html += '<div class="badge badge-warning">'+row.grupo_organizacion__name+'</span>';
                     return html;

                 }
             },
            { data: 'email', orderable: false },
             {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data,type, row) {
                moment.locale('es');
               let f_reseteo=row.last_login;
                if (!f_reseteo){
                  f_reseteo='No se logueo'
                    }else{
                f_reseteo=moment(row.last_login).format('LLL ')
                }

                return f_reseteo;
                }
            },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data,type,row) {
                moment.locale('es');
                let f_reseteo=row.fecha_reseteo;
                if (!f_reseteo){
                  f_reseteo='No Reseteado'
                    }else{
                f_reseteo=moment(row.fecha_reseteo).format('LLL ')
                }

                return f_reseteo;
                }
            },
            { data: 'tipo_reset', orderable: false },
            {

                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return '<button class="btn-success">Resetear</button>';
                }
            },
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = ''
                          buttons += '<a title="Editar" href="'+'{% url "actualizar-usuario" 9999 %}'.replace('9999',row.id)+'" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></a> ' + '&nbsp;&nbsp';
                          buttons += '<span id="elimiar-usuario" id_usuario="'+row.id+'" usuario="'+row.first_name +' '+ row.last_name+'" title="Eliminar" class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span> ' + '&nbsp;&nbsp'
                    return buttons;
                }
            }
        ],
        language: {
            decimal: "",
            emptyTable: "Sin resultados encontrados",
            info: "Mostrando _START_ a _END_ de _TOTAL_ Registros",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
//            infoFiltered: "(Filtrado de _MAX_ registros en total)",
            infoFiltered: '',
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

        initComplete: function (settings, json) {
            //console.log(json)
         }
    });

    $('#tabla tbody').on('click', 'button', function () {
       var data = tablaPersonas.row($(this).parents('tr')).data();
       $.ajax({
            url: "{% url 'reser-via-ajax' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            dataType: 'json',
            data : {
                'correo': data.email
            },
            beforeSend: function () {
                $.LoadingOverlay("show",
                    {
                        background      : "rgba(0, 0, 0, 0.5)",
                        imageAnimation  : "1.5s fadein",
                        imageColor      : "#ffcc00",
//                        text            : "Registrando % de voto...."
                    });
            },
        }).done(function (resultado) {
            if (!data.hasOwnProperty('error')) {
                $.LoadingOverlay("hide");
                RecargarTabla();
                Swal.fire({
                    text: resultado.enviado,
                    confirmButtonText: 'Aceptar'
                })
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(textStatus + ':' + errorThrown)
        }).always(function (resultado) {

        });
    });
    function RecargarTabla() {
        comprobarSesion()
        tablaPersonas.ajax.reload(null, true);
    };

    $('#tabla tbody').on('click', '#elimiar-usuario', function () {
        comprobarSesion()
        var id = $(this).attr('id_usuario');
        var  usuario = $(this).attr('usuario');
        setTimeout(function() {
            Swal.fire({
                //title: 'Elimiar usuario',
                text: "Esta por eliminar el usuario " + usuario,
                //icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#999999',
                confirmButtonText: 'Eliminarlo'
            }).then((result) => {
                if (result.value) {
                    $.ajax({
                        url: "{% url 'eliminar-usuario' 0 %}".replace('0',id),
                        type: "get",
                        dataType: "json",
                        success: function (data) {
                           if (data.borrado) {
                                 RecargarTabla();
                                Swal.fire({
                                  position: 'center',
                                  //icon: 'success',
                                  text: data['mensaje'],
                                  showConfirmButton: false,
                                  timer: 1500
                                });
                            }
                             if (!data.borrado){
                                    Swal.fire({
                                        //position: 'top-end',
                                        //icon: 'error',
                                        text: data['mierror'],
                                        showConfirmButton: false,
                                        timer: 7000
                                      })
                                }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                                alert('Error al eliminar usuarios');
                        }
                    });
                }
            })
        },200)
    });
});