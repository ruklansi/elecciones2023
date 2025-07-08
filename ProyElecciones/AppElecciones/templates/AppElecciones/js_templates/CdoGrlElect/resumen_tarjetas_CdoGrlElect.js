var csrftoken = Cookies.get('csrftoken');
$(function () {
    let id_cge = parseInt('{{ object.id }}')
    $.ajax({
        url: '{% url "resumn-del-cge-ajax" %}',
        type: "post",
        headers: { 'X-CSRFToken': csrftoken },
        dataType: "json",
        data: { 'id': id_cge },
        success: function (data) {
            //console.log(data)
            var datos = JSON.parse(JSON.stringify(data))
            //console.log(datos)

            //Organizacion
            let cant_distritos = datos.cant_distritos
            let cant_subdistritos = datos.cant_subdistritos
            let cant_secciones = datos.cant_secciones
            let cant_circuitos = datos.cant_circuitos
            let cant_locales = datos.cant_locales
            $('#distritos_cgetotal').html(cant_distritos)
            $('#subdistritos_cgetotal').html(cant_subdistritos)
            $('#secciones_cgetotal').html(cant_secciones)
            $('#circuitos_cgetotal').html(cant_circuitos)
            $('#locales_cgetotal').html(cant_locales)

            //Vehiculos
            let total_vehiculos_cgetotal = datos.total_vehiculos_cge
            let veh_propios_cgetotal = datos.total_vehiculos_propios_todo_cge
            let veh_contratados_cgetotal = datos.total_vehiculos_contratados_todo_cge
            $('#total_vehiculos_cgetotal').html(total_vehiculos_cgetotal)
            $('#veh_propios_cgetotal').html(veh_propios_cgetotal)
            $('#veh_contratados_cgetotal').html(veh_contratados_cgetotal)

            //Novedades
            let cant_novedades_cgetotal = datos.cant_novedades
            let nov_baja_cgetotal = datos.nov_baja
            let nov_media_cgetotal = datos.nov_media
            let nov_alta_cgetotal = datos.nov_alta
            let nov_critica_cgetotal = datos.nov_critica
            $('#cant_novedades_cgetotal').html(cant_novedades_cgetotal)
            $('#nov_baja_cgetotal').html(nov_baja_cgetotal)
            $('#nov_media_cgetotal').html(nov_media_cgetotal)
            $('#nov_alta_cgetotal').html(nov_alta_cgetotal)
            $('#nov_critica_cgetotal').html(nov_critica_cgetotal)

            //Personal
            let total_personal_cgetotal = datos.todo_personal_del_cge
            let organica_cgetotal = datos.organico_del_cge
            let reserva_cgetotal = datos.reserva_del_cge
            let seg_interna_cgetotal = datos.seg_interna
            let seg_externa_cgetotal = datos.seg_externa
            $('#total_personal_cgetotal').html(total_personal_cgetotal)
            $('#organica_cgetotal').html(organica_cgetotal)
            $('#reserva_cgetotal').html(reserva_cgetotal)
            $('#seg_interna_cgetotal').html(seg_interna_cgetotal)
            $('#seg_externa_cgetotal').html(seg_externa_cgetotal)

            //Datos de Personal y Vehículos solamente del CGE sin sus elementos dependientes
            //Personal
            let solamente_todo_el_personal_del_cge = datos.solamente_todo_el_personal_del_cge
            let solamente_todo_el_personal_organico_del_cge = datos.solamente_todo_el_personal_organico_del_cge
            let solamente_todo_el_personal_de_la_reserva_del_cge = datos.solamente_todo_el_personal_de_la_reserva_del_cge
            $('#solamente_todo_el_personal_del_cge').html(solamente_todo_el_personal_del_cge)
            $('#solamente_todo_el_personal_organico_del_cge').html(solamente_todo_el_personal_organico_del_cge)
            $('#solamente_todo_el_personal_de_la_reserva_del_cge').html(solamente_todo_el_personal_de_la_reserva_del_cge)

            //Vehículos
            let solamente_todo_los_veh_del_cge = datos.solamente_todo_los_veh_del_cge
            let solamente_todo_los_veh_propios_del_cge = datos.solamente_todo_los_veh_propios_del_cge
            let solamente_todo_los_veh_contratados_del_cge = datos.solamente_todo_los_veh_contratados_del_cge
            $('#solamente_todo_los_veh_del_cge').html(solamente_todo_los_veh_del_cge)
            $('#solamente_todo_los_veh_propios_del_cge').html(solamente_todo_los_veh_propios_del_cge)
            $('#solamente_todo_los_veh_contratados_del_cge').html(solamente_todo_los_veh_contratados_del_cge)

        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert('Error cargando datos de resumen para Cdo Grl Elect');
        }
    });
    '{% load guardian_tags %}'
    '{% get_obj_perms request.user for object as "permiso" %}'


});