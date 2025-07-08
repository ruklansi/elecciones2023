var csrftoken = Cookies.get('csrftoken');
$(function () {
    let id_local = parseInt('{{ object.id }}')
    $.ajax({
        url: "{% url 'detalles-del-local-ajax' %}",
        type: "post",
        headers: { 'X-CSRFToken': csrftoken },
        dataType: "json",
        data: { 'id': id_local },
        success: function (data) {
            var datos = JSON.parse(JSON.stringify(data))
            //console.log(datos)
            let cant_seg_iterna = datos.seg_interna
            let cant_seg_externa = datos.seg_externa.cant_efectivos__sum
            let cant_novedades = datos.cant_novedades
            let porcentaje_votos = datos.cant_votos.cant_votos__max
            let cant_mesas = datos.cant_mesas
            $('#seg-interna').html(cant_seg_iterna)
            $('#seg-externa').html(cant_seg_externa)
            $('#cant-novedades').html(cant_novedades)
            $('#cant-mesas').html(cant_mesas)
            $('#porcentaje_votos').html(porcentaje_votos + ' %')
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert('Error cargando datos de detalles para resumen en el Local');
        }
    });
    $("#seg-interna").html(id_local)

});
