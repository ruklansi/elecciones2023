from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from guardian.mixins import PermissionRequiredMixin as guardianPermisos
from model_utils import Choices

from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Subdistrito, Circuito, Local, DistribucionPersonalSubdistrito, \
    DistribucionPersonalSeccion, ReservaSubdistrito, VehiculosPropiosSubdistrito, VehiculosPropiosSeccion, \
    VehiculosContratadosSubdistrito, VehiculosContratadosSeccion, AuxiliarLocal, SegInternaLocal, SegExternaLocal, \
    NovedadesEnLocal, Persona


class ListadoSubdistritos(PermisoDesdeDjango, ListView):
    model = Subdistrito
    template_name = "AppElecciones/subdistritos/listado.html"
    permission_required = 'AppElecciones.view_subdistrito'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            # id_distrito = request.POST['id_distrito']
            ORDENAR_COLUMNAS = Choices(('0', 'subdistrito'))
            buscar = ['subdistrito', 'distrito__distrito', 'detalle']
            columnas = ('id', 'subdistrito', 'distrito__distrito', 'detalle')
            agregados = None
            otros_filtros = None
            con_permisos = True

            subdistritos = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                otros_filtros,
                                                con_permisos, request.POST)

            result = dict()
            result['data'] = subdistritos['items']
            result['draw'] = subdistritos['draw']
            result['recordsTotal'] = subdistritos['total']
            result['recordsFiltered'] = subdistritos['count']
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Subdistritos'
        context['listado_url'] = reverse_lazy('listado-de-subdistritos')
        # context['crear_url'] = reverse_lazy('crear-subdistrito')
        return context


class DetalleSubdistrito(guardianPermisos, DetailView):
    model = Subdistrito
    template_name = 'AppElecciones/subdistritos/detalles.html'
    permission_required = 'AppElecciones.view_subdistrito'
    raise_exception = True
    accept_global_perms = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Subdistrito Electoral'
        return context


class ResumenDelSubdistritoAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        if request.POST:
            id_subdistrito = (request.POST['id'])  # id del subdistrito

            # Organizacion
            subdistrito = Subdistrito.objects.get(id=id_subdistrito)
            secciones_este_subdistrito = subdistrito.subdistrito_electoral.all()
            circuitos_este_subdistrito = Circuito.objects.filter(
                seccion__in=secciones_este_subdistrito)
            locales_de_este_subdistrito = Local.objects.filter(
                circuito__in=circuitos_este_subdistrito)

            # Personal
            personal_en_este_subdistrito = DistribucionPersonalSubdistrito.objects.filter(
                subdistrito=id_subdistrito).count()
            personal_en_las_secciones_dependientes_subdistrito = DistribucionPersonalSeccion.objects.filter(
                seccion__in=secciones_este_subdistrito).count()

            # Reserva
            personal_de_reserva_en_este_subdistrito = ReservaSubdistrito.objects.filter(
                subdistrito=id_subdistrito).count()

            # Vehículos
            veh_propios_de_este_subdistrito = VehiculosPropiosSubdistrito.objects.filter(
                subdistrito=id_subdistrito).count()
            veh_propios_en_las_secciones_dependientes_subdistrito = VehiculosPropiosSeccion.objects.filter(
                seccion__in=secciones_este_subdistrito).count()
            veh_contratados_de_este_subdistrito = VehiculosContratadosSubdistrito.objects.filter(
                subdistrito=id_subdistrito).count()
            veh_contratados_en_las_secciones_dependientes_subdistrito = VehiculosContratadosSeccion.objects.filter(
                seccion__in=secciones_este_subdistrito).count()

            cond_solamente_subdistrito = Persona.objects.filter(
                (Q(tiene_cargo=False) & Q(es_conductor=True) & Q(veh_pro_sub_persona__subdistrito=id_subdistrito) | Q(veh_con_sub_personal__subdistrito=id_subdistrito))
                | (Q(tiene_cargo=False) & Q(es_conductor=True) & Q(veh_prop_personal_sec__seccion__subdistrito=id_subdistrito) | Q(veh_cont_personal_sec__seccion__subdistrito=id_subdistrito))
            ).count()


            # Seguridad interna en locales
            auxiliares = AuxiliarLocal.objects.filter(
                seg_interna_local__local__in=locales_de_este_subdistrito).values_list('auxiliar', flat=True).count()
            jefe_local = SegInternaLocal.objects.filter(
                local__in=locales_de_este_subdistrito).values_list('jefe_local', flat=True).count()
            seg_interna = jefe_local + auxiliares

            # Seguridad externa en locales
            seg_externa = SegExternaLocal.objects.filter(local__in=locales_de_este_subdistrito).aggregate(
                Sum('cant_efectivos'))
            if not seg_externa['cant_efectivos__sum']:
                seg_externa = 0
            else:
                seg_externa = seg_externa['cant_efectivos__sum']
            # seg_externa = 0
            nov_baja = 0
            nov_media = 0
            nov_alta = 0
            nov_critica = 0

            for n in NovedadesEnLocal.objects.filter(local__in=locales_de_este_subdistrito).select_related('local'):
                if n.tipo.nivel == '0':
                    nov_baja += 1
                if n.tipo.nivel == '1':
                    nov_media += 1
                if n.tipo.nivel == '2':
                    nov_alta += 1
                if n.tipo.nivel == '3':
                    nov_critica += 1
            cant_novedades = nov_baja + nov_media + nov_alta + nov_critica

            # Datos de personal
            data['organico_este_subdistrito'] = personal_en_este_subdistrito + \
                                                personal_en_las_secciones_dependientes_subdistrito + \
                                                cond_solamente_subdistrito
                                                #veh_propios_de_este_subdistrito + veh_propios_en_las_secciones_dependientes_subdistrito + \
                                                #veh_contratados_de_este_subdistrito + \
                                                #veh_contratados_en_las_secciones_dependientes_subdistrito
            data['reserva_subdistrito'] = personal_de_reserva_en_este_subdistrito
            data['seg_interna'] = seg_interna
            data['seg_externa'] = seg_externa
            data['total_personal_subdistrito'] = personal_en_este_subdistrito + \
                                                 seg_interna + seg_externa + \
                                                 personal_en_las_secciones_dependientes_subdistrito + \
                                                 cond_solamente_subdistrito + personal_de_reserva_en_este_subdistrito
                                                 # veh_propios_de_este_subdistrito + veh_propios_en_las_secciones_dependientes_subdistrito + \
                                                 # veh_contratados_de_este_subdistrito + \
                                                 # veh_contratados_en_las_secciones_dependientes_subdistrito

            # Datos de la organizción
            data['organizacion'] = secciones_este_subdistrito.count() + circuitos_este_subdistrito.count() + \
                                   locales_de_este_subdistrito.count()
            data['cant_secciones'] = secciones_este_subdistrito.count()
            data['cant_circuitos'] = circuitos_este_subdistrito.count()
            data['cant_locales'] = locales_de_este_subdistrito.count()

            # Datos de novedades
            data['cant_novedades'] = cant_novedades
            data['nov_baja'] = nov_baja
            data['nov_media'] = nov_media
            data['nov_alta'] = nov_alta
            data['nov_critica'] = nov_critica

            # Datos de vehiculos
            data['total_vehiculos'] = veh_propios_de_este_subdistrito + \
                                      veh_contratados_de_este_subdistrito + veh_propios_en_las_secciones_dependientes_subdistrito + \
                                      veh_contratados_en_las_secciones_dependientes_subdistrito
            data['veh_propios'] = veh_propios_de_este_subdistrito + \
                                  veh_propios_en_las_secciones_dependientes_subdistrito
            data['veh_contratados'] = veh_contratados_de_este_subdistrito + \
                                      veh_contratados_en_las_secciones_dependientes_subdistrito

        return JsonResponse(data, safe=False)