var csrftoken = Cookies.get('csrftoken');
$(function () {
    var pathArray = window.location.pathname.split('/');
    var id_seccion = pathArray[pathArray.length-1]
    $.ajax({
        url: '{% url "resumn-de-la-seccion-ajax" %}',
        type: "post",
        headers: { 'X-CSRFToken': csrftoken },
        dataType: "json",
        data: { 'id': id_seccion },
        success: function (data) {
            //console.log(data)
            var datos = JSON.parse(JSON.stringify(data))
//            console.log(datos)

            let organico_esta_seccion = datos.organico_esta_seccion
            let seg_interna = datos.seg_interna
            let seg_externa = datos.seg_externa
            let total_personal_seccion = datos.total_personal_seccion

            let organizacion = datos.organizacion
            let cant_circuitos = datos.cant_circuitos
            let cant_locales = datos.cant_locales
            let cant_novedades = datos.cant_novedades

            let nov_baja = datos.nov_baja
            let nov_media = datos.nov_media
            let nov_alta = datos.nov_alta
            let nov_critica = datos.nov_critica
            let total_vehiculos = datos.total_vehiculos
            let veh_propios = datos.veh_propios
            let veh_contratados = datos.veh_contratados

            $('#organico_esta_seccion').html(organico_esta_seccion)
            $('#seg_interna').html(seg_interna)
            $('#seg_externa').html(seg_externa)
            $('#total_personal_seccion').html(total_personal_seccion)

            $('#organizacion').html(organizacion)
            $('#cant_circuitos').html(cant_circuitos)
            $('#cant_locales').html(cant_locales)

            $('#cant_novedades').html(cant_novedades)
            $('#nov_baja').html(nov_baja)
            $('#nov_media').html(nov_media)
            $('#nov_alta').html(nov_alta)
            $('#nov_critica').html(nov_critica)
            $('#total_vehiculos').html(total_vehiculos)
            $('#veh_propios').html(veh_propios)
            $('#veh_contratados').html(veh_contratados)
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert('Error cargando datos de resumen para tarjetas de la Sección');
        }
    });
});