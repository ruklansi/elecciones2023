var csrftoken = Cookies.get('csrftoken');
$(function () {


    let id_distrito1 = parseInt('{{object.id}}')
    var id_distrito = id_distrito1
    $.ajax({
        url: '{% url "resumn-del-distrito-ajax" %}',
        type: "post",
        headers: { 'X-CSRFToken': csrftoken },
        dataType: "json",
        data: { 'id': id_distrito },
        success: function (data) {
            //console.log(data)
            var datos = JSON.parse(JSON.stringify(data))
            //console.log(datos)

            //Organizacion
            let organizacion = datos.organizacion
            let cant_subdistritos = datos.cant_subdistritos
            let cant_secciones = datos.cant_secciones
            let cant_circuitos = datos.cant_circuitos
            let cant_locales = datos.cant_locales
            $('#organizacion_distrito').html(organizacion)
            $('#cant_subdistritos_distrito').html(cant_subdistritos)
            $('#cant_secciones_distrito').html(cant_secciones)
            $('#cant_circuitos_distrito').html(cant_circuitos)
            $('#cant_locales_distritos').html(cant_locales)

            //Personal
            let organico_este_distrito = datos.organico_este_distrito
            let reserva_distrito = datos.reserva_distrito
            let seg_interna = datos.seg_interna
            let seg_externa = datos.seg_externa
            let total_personal_distrito = datos.total_personal_distrito
            $('#organico_este_distrito').html(organico_este_distrito)
            $('#reserva_distrito').html(reserva_distrito)
            $('#seg_interna_distrito').html(seg_interna)
            $('#seg_externa_distrito').html(seg_externa)
            $('#total_personal_distrito').html(total_personal_distrito)

            //Vehiculos
            let total_vehiculos = datos.total_vehiculos
            let veh_propios = datos.veh_propios
            let veh_contratados = datos.veh_contratados
            $('#total_vehiculos_distrito').html(total_vehiculos)
            $('#veh_propios_distrito').html(veh_propios)
            $('#veh_contratados_distrito').html(veh_contratados)

            //Novedades
            let cant_novedades = datos.cant_novedades
            let nov_baja = datos.nov_baja
            let nov_media = datos.nov_media
            let nov_alta = datos.nov_alta
            let nov_critica = datos.nov_critica
            $('#cant_novedades_distrito').html(cant_novedades)
            $('#nov_baja_distrito').html(nov_baja)
            $('#nov_media_distrito').html(nov_media)
            $('#nov_alta_distrito').html(nov_alta)
            $('#nov_critica_distrito').html(nov_critica)

        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert('Error cargando datos de resumen para tarjetas de la sección');
        }
    });





});