var csrftoken = Cookies.get('csrftoken');
$(function () {
    var pathArray = window.location.pathname.split('/');
    var id_subdistrito = pathArray[pathArray.length -1]
    $.ajax({
        url: '{% url "resumn-del-subdistrito-ajax" %}',
        type: "post",
        headers: { 'X-CSRFToken': csrftoken },
        dataType: "json",
        data: { 'id': id_subdistrito },
        success: function (data) {
            //console.log(data)
            var datos = JSON.parse(JSON.stringify(data))
            //console.log(datos)

            //Personal
            let organico_este_subdistrito = datos.organico_este_subdistrito
            let reserva_subdistrito = datos.reserva_subdistrito
            let seg_interna = datos.seg_interna
            let seg_externa = datos.seg_externa
            let total_personal_subdistrito = datos.total_personal_subdistrito

            //Organizacion
            let organizacion = datos.organizacion
            let cant_secciones = datos.cant_secciones
            let cant_circuitos = datos.cant_circuitos
            let cant_locales = datos.cant_locales

            //Novedades
            let cant_novedades = datos.cant_novedades
            let nov_baja = datos.nov_baja
            let nov_media = datos.nov_media
            let nov_alta = datos.nov_alta
            let nov_critica = datos.nov_critica

            //Vehiculos
            let total_vehiculos = datos.total_vehiculos
            let veh_propios = datos.veh_propios
            let veh_contratados = datos.veh_contratados

            //Personal
            $('#organico_este_subdistrito').html(organico_este_subdistrito)
            $('#reserva_subdistrito').html(reserva_subdistrito)
            $('#seg_interna_subdistrito').html(seg_interna)
            $('#seg_externa_subdistrito').html(seg_externa)
            $('#total_personal_subdistrito').html(total_personal_subdistrito)
            //Organizacion
            $('#organizacion_subdistrito').html(organizacion)
            $('#cant_secciones_subdistritos').html(cant_secciones)
            $('#seg_circuitos_secciones').html(cant_circuitos)
            $('#seg_locales_secciones').html(cant_locales)
            //Novedades
            $('#cant_novedades_subdistrito').html(cant_novedades)
            $('#nov_baja_subdistrito').html(nov_baja)
            $('#nov_media_subdistrito').html(nov_media)
            $('#nov_alta_subdistrito').html(nov_alta)
            $('#nov_critica_subdistrito').html(nov_critica)
            //Vehículos
            $('#total_vehiculos_subdistrito').html(total_vehiculos)
            $('#veh_propios_subdistrito').html(veh_propios)
            $('#veh_contratados_subdistrito').html(veh_contratados)
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert('Error cargando datos de resumen para tarjetas de Subdistrito');
        }
    });
});