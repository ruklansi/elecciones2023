from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views import View
from django.views.generic.detail import DetailView

from AppElecciones.models import CdoGrlElect, Subdistrito, Seccion, Circuito, Local, DistribucionPersonalCdoGrlElect, \
    ReservaCdoGrlElect, DistribucionPersonalDistrito, ReservaDistrito, DistribucionPersonalSubdistrito, \
    DistribucionPersonalSeccion, SegInternaLocal, SegExternaLocal, VehiculosPropiosCdoGrlElect, \
    VehiculosPropiosDistrito, VehiculosPropiosSubdistrito, VehiculosPropiosSeccion, VehiculosContratadosCdoGrlElect, \
    VehiculosContratadosDistrito, VehiculosContratadosSubdistrito, VehiculosContratadosSeccion, NovedadesEnLocal, \
    Persona

from guardian.mixins import PermissionRequiredMixin as guardianPermisos


class DetalleCdoGrlElect(guardianPermisos, DetailView):
    model = CdoGrlElect
    template_name = 'AppElecciones/CdoGrlElect/detalles.html'
    permission_required = 'AppElecciones.view_cdogrlelect'
    raise_exception = True
    accept_global_perms = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ResumenDelCGEAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        if request.POST:
            pass
            id_CGE = (request.POST['id'])  # id del cge
            # https://riptutorial.com/es/django/example/13050/promedio--minimo--maximo--suma-de-queryset

            # Obtencion de datos

            # Organizacion #####################################################
            cge = CdoGrlElect.objects.get(id=id_CGE)
            distritos_del_cge = cge.cge.filter((~Q(distrito="NO POSEE")))
            subdistritos_del_cge = Subdistrito.objects.filter(
                Q(distrito__in=distritos_del_cge) and ~Q(distrito__distrito="NO POSEE"))
            secciones_del_cge = Seccion.objects.filter(
                distrito__in=distritos_del_cge)
            circuitos_del_cge = Circuito.objects.filter(
                seccion__in=secciones_del_cge)
            locales_del_cge = Local.objects.filter(
                circuito__in=circuitos_del_cge)
            ####################################################################

            # Personal #########################################################
            # Cdo Grl Elect
            personal_organico_cge = DistribucionPersonalCdoGrlElect.objects.all().count()
            personal_reserva_cge = ReservaCdoGrlElect.objects.all().count()
            todo_el_personal_en_cge = personal_organico_cge + personal_reserva_cge

            # Distritos
            personal_organico_distritos = DistribucionPersonalDistrito.objects.all().count()
            personal_reserva_distritos = ReservaDistrito.objects.all().count()
            todo_el_personal_en_los_distritos = personal_organico_distritos + \
                                                personal_reserva_distritos

            # Subdistritos
            todo_el_personal_organico_en_los_subdistritos = DistribucionPersonalSubdistrito.objects.all().count()

            # Secciones
            todo_el_personal_organico_en_las_secciones = DistribucionPersonalSeccion.objects.all().count()

            # ***********************************
            # values_list()con un solo campo, puede usar flat=True para devolver un QuerySet de valores únicos en lugar de tuplas: <QuerySet [1, 2]>
            jefe_local = 0
            auxiliares = 0
            seg_interna = 0
            jefe_local = SegInternaLocal.objects.all().values_list(
                'jefe_local', flat=True).count()
            # auxiliares=SegInternaLocal.objects.filter(local__in=locales_de_este_distrito).values_list('auxiliares',flat=True).count() ->> dejo esto como ejemplo con filtro
            # auxiliares = SegInternaLocal.objects.all().exclude(auxiliares=None).values_list(
            #     'auxiliares', flat=True).count()

            seg_interna = jefe_local + auxiliares

            seg_externa = SegExternaLocal.objects.all().aggregate(Sum('cant_efectivos'))
            if not seg_externa['cant_efectivos__sum']:
                seg_externa = 0
            else:
                seg_externa = seg_externa['cant_efectivos__sum']

            cond_solamente_cge = Persona.objects.filter(
                (Q(tiene_cargo=False) & Q(es_conductor=True) & (Q(veh_pro_cge_persona__cge=id_CGE) | Q(veh_con_cge_persona__cge=id_CGE)))).count()
            # ************************************

            # Totales
            todo_el_personal_organico_cge = personal_organico_cge + \
                                            personal_organico_distritos + \
                                            todo_el_personal_organico_en_las_secciones
            todo_el_personal_reserva_cge = personal_reserva_cge + personal_reserva_distritos

            todo_el_personal_del_cge = todo_el_personal_organico_cge + \
                                       todo_el_personal_reserva_cge + cond_solamente_cge
            ####################################################################

            # Vehiculos ########################################################
            veh_propios_de_todo_el_cge = 0
            veh_propios_del_cge = VehiculosPropiosCdoGrlElect.objects.all().count()
            veh_propios_de_los_distritos = VehiculosPropiosDistrito.objects.all().count()
            veh_propios_de_los_subdistritos = VehiculosPropiosSubdistrito.objects.all().count()
            veh_propios_de_las_secciones = VehiculosPropiosSeccion.objects.all().count()
            veh_propios_de_todo_el_cge = veh_propios_del_cge + veh_propios_de_los_distritos + \
                                         veh_propios_de_los_subdistritos + veh_propios_de_las_secciones

            veh_contratados_de_todo_el_cge = 0
            veh_contratados_del_cge = VehiculosContratadosCdoGrlElect.objects.all().count()
            veh_contratados_de_los_distritos = VehiculosContratadosDistrito.objects.all().count()
            veh_contratados_de_los_subdistritos = VehiculosContratadosSubdistrito.objects.all().count()
            veh_contratados_de_las_secciones = VehiculosContratadosSeccion.objects.all().count()
            veh_contratados_de_todo_el_cge = veh_contratados_del_cge + veh_contratados_de_los_distritos + \
                                             veh_contratados_de_los_subdistritos + veh_contratados_de_las_secciones

            ####################################################################

            # Novedades ########################################################
            nov_baja = 0
            nov_media = 0
            nov_alta = 0
            nov_critica = 0
            cant_novedades = 0

            nov_baja = NovedadesEnLocal.objects.filter(local__in=locales_del_cge).filter(
                tipo__nivel='0').count()
            nov_media = NovedadesEnLocal.objects.filter(local__in=locales_del_cge).filter(
                tipo__nivel='1').count()
            nov_alta = NovedadesEnLocal.objects.filter(local__in=locales_del_cge).filter(
                tipo__nivel='2').count()
            nov_critica = NovedadesEnLocal.objects.filter(local__in=locales_del_cge).filter(
                tipo__nivel='3').count()
            cant_novedades = nov_baja + nov_media + nov_alta + nov_critica
            ####################################################################

            # Exportacion de datos

            # Datos del cge más sus elementos dependientes
            # Datos de la organizción
            data['cant_distritos'] = distritos_del_cge.count()
            data['cant_subdistritos'] = subdistritos_del_cge.count()
            data['cant_secciones'] = secciones_del_cge.count()
            data['cant_circuitos'] = circuitos_del_cge.count()
            data['cant_locales'] = locales_del_cge.count()

            # Datos de vehiculos
            data['total_vehiculos_propios_todo_cge'] = veh_propios_de_todo_el_cge
            data['total_vehiculos_contratados_todo_cge'] = veh_contratados_de_todo_el_cge
            data['total_vehiculos_cge'] = veh_propios_de_todo_el_cge + \
                                          veh_contratados_de_todo_el_cge

            # Datos de novedades
            data['cant_novedades'] = cant_novedades
            data['nov_baja'] = nov_baja
            data['nov_media'] = nov_media
            data['nov_alta'] = nov_alta
            data['nov_critica'] = nov_critica

            # Datos de seguridad

            data['seg_interna'] = seg_interna
            data['seg_externa'] = seg_externa

            # Datos de personal
            data['todo_personal_del_cge'] = todo_el_personal_del_cge
                                            #cond_solamente_cge
                                            #seg_externa + seg_interna
            data['organico_del_cge'] = todo_el_personal_organico_cge
            data['reserva_del_cge'] = todo_el_personal_reserva_cge

            # Datos solo del comando sin sus elementos dependientes
            # Personal
            data['solamente_todo_el_personal_del_cge'] = todo_el_personal_en_cge
            data['solamente_todo_el_personal_organico_del_cge'] = personal_organico_cge
            data['solamente_todo_el_personal_de_la_reserva_del_cge'] = personal_reserva_cge

            # Vehículos
            data['solamente_todo_los_veh_propios_del_cge'] = veh_propios_del_cge
            data['solamente_todo_los_veh_contratados_del_cge'] = veh_contratados_del_cge
            data['solamente_todo_los_veh_del_cge'] = veh_propios_del_cge + \
                                                     veh_contratados_del_cge

        return JsonResponse(data, safe=False)
