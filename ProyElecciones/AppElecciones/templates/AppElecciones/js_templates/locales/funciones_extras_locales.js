var csrftoken = Cookies.get('csrftoken');
$(function () {

        const querystring = window.location.search
        const params = new URLSearchParams(querystring)
        let validado =params.get('validado')
        if (validado == 'no'){
            $('#cancelar_local').attr('href', '{% url "listado-de-locales-novalidados" %}')
        }
        else {
            $('#cancelar_local').attr('href', '{% url "listado-de-locales-validados" %}')
        }
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
        //cargar_distritos()
        var select_subdistritos = '';
        var select_secciones = '';
        var select_circuitos = '';

        var opciones_subdistritos = '';
        var opciones_secciones = '';
        var opciones_circuitos = '';

        $('#distrito').select2({
            theme: "bootstrap4",
            allowClear: true,
            placeholder: 'Seleccione',
        })
        $('#subdistrito').select2({
            theme: "bootstrap4",
            allowClear: true,
            placeholder: 'Seleccione',
        })
        $('#seccion').select2({
            theme: "bootstrap4",
            allowClear: true,
            placeholder: 'Seleccione',
        })
        $('#circuito').select2({
            theme: "bootstrap4",
            allowClear: true,
            placeholder: 'Seleccione',
        })

        $('select[name="distrito"]').on('change', function () {
            comprobarSesion()
            var id = $(this).val();
            //alert(id)
            select_subdistritos = $('select[name="subdistrito"]')
            select_secciones = $('select[name="seccion"]')
            select_circuitos = $('select[name="circuito"]')

            opciones_subdistritos = '<option value="">Todos</option>';
            opciones_secciones = '<option value="">Todos</option>';
            opciones_circuitos = '<option value="">Todos</option>';

            select_subdistritos.html(opciones_subdistritos)
            select_secciones.html(opciones_secciones)
            select_circuitos.html(opciones_circuitos)

            if (id === '') {
                select_subdistrito.html(opciones_subdistritos);
                return false;
            }
            $.ajax({
                url: "{% url 'filtra-campos-local-ajax' %}",
                type: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'filtrar-subdistritos-en-local',
                    'id': id
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
                        //console.log(respuesta)
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
            var id = $(this).val();
            select_secciones = $('select[name="seccion"]')
            select_circuitos = $('select[name="circuito"]')

            opciones_secciones = '<option value="">Todas</option>';
            opciones_circuitos = '<option value="">Todos</option>';

            select_circuitos.html(opciones_circuitos)
            if (id === '') {
                select_secciones.html(opciones_secciones);
                return false;
            }
            $.ajax({
                url: "{% url 'filtra-campos-local-ajax' %}",
                type: 'POST',
                 headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'filtrar-seccion-en-local',
                    'id': id
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
                //console.log(opciones_sec_en_circuito)
                select_secciones.html(opciones_secciones);
            })
        });


        $('select[name="seccion"]').on('change', function () {
            comprobarSesion()
            var id = $(this).val();
            select_circuitos = $('select[name="circuito"]')
            // Sino se seleciono ningun id
            opciones_circuitos = '<option value="">Todos</option>';
            if (id === '') {
                select_circuitos.html(opciones_circuitos);
                return false;
            }
            $.ajax({
                url: "{% url 'filtra-campos-local-ajax' %}",
                type: 'POST',
                 headers: { 'X-CSRFToken': csrftoken },
                data: {
                    'accion': 'filtrar-circuito-en-local',
                    'id': id
                },
                dataType: 'json',
            }).done(function (respuesta) {
                if (!respuesta.hasOwnProperty('error')) {
                    //console.log(respuesta)

                    if (respuesta.hay_circuitos) {
                        //console.log(respuesta.datos)
                        $.each(respuesta.datos, function (key, value) {
                            opciones_circuitos += '<option value="' + value.id + '">' + value.circuito + '</option>';
                        })
                    }
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ':' + errorThrown)
            }).always(function (respuesta) {
                //console.log(opciones_sec_en_circuito)
                select_circuitos.html(opciones_circuitos);
            })
        });
})





