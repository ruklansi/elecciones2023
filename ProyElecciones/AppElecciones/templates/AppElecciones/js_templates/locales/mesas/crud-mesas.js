var csrftoken = Cookies.get('csrftoken');
$(function () {
    $("#pills-mesas-tab").click(function () {
        RecargarTabla();
    });
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
    let id_local = parseInt('{{ object.id }}')
    var tabla_mesas = $('#tablamesaslocal').DataTable({
        //select: true,
        responsive: true,
        autoWidth: true,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        lengthMenu: [[5, 10], [5, 10]],
        pageLength: 5,
        order: [[0, "asc"]],
        //paging: false,
        //bFilter: false,
        ajax: {
            url:  "{% url 'listado-de-mesas-en-local' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'id_local': id_local
            },
        },
        columns: [
            { data: 'mesas', orderable: false},
//            { data: 'cant_electores', orderable: false},
            { data: 'voto_', orderable: false},
            {
                data: null,
                orderable: false,
                render:  function(data, type, row){
                    let boton = '';
                    if (row.editar){
                        boton += '<span id="editar-mesa" title="Editar" id_edit_mesa="'+row.id+'"  class="" ><i class="fas fa-edit" style="font-size:15px;color:yellowgreen"></i></span> ' + '&nbsp;&nbsp'
                    }
                    if (row.eliminar){
                        boton += '<span id="elimiar-mesa" title="Eliminar" id_del_mesa="'+row.id+'"  class="" ><i class="fas fa-trash-alt" style="font-size:15px;color:red"></i></span>'
                    }
                    return boton
                }
            }
        ],
        language: {
            decimal: "",
            emptyTable: "Sin resultados encontrados",
            info: "Mostrando _START_ a _END_ de _TOTAL_ Registros",
            infoEmpty: "Mostrando 0 to 0 of 0 Entradas",
            infoFiltered: "(Filtrado de _MAX_ registros en total)",
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
    });
    //Otra forma de obtener datos del datatables para futuros usos
    //var info = tabla_seg_interna.page.info();
    //console.log(info.recordsTotal);
    function RecargarTabla() {
        comprobarSesion()
        tabla_mesas.ajax.reload(null, true);
    };
    var MostrarFormularioMesasLocal = function () {
        comprobarSesion()
        var boton = $(this);
        $.ajax({
            url: boton.attr("data-url"),
            type: "get",
            dataType: "json",
            data: { 'id_local': id_local },
            beforeSend: function () {
            },
            success: function (data) {
                $('#modal-mesas-en-local .modal-content').html(data.html_form);
                $('#modal-mesas-en-local').modal('show')
                $('#id_voto').select2({
                    theme: "bootstrap4",
                    allowClear: true,
                    placeholder: 'Seleccione',
                });
            }
        });
    };
    var GuardarFormularioMesasLocal = function () {
        comprobarSesion()
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('data-url'),
            data: form.serialize() + "&id_local=" + id_local,
            dataType: "json",
            headers: { 'X-CSRFToken': csrftoken },
            success: function (data) {
                if (data.form_es_valido) {
                    //$('#boton-agregar').hide()
                    $('#modal-mesas-en-local').modal('hide');
                    RecargarTabla();
                    Swal.fire({
                                     position: 'center',
                                     text: data['mensaje'],
                                     showConfirmButton: false,
                                     timer: 1500
                                 });
                }
                else {
                    $('#modal-mesas-en-local .modal-content').html(data.html_form);
                    $('#id_voto').select2({
                        theme: "bootstrap4",
                        allowClear: true,
                        placeholder: 'Seleccione',
                    });
                }
            }
        })
        return false;
    };
    $('#mostrar-modal-mesas').click(MostrarFormularioMesasLocal)
    $("#modal-mesas-en-local").on("submit", ".agregar-mesa", GuardarFormularioMesasLocal)
    $("#modal-mesas-en-local").on("submit", ".actualizar-mesa", GuardarFormularioMesasLocal);
    $('#tablamesaslocal tbody').on('click', '#editar-mesa', function () {
        comprobarSesion()
        var id = $(this).attr('id_edit_mesa');
        $.ajax({
            url: "{% url 'actualizar-mesas-en-local' 991 %}".replace('991',id),
            type: "get",
            dataType: "json",
            success: function (data) {
                $('#modal-mesas-en-local .modal-content').html(data.html_form);
                $('#modal-mesas-en-local').modal('show')
                $('#id_voto').select2({
                    theme: "bootstrap4",
                    allowClear: true,
                    placeholder: 'Seleccione',
                });
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert('Error modificando datos de mesas en local');
            }
        });
    });
    $('#tablamesaslocal tbody').on('click', '#elimiar-mesa', function () {
        comprobarSesion()
        var id = $(this).attr('id_del_mesa');
        Swal.fire({
            //title: 'Borrar este registro ?',
            text: "Borrar este registro",
//            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: 'Cancelar',
            confirmButtonText: 'Sí, borrarlo'
        }).then((result) => {
            if (result.value) {
                $.ajax({
                    url: "{% url 'eliminar-mesas-en-local' 991 %}".replace('991',id),
                    type: "get",
                    dataType: "json",
                    success: function (data) {
                        if (data.borrado) {
                            RecargarTabla();
                            Swal.fire({
                                     position: 'center',
                                     text: data['mensaje'],
                                     showConfirmButton: false,
                                     timer: 1500
                                 });
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        alert('Error borrando mesas');
                    }
                });
            }
        })
    });
});


