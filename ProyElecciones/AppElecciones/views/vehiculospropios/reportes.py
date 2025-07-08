from django.db.models import Case, Q, When, Value, F, IntegerField, DateTimeField, CharField
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import redirect
from guardian.shortcuts import get_objects_for_user

from AppAdministracion.models import CamposEnMayusculas
from AppElecciones.Reportes.Vehiculos.exportarVehiculosPropios import VehPropiosResource, VehPropioEmpleoResource
from AppElecciones.models import VehiculosPropios
from django.contrib import messages

def exportarVehPropios(request):
    veh_propio_recurso = VehPropiosResource()
    usuario = request.user
    queryset = get_objects_for_user(usuario, 'view_vehiculospropios', VehiculosPropios,
                                    accept_global_perms=False)
    queryset = queryset.annotate(sensor=
                                 Case(
                                     When(posee_sensor_rastreo=True, then=Value('Si')), default=Value('No'),
                                     output_field=CharField()),
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
        nombre_archvivo = 'Vehiculos-provistos.xls'
        dataset = veh_propio_recurso.export(queryset)
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

def exportarVehPropiosEmpleo(request):
    veh_propio_empleo = VehPropioEmpleoResource()
    usuario = request.user
    filtros={'veh_propio_distrito__isnull':False,'veh_propio_cge__isnull': False,'veh_prop_sub__isnull':False,'veh_prop_sec__isnull':False}
    queryset = get_objects_for_user(usuario, 'view_vehiculospropios', VehiculosPropios, accept_global_perms=False).filter(**filtros,_connector=Q.OR).annotate(
                                 organizacion=Case(
                                     When(veh_propio_distrito__isnull=False,  then=Concat(Value('DIS: '),F('veh_propio_distrito__distrito__distrito'))),
                                     When(veh_propio_cge__isnull=False,  then=Value('CGE')),
                                     When(veh_prop_sub__isnull=False, then=Concat(Value('SUB: '),F('veh_prop_sub__subdistrito__subdistrito'))),
                                     When(veh_prop_sec__isnull=False, then=Concat(Value('Sec: '),F('veh_prop_sec__seccion__seccion'))),
                                     default=Value('sin organizacion'), output_field=CamposEnMayusculas()),


                                 tareas=Case(
                                When(veh_propio_distrito__isnull=False, then=F('veh_propio_distrito__tareas__tareas')),
                                When(veh_propio_cge__isnull=False, then=F('veh_propio_cge__tareas__tareas')),
                                When(veh_prop_sub__isnull=False,then=F('veh_prop_sub__tareas__tareas')),
                                When(veh_prop_sec__isnull=False, then=F('veh_prop_sec__tareas__tareas')),
                                default=Value('nada'), output_field=CamposEnMayusculas()),
                                zona_trabajo=Case(
                                When(veh_propio_distrito__isnull=False, then=F('veh_propio_distrito__zona_trabajo')),
                                When(veh_propio_cge__isnull=False, then=F('veh_propio_cge__zona_trabajo')),
                                When(veh_prop_sub__isnull=False, then=F('veh_prop_sub__zona_trabajo')),
                                When(veh_prop_sec__isnull=False, then=F('veh_prop_sec__zona_trabajo')),
                                default=Value('nada'), output_field=CamposEnMayusculas()) ,
                                desde=Case(
                                When(veh_propio_distrito__isnull=False, then=F('veh_propio_distrito__desde')),
                                When(veh_propio_cge__isnull=False, then=F('veh_propio_cge__desde')),
                                When(veh_prop_sub__isnull=False, then=F('veh_prop_sub__desde')),
                                When(veh_prop_sec__isnull=False, then=F('veh_prop_sec__desde')),
                                default=None, output_field=DateTimeField()),
                                hasta = Case(
                               When(veh_propio_distrito__isnull=False, then=F('veh_propio_distrito__hasta')),
                               When(veh_propio_cge__isnull=False, then=F('veh_propio_cge__hasta')),
                               When(veh_prop_sub__isnull=False, then=F('veh_prop_sub__hasta')),
                               When(veh_prop_sec__isnull=False, then=F('veh_prop_sec__hasta')),
                               default=None, output_field=DateTimeField()),
                               kilometros_a_recorrer = Case(
                                When(veh_propio_distrito__isnull=False, then=F('veh_propio_distrito__kilometros_a_recorrer')),
                                When(veh_propio_cge__isnull=False, then=F('veh_propio_cge__kilometros_a_recorrer')),
                                When(veh_prop_sub__isnull=False, then=F('veh_prop_sub__kilometros_a_recorrer')),
                                When(veh_prop_sec__isnull=False, then=F('veh_prop_sec__kilometros_a_recorrer')),
                                default=Value(0), output_field=IntegerField()),
                                obs = Case(
                                When(veh_propio_distrito__isnull=False, then=F('veh_propio_distrito__obs')),
                                When(veh_propio_cge__isnull=False, then=F('veh_propio_cge__obs')),
                                When(veh_prop_sub__isnull=False, then=F('veh_prop_sub__obs')),
                                When(veh_prop_sec__isnull=False, then=F('veh_prop_sec__obs')),
                                    default=Value(''), output_field=CamposEnMayusculas()),
                               conductor=Case(
                                When(veh_propio_distrito__isnull=False, then=Concat(F('veh_propio_distrito__conductor__grado__grado'),Value(' '),
                                                                                             F('veh_propio_distrito__conductor__nombre'),Value(' '),
                                                                                             F('veh_propio_distrito__conductor__apellido'),Value(' DNI:'),
                                                                                             F('veh_propio_distrito__conductor__dni'))),
                                When(veh_propio_cge__isnull=False, then=Concat(F('veh_propio_cge__conductor__grado__grado'),Value(' '),
                                                                                             F('veh_propio_cge__conductor__nombre'),Value(' '),
                                                                                             F('veh_propio_cge__conductor__apellido'), Value(' DNI:'),
                                                                                             F('veh_propio_cge__conductor__dni'))),
                                When(veh_prop_sub__isnull=False, then=Concat(F('veh_prop_sub__conductor__grado__grado'),Value(' '),
                                                                                             F('veh_prop_sub__conductor__nombre'),Value(' '),
                                                                                             F('veh_prop_sub__conductor__apellido'),Value(' DNI:'),
                                                                                             F('veh_prop_sub__conductor__dni'))),
                                When(veh_prop_sec__isnull=False, then=Concat(F('veh_prop_sec__conductor__grado__grado'),Value(' '),
                                                                                             F('veh_prop_sec__conductor__nombre'),Value(' '),
                                                                                            F('veh_prop_sec__conductor__apellido'),  Value(' DNI:'),
                                                                                            F('veh_prop_sec__conductor__dni'))),
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

    # print(queryset.values_list('organizacion','fuerza__fuerza','unidad','ni_patente_matricula',
    #                             'tareas','zona_trabajo',
    #                             'desde',
    #                             'hasta',
    #                             'kilometros_a_recorrer',
    #                             'obs',
    #                             'conductor'
    #                             ))

    # html = "<html><body>prueba</body></html>"
    # return HttpResponse(html)
    if queryset:
        control = 1
        nombre_archvivo = 'Empleo-vehiculos-provistos.xls'
        dataset = veh_propio_empleo.export(queryset)
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





