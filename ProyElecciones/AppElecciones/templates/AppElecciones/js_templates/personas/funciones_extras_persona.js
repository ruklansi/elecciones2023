var csrftoken = Cookies.get('csrftoken');
$(function () {
    const querystring = window.location.search
    const params = new URLSearchParams(querystring)
    let validado =params.get('validado')
    if (validado == 'no'){
        $('#cancelar').attr('href', '{% url "listado-de-personal-no-validado" %}')
    }
    else {
        $('#cancelar').attr('href', '{% url "listado-de-personas" %}')
    }
    $('#grado').select2({
            theme: "bootstrap4",
            allowClear: true,
            placeholder: 'Seleccione',
    })
    $('#id_fuerza').select2({
            theme: "bootstrap4",
            allowClear: true,
            placeholder: 'Seleccione',
    })
    $('#id_validado_persona').select2({
            theme: "bootstrap4",
            allowClear: true,
            placeholder: 'Seleccione',
    })
    $('select[id="id_fuerza"]').on('change', function () {
        var id = $(this).val();

        var valores = '<option value="">Seleccione</option>';
        var select_grado = $('select[id="grado"]')
        select_grado.html(valores)

         if (id === '') {
                select_grado.html(valores);
                return false;
            }
        $.ajax({
            url: '{% url "listar-fuerza-para-personal" %}',
            type: 'post',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'accion': 'cargar-grado',
                'id': id
            },
            dataType: 'json',
        }).done(function (data) {
            if (!data.hasOwnProperty('error')) {
                $.each(data, function (key, value) {
                    valores += '<option value="' + value.id + '">' + value.grado + '</option>';
                })
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(textStatus + ':' + errorThrown)
        }).always(function (data) {
            select_grado.html(valores);
        });


    });
});