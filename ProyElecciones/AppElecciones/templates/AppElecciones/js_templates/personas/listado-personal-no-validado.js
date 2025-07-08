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

    cargar_fuerzas()

    var fuerza = '';

    var tablaPersonasNoValidadas = $('#tabla').DataTable({
        rowCallback: function (row, data, index) {},
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
            url: "{% url 'listado-de-personal-no-validado' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: function (d) {
                d.fuerza = fuerza
            },
        },
        dom: '<"titulo">lfrtip',
        columns: [
            { data: 'grado__grado', orderable: false },
            { data: 'nombre', orderable: false },
            { data: 'apellido', orderable: true },
            { data: 'dni', orderable: true },
            { data: 'fuerza__fuerza', orderable: false },
            { data: 'nro_tel', orderable: false},
            {
                data: null,
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {

                    let buttons = '';
                    buttons = '<span id="validar_pers" id_persona="'+row.id+'" grado="'+row.grado__grado+'" nombre="'+ row.nombre +'" apellido="'+ row.apellido +'" fuerza="'+ row.fuerza__fuerza +'" nro_tel="'+ row.nro_tel+'" dni="'+ row.dni+'" title="Confirmar persona" class="" ><i class="fas fa-solid fa-user-check" style="font-size:15px;color:#70dbdb"></i></span>' + '&nbsp;&nbsp';
                    return buttons;
                }
            }
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

    // Validar la persona via ajax
    $('#tabla tbody').on('click', '#validar_pers', function () {
        comprobarSesion()
        let id_persona = $(this).attr('id_persona');
        let grado = $(this).attr('grado');
        let nombre = $(this).attr('nombre');
        let apellido = $(this).attr('apellido');
        let dni = $(this).attr('dni');
        let fuerza = $(this).attr('fuerza');
        let url_= "{% url 'actualizar-persona' 0 %}"
        Swal.fire({
                 title: '<strong>Seleccionar persona</strong>',
                 html:
                    '<p>Confirma que esta persona va a formar parte de su Organización:</p> ' +
                    '<p>Grado: '+grado+'</p> ' +
                    '<p>Nombre: '+nombre+'</p> ' +
                    '<p>Apellido: '+apellido+'</p> ' +
                    '<p>DNI: '+dni+'</p> ' +
                    '<p>Fuerza: '+fuerza+'</p> ',
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
                        data: {'accion':'validar_personal', 'id_persona': id_persona},
                        success: function (data) {
                            if (data.validado) {
                                RecargarTabla();
//                                Swal.fire({
//                                  position: 'center',
//                                  text: data['mensaje'],
//                                  showConfirmButton: true,
//                                });
                            }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                                alert('Error eliminando vehículo contratado');
                        }
                    });
                }
            })
    });


    function RecargarTabla() {
        comprobarSesion()
        tablaPersonasNoValidadas.ajax.reload(null, true);
    };

    function cargar_fuerzas() {
        var valores_fuerzas = '<option value="">Todos</option>';
        var select_fuerzas = $('select[id="filtro-fuerza-para-personal"]')
        $.ajax({
            url: "{% url 'filtros-para-personas' %}",
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'accion': 'cargar-fuerzas-pers-no-validado'
            },
            dataType: 'json',
        }).done(function (data) {
            if (!data.hasOwnProperty('error')) {
                if (data.hay_fuerza) {
                    $.each(data.datos, function (key, value) {
                        valores_fuerzas += '<option value="' + value.id + '">' + value.fuerza + '</option>';
                    })
                }
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(textStatus + ':' + errorThrown)
        }).always(function (data) {
            select_fuerzas.html(valores_fuerzas);
        });
    }

    $('#filtro-fuerza-para-personal').on('change', function () {
        comprobarSesion()
        fuerza = $(this).val();
        RecargarTabla();
    });

});

