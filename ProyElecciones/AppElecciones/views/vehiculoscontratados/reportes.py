from django.contrib import messages
from django.db.models import Case, When, F, Value, IntegerField, Q, DateTimeField, CharField
from django.db.models.functions import Concat

from django.http import HttpResponse
from django.shortcuts import redirect
from guardian.shortcuts import get_objects_for_user

from AppElecciones.Reportes.Vehiculos.exportarVehiculosContratados import VehContratadosResource, \
    VehContratadoEmpleoResource
from AppElecciones.models import VehiculosContratados, CamposEnMayusculas


def exportarVehContratados(request):
    veh_contratado_recurso = VehContratadosResource()
    usuario = request.user
    queryset = get_objects_for_user(usuario, 'view_vehiculoscontratados', VehiculosContratados,
                                    accept_global_perms=False)
    queryset = queryset.annotate(sensor=
                                    Case(
                                        When(posee_sensor_rastreo=True, then=Value('Si')), default=Value('No'),
                                        output_field=CharField()
                                    ),
                                    troncal1=
                                     Case(
                                            When(troncal=Value(1), then=Value('Primaria')),
                                            When(troncal=Value(2), then=Value('Secundaria')),
                                            default=Value('--'),
                                            output_field=CharField()
                                        )
    )
    if queryset:
        control = 1
        nombre_archvivo = 'Vehiculos-contratados.xls'
        dataset = veh_contratado_recurso.export(queryset)
        response = HttpResponse(dataset.xls,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="archivo.xlsx"'
        response['X-control'] = control
        response['X-nombre-archivo'] = nombre_archvivo
        return response
    else:
        control = 0
        response = HttpResponse()
        # Agregar los parámetros como encabezados
        response['X-control'] = control
        return response



def exportarVehContratadosEmpleo(request):
    veh_contratado_empleo_recurso = VehContratadoEmpleoResource()
    usuario = request.user
    filtros={'vehiculo_contratado_distrito__isnull':False,'vehiculo_contratado_cge__isnull': False,'vehiculo_contratado_subdistrito__isnull':False,'vehiculo_contratado_seccion__isnull':False}


    queryset = get_objects_for_user(usuario, 'view_vehiculoscontratados', VehiculosContratados,
                                    accept_global_perms=False).filter(**filtros,_connector=Q.OR).annotate(
                                 organizacion=Case(
                                     When(vehiculo_contratado_distrito__isnull=False,  then=Concat(Value('DIS: '),F('vehiculo_contratado_distrito__distrito__distrito'))),
                                     When(vehiculo_contratado_cge__isnull=False,  then=Value('CGE')),
                                     When(vehiculo_contratado_subdistrito__isnull=False, then=Concat(Value('SUB: '),F('vehiculo_contratado_subdistrito__subdistrito__subdistrito'))),
                                     When(vehiculo_contratado_seccion__isnull=False, then=Concat(Value('Sec: '),F('vehiculo_contratado_seccion__seccion__seccion'))),
                                     default=Value('sin organizacion'), output_field=CamposEnMayusculas()),
                                 cantidad_pasajeros=Case(
                                 When(vehiculo_contratado_distrito__isnull=False,then=F('vehiculo_contratado_distrito__cantidad_pasajeros')),
                                 When(vehiculo_contratado_cge__isnull=False, then=F('vehiculo_contratado_cge__cantidad_pasajeros')),
                                 When(vehiculo_contratado_subdistrito__isnull=False, then=F('vehiculo_contratado_subdistrito__cantidad_pasajeros')),
                                 When(vehiculo_contratado_seccion__isnull=False, then=F('vehiculo_contratado_seccion__cantidad_pasajeros')),
                                 default=Value(0) ,output_field=IntegerField() ),
                                 tareas=Case(
                                When(vehiculo_contratado_distrito__isnull=False, then=F('vehiculo_contratado_distrito__tareas__tareas')),
                                When(vehiculo_contratado_cge__isnull=False, then=F('vehiculo_contratado_cge__tareas__tareas')),
                                When(vehiculo_contratado_subdistrito__isnull=False,then=F('vehiculo_contratado_subdistrito__tareas__tareas')),
                                When(vehiculo_contratado_seccion__isnull=False, then=F('vehiculo_contratado_seccion__tareas__tareas')),
                                default=Value('nada'), output_field=CamposEnMayusculas()),
                                zona_trabajo=Case(
                                When(vehiculo_contratado_distrito__isnull=False, then=F('vehiculo_contratado_distrito__zona_trabajo')),
                                When(vehiculo_contratado_cge__isnull=False, then=F('vehiculo_contratado_cge__zona_trabajo')),
                                When(vehiculo_contratado_subdistrito__isnull=False, then=F('vehiculo_contratado_subdistrito__zona_trabajo')),
                                When(vehiculo_contratado_seccion__isnull=False, then=F('vehiculo_contratado_seccion__zona_trabajo')),
                                default=Value('nada'), output_field=CamposEnMayusculas()) ,
                                desde=Case(
                                When(vehiculo_contratado_distrito__isnull=False, then=F('vehiculo_contratado_distrito__desde')),
                                When(vehiculo_contratado_cge__isnull=False, then=F('vehiculo_contratado_cge__desde')),
                                When(vehiculo_contratado_subdistrito__isnull=False, then=F('vehiculo_contratado_subdistrito__desde')),
                                When(vehiculo_contratado_seccion__isnull=False, then=F('vehiculo_contratado_seccion__desde')),
                                default=None, output_field=DateTimeField()),
                                hasta = Case(
                               When(vehiculo_contratado_distrito__isnull=False, then=F('vehiculo_contratado_distrito__hasta')),
                               When(vehiculo_contratado_cge__isnull=False, then=F('vehiculo_contratado_cge__hasta')),
                               When(vehiculo_contratado_subdistrito__isnull=False, then=F('vehiculo_contratado_subdistrito__hasta')),
                               When(vehiculo_contratado_seccion__isnull=False, then=F('vehiculo_contratado_seccion__hasta')),
                               default=None, output_field=DateTimeField()),
                               kilometros_a_recorrer = Case(
                                When(vehiculo_contratado_distrito__isnull=False, then=F('vehiculo_contratado_distrito__kilometros_a_recorrer')),
                                When(vehiculo_contratado_cge__isnull=False, then=F('vehiculo_contratado_cge__kilometros_a_recorrer')),
                                When(vehiculo_contratado_subdistrito__isnull=False, then=F('vehiculo_contratado_subdistrito__kilometros_a_recorrer')),
                                When(vehiculo_contratado_seccion__isnull=False, then=F('vehiculo_contratado_seccion__kilometros_a_recorrer')),
                                default=Value(0), output_field=IntegerField()),
                                obs = Case(
                                When(vehiculo_contratado_distrito__isnull=False, then=F('vehiculo_contratado_distrito__obs')),
                                When(vehiculo_contratado_cge__isnull=False, then=F('vehiculo_contratado_cge__obs')),
                                When(vehiculo_contratado_subdistrito__isnull=False, then=F('vehiculo_contratado_subdistrito__obs')),
                                When(vehiculo_contratado_seccion__isnull=False, then=F('vehiculo_contratado_seccion__obs')),
                                    default=Value(''), output_field=CamposEnMayusculas()),
                               responsable=Case(
                                When(vehiculo_contratado_distrito__isnull=False, then=Concat(F('vehiculo_contratado_distrito__responsable__grado__grado'),Value(' '),
                                                                                             F('vehiculo_contratado_distrito__responsable__nombre'),Value(' '),
                                                                                             F('vehiculo_contratado_distrito__responsable__apellido'),Value(' DNI:'),
                                                                                             F('vehiculo_contratado_distrito__responsable__dni'))),
                                When(vehiculo_contratado_cge__isnull=False, then=Concat(F('vehiculo_contratado_cge__responsable__grado__grado'),Value(' '),
                                                                                             F('vehiculo_contratado_cge__responsable__nombre'),Value(' '),
                                                                                             F('vehiculo_contratado_cge__responsable__apellido'), Value(' DNI:'),
                                                                                             F('vehiculo_contratado_cge__responsable__dni'))),
                                When(vehiculo_contratado_subdistrito__isnull=False, then=Concat(F('vehiculo_contratado_subdistrito__responsable__grado__grado'),Value(' '),
                                                                                             F('vehiculo_contratado_subdistrito__responsable__nombre'),Value(' '),
                                                                                             F('vehiculo_contratado_subdistrito__responsable__apellido'),Value(' DNI:'),
                                                                                             F('vehiculo_contratado_subdistrito__responsable__dni'))),
                                When(vehiculo_contratado_seccion__isnull=False, then=Concat(F('vehiculo_contratado_seccion__responsable__grado__grado'),Value(' '),
                                                                                             F('vehiculo_contratado_seccion__responsable__nombre'),Value(' '),
                                                                                            F('vehiculo_contratado_seccion__responsable__apellido'),  Value(' DNI:'),
                                                                                            F('vehiculo_contratado_seccion__responsable__dni'))),
                                default=Value(''), output_field=CamposEnMayusculas())

    ).annotate(sensor=
                                    Case(
                                        When(posee_sensor_rastreo=True, then=Value('Si')), default=Value('No'),
                                        output_field=CharField()
                                    ),
                                    troncal1=
                                     Case(
                                            When(troncal=Value(1), then=Value('Primaria')),
                                            When(troncal=Value(2), then=Value('Secundaria')),
                                            default=Value('--'),
                                            output_field=CharField()
                                        )
    )
    # print(queryset.values_list('organizacion','patente_matricula','cantidad_pasajeros',
    #                             'tareas','zona_trabajo',
    #                             'desde',
    #                             'hasta',
    #                             'kilometros_a_recorrer',
    #                             'obs',
    #                             'responsable'
    #                             ))
    #
    # html = "<html><body>prueba.</body></html>"
    # return HttpResponse(html)
    if queryset:
        control = 1
        nombre_archvivo = 'Empleo-vehiculos-contratados.xls'
        dataset = veh_contratado_empleo_recurso.export(queryset)
        response = HttpResponse(dataset.xls,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="archivo.xlsx"'
        response['X-control'] = control
        response['X-nombre-archivo'] = nombre_archvivo
        return response
    else:
        control = 0
        response = HttpResponse()
        # Agregar los parámetros como encabezados
        response['X-control'] = control
        return response
