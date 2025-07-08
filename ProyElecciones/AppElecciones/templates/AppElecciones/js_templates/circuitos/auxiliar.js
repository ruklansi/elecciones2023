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

        var select_subdistritos = '';
        var select_secciones = '';

        var opciones_subdistritos = '';
        var opciones_secciones = '';


        $('#distrito').select2({
            theme: "bootstrap4",
            language: 'es',
            allowClear: true,
            placeholder: 'Seleccione'
        });
        $('#subdistrito').select2({
            theme: "bootstrap4",
            language: 'es',
            allowClear: true,
            placeholder: 'Seleccione'
        });
        $('#seccion').select2({
            theme: "bootstrap4",
            language: 'es',
            allowClear: true,
            placeholder: 'Seleccione'
        });

        $('select[name="distrito"]').on('change', function () {
            comprobarSesion()
            let id_distrito = $(this).val();

            select_subdistritos = $('select[name="subdistrito"]')
            select_secciones = $('select[name="seccion"]')


            opciones_subdistritos = '<option value="">Todos</option>';
            opciones_secciones = '<option value="">Todos</option>';

            select_subdistritos.html(opciones_subdistritos)
            select_secciones.html(opciones_secciones)


            if (id_distrito === '') {
                select_subdistrito.html(opciones_subdistritos);
                return false;
            }
            $.ajax({
                url: '{% url "filtra-campos-circuito-ajax" %}',
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'filtrar-subdistritos-en-circuito',
                    'id': id_distrito
                },
                dataType: 'json',
            }).done(function (respuesta) {
                if (!respuesta.hasOwnProperty('error')) {

                    if (respuesta.hay_subdistrito) {
                        //sub.show();
                        //console.log(respuesta.hay_subdistrito)
                        $.each(respuesta.datos, function (key, value) {
                            opciones_subdistritos += '<option value="' + value.id + '">' + value.subdistrito + '</option>';
                        })
                    }
                    if (!respuesta.hay_subdistrito) {
                        //sub.hide();
                        //console.log(respuesta.hay_subdistrito)
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

        $('select[name="subdistrito"]').on('change', function () {
            comprobarSesion()
            let id_sub = $(this).val();
            select_secciones = $('select[name="seccion"]')
            opciones_secciones = '<option value="">Todas</option>';
            if (id_sub === '') {
                select_secciones.html(opciones_secciones);
                return false;
            }
            $.ajax({
                url: '{% url "filtra-campos-circuito-ajax" %}',
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'filtrar-seccion-en-circuito',
                    'id': id_sub
                },
                dataType: 'json',
            }).done(function (respuesta) {
                if (!respuesta.hasOwnProperty('error')) {
                    //console.log(respuesta)
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
                select_secciones.html(opciones_secciones);
            })
        });
});