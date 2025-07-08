from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.db.models import Q, Sum, F
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from guardian.mixins import PermissionRequiredMixin as guardianPermisos
from model_utils import Choices

from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Distrito, Seccion, Circuito, Local, DistribucionPersonalDistrito, \
    DistribucionPersonalSubdistrito, DistribucionPersonalSeccion, ReservaDistrito, VehiculosPropiosDistrito, \
    VehiculosContratadosDistrito, VehiculosPropiosSubdistrito, VehiculosContratadosSubdistrito, VehiculosPropiosSeccion, \
    VehiculosContratadosSeccion, AuxiliarLocal, SegInternaLocal, SegExternaLocal, NovedadesEnLocal, Persona, Led



class ListadoDistritos(PermisoDesdeDjango, ListView):
    model = Distrito
    template_name = "AppElecciones/distritos/listado.html"
    permission_required = 'AppElecciones.view_distrito'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            ORDENAR_COLUMNAS = Choices(('0', 'distrito'))
            buscar = ['distrito']
            columnas = ('id', 'distrito')
            agregados = None
            otros_filtros = None
            con_permisos = True

            distritos = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas, otros_filtros,
                                             con_permisos, request.POST)
            result = dict()
            result['data'] = distritos['items']
            result['draw'] = distritos['draw']
            result['recordsTotal'] = distritos['total']
            result['recordsFiltered'] = distritos['count']
            # print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Distritos'
        context['listado_url'] = reverse_lazy('listado-de-distritos')
        return context


class DetalleDistrito(guardianPermisos, DetailView):
    model = Distrito
    template_name = 'AppElecciones/distritos/detalles.html'
    permission_required = 'AppElecciones.view_distrito'
    raise_exception = True
    accept_global_perms = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Distrito Electoral'
        return context


class ResumenDelDistritoAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        if request.POST:
            id_distrito = (request.POST['id'])  # id del distrito
            # https://riptutorial.com/es/django/example/13050/promedio--minimo--maximo--suma-de-queryset

            # Organizacion
            distrito = Distrito.objects.get(id=id_distrito)
            subdistritos_de_este_distrito = distrito.distrito_electoral.all()
            if subdistritos_de_este_distrito:
                secciones_este_distrito = Seccion.objects.filter(
                    subdistrito__in=subdistritos_de_este_distrito)
                circuitos_este_distrito = Circuito.objects.filter(
                    seccion__in=secciones_este_distrito)
                locales_de_este_distrito = Local.objects.filter(
                    circuito__in=circuitos_este_distrito)
            else:
                secciones_este_distrito = distrito.distrito_electora_de_la_seccion.all()

                circuitos_este_distrito = Circuito.objects.filter(
                    seccion__in=secciones_este_distrito)
                locales_de_este_distrito = Local.objects.filter(
                    circuito__in=circuitos_este_distrito)

            # Personal
            personal_en_los_subdistritos_dependientes_distrito = 0
            personal_en_este_distrito = DistribucionPersonalDistrito.objects.filter(
                distrito=id_distrito).count()
            if subdistritos_de_este_distrito:
                personal_en_los_subdistritos_dependientes_distrito = DistribucionPersonalSubdistrito.objects.filter(
                    subdistrito__in=subdistritos_de_este_distrito).count()
            personal_en_las_secciones_dependientes_distrito = DistribucionPersonalSeccion.objects.filter(
                seccion__in=secciones_este_distrito).count()

            # Reserva
            personal_de_reserva_en_este_distrito = Persona.objects.filter(
                Q(res_dis_personal__distrito=id_distrito) | Q(res_sub_personal__subdistrito__distrito=id_distrito)
            ).count()

            l = Led.objects.filter(distrito=id_distrito).annotate(
                cantffaa=Coalesce(Sum('led_seg_ffaa__cant_personal'), 0)).values('cantffaa').aggregate(
                total=Sum('cantffaa'))

            l1 = Led.objects.filter(distrito=id_distrito).annotate(
                cantffss=Coalesce(Sum('led_seg_ffseg__cant_personal'), 0)).values('cantffss').aggregate(
                total=Sum('cantffss'))

            cantidad_led = int(l['total']) + int(l1['total'])
            print(cantidad_led)
            # Vehículos
            veh_propios_subdistrito_de_este_distrito = 0
            veh_contratados_subdistrito_de_este_distrito = 0
            veh_propios_de_este_distrito = VehiculosPropiosDistrito.objects.filter(
                distrito=id_distrito).count()
            veh_contratados_de_este_distrito = VehiculosContratadosDistrito.objects.filter(
                distrito=id_distrito).count()
            if subdistritos_de_este_distrito:
                # Sin select_related (), esto haría una consulta de base de datos para cada iteración de bucle con el fin de buscar el subdistrito relacionado para cada VehPropSub
                veh_propios_subdistrito_de_este_distrito = VehiculosPropiosSubdistrito.objects.filter(
                    subdistrito__in=subdistritos_de_este_distrito).count()
                veh_contratados_subdistrito_de_este_distrito = VehiculosContratadosSubdistrito.objects.filter(
                    subdistrito__in=subdistritos_de_este_distrito).count()

            veh_propios_en_las_secciones_dependientes_distrito = VehiculosPropiosSeccion.objects.filter(
                seccion__in=secciones_este_distrito).count()
            veh_contratados_en_las_secciones_dependientes_distrito = VehiculosContratadosSeccion.objects.filter(
                seccion__in=secciones_este_distrito).count()

            cond_solamente_distrito = Persona.objects.filter(tiene_cargo=False, es_conductor=True, distrito= id_distrito).count()



            auxiliares = AuxiliarLocal.objects.filter(
                seg_interna_local__local__in=locales_de_este_distrito).values_list('auxiliar', flat=True).count()
            jefe_local = SegInternaLocal.objects.filter(
                local__in=locales_de_este_distrito).values_list('jefe_local', flat=True).count()

            seg_interna = jefe_local + auxiliares

            seg_externa = SegExternaLocal.objects.filter(
                local__in=locales_de_este_distrito).aggregate(Sum('cant_efectivos'))
            if not seg_externa['cant_efectivos__sum']:
                seg_externa = 0
            else:
                seg_externa = seg_externa['cant_efectivos__sum']

            nov_baja = NovedadesEnLocal.objects.filter(local__in=locales_de_este_distrito).filter(
                tipo__nivel='0').count()
            nov_media = NovedadesEnLocal.objects.filter(local__in=locales_de_este_distrito).filter(
                tipo__nivel='1').count()
            nov_alta = NovedadesEnLocal.objects.filter(local__in=locales_de_este_distrito).filter(
                tipo__nivel='2').count()
            nov_critica = NovedadesEnLocal.objects.filter(local__in=locales_de_este_distrito).filter(
                tipo__nivel='3').count()
            cant_novedades = nov_baja + nov_media + nov_alta + nov_critica

            # Datos de personal
            data['organico_este_distrito'] = personal_en_este_distrito + \
                                             personal_en_los_subdistritos_dependientes_distrito + \
                                             personal_en_las_secciones_dependientes_distrito + \
                                             cond_solamente_distrito
                                             #veh_propios_de_este_distrito + veh_contratados_de_este_distrito + \
                                             #veh_propios_subdistrito_de_este_distrito + \
                                             #veh_contratados_subdistrito_de_este_distrito + veh_propios_en_las_secciones_dependientes_distrito + \
                                             #veh_contratados_en_las_secciones_dependientes_distrito
            data['reserva_distrito'] = personal_de_reserva_en_este_distrito + cantidad_led

            data['seg_interna'] = seg_interna
            data['seg_externa'] = seg_externa

            data['total_personal_distrito'] = personal_en_este_distrito + \
                                              jefe_local + auxiliares + seg_externa + \
                                              personal_en_los_subdistritos_dependientes_distrito + \
                                              personal_en_las_secciones_dependientes_distrito + \
                                              cond_solamente_distrito + personal_de_reserva_en_este_distrito + \
                                              + cantidad_led
                                              #+ veh_propios_de_este_distrito + veh_contratados_de_este_distrito + \
                                              # veh_propios_subdistrito_de_este_distrito + \
                                              # veh_contratados_subdistrito_de_este_distrito + veh_propios_en_las_secciones_dependientes_distrito + \
                                              # veh_contratados_en_las_secciones_dependientes_distrito

            # Datos de la organizción
            data['organizacion'] = subdistritos_de_este_distrito.count() + secciones_este_distrito.count() + \
                                   circuitos_este_distrito.count() + locales_de_este_distrito.count()
            data['cant_subdistritos'] = subdistritos_de_este_distrito.count()
            data['cant_secciones'] = secciones_este_distrito.count()
            data['cant_circuitos'] = circuitos_este_distrito.count()
            data['cant_locales'] = locales_de_este_distrito.count()

            # Datos de novedades
            data['cant_novedades'] = cant_novedades
            data['nov_baja'] = nov_baja
            data['nov_media'] = nov_media
            data['nov_alta'] = nov_alta
            data['nov_critica'] = nov_critica

            # Datos de vehiculos

            data['total_vehiculos'] = veh_propios_de_este_distrito + \
                                      veh_contratados_de_este_distrito + veh_propios_subdistrito_de_este_distrito + \
                                      veh_contratados_subdistrito_de_este_distrito + veh_propios_en_las_secciones_dependientes_distrito + \
                                      veh_contratados_en_las_secciones_dependientes_distrito
            data['veh_propios'] = veh_propios_de_este_distrito + \
                                  veh_propios_subdistrito_de_este_distrito + \
                                  veh_propios_en_las_secciones_dependientes_distrito
            data['veh_contratados'] = veh_contratados_de_este_distrito + \
                                      veh_contratados_subdistrito_de_este_distrito + \
                                      veh_contratados_en_las_secciones_dependientes_distrito

        return JsonResponse(data, safe=False)


class DistritosResource:
    pass


def exportar_distritos(request):
    distrito_recurso = DistritosResource()
    filtro = Distrito.objects.filter(~Q(distrito="NO POSEE"))
    dataset = distrito_recurso.export(filtro)
    # dataset = distrito_recurso.export()
    response = HttpResponse(
        dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Distritos.xls"'
    return response
