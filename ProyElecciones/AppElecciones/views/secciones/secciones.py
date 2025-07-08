from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from guardian.mixins import PermissionRequiredMixin as guardianPermisos
from model_utils import Choices

from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Seccion, Local, VehiculosPropiosSeccion, VehiculosContratadosSeccion, \
    DistribucionPersonalSeccion, AuxiliarLocal, SegInternaLocal, SegExternaLocal, NovedadesEnLocal, Persona


class ListadoSecciones(PermisoDesdeDjango, ListView):
    model = Seccion
    template_name = "AppElecciones/secciones/listado.html"
    permission_required = 'AppElecciones.view_seccion'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":

            id_distrito = request.POST['id_distrito']
            id_subdistrito = request.POST['id_subdistrito']

            ORDENAR_COLUMNAS = Choices(('0', 'seccion'))
            buscar = ['seccion', 'subdistrito__subdistrito', 'distrito__distrito']
            columnas = ('id', 'seccion', 'subdistrito__subdistrito', 'distrito__distrito')
            agregados = None

            otros_filtros = {}
            if id_distrito != '':
                otros_filtros['distrito'] = id_distrito
            if id_subdistrito != '':
                otros_filtros['subdistrito'] = id_subdistrito

            con_permisos = True

            secciones = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas, otros_filtros,
                                             con_permisos, request.POST)
            result = dict()
            result['data'] = secciones['items']
            result['draw'] = secciones['draw']
            result['recordsTotal'] = secciones['total']
            result['recordsFiltered'] = secciones['count']
            # print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Secciones'
        context['listado_url'] = reverse_lazy('listado-de-secciones')
        context['tiene_subdistrito'] = organizacion_del_usuario()['tiene_subdistrito']
        return context


class DetalleSeccion(guardianPermisos, DetailView):
    model = Seccion
    template_name = 'AppElecciones/secciones/detalles.html'
    permission_required = 'AppElecciones.view_seccion'
    raise_exception = True
    accept_global_perms = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Sección Electoral'
        return context


class ResumenDeLaSeccionAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        if request.POST:
            id_seccion = (request.POST['id'])  # id de la seccion
            # https://riptutorial.com/es/django/example/13050/promedio--minimo--maximo--suma-de-queryset

            seccion = Seccion.objects.get(id=id_seccion)
            # https://docs.djangoproject.com/en/3.0/topics/db/queries/#following-relationships-backward
            # en este caso uso seccion_electoral porque puse ese nombre en el modelo en la propiedad related_name
            circuitos_de_esta_seccion = seccion.seccion_electoral.all()
            locales_de_esta_seccion = Local.objects.filter(
                circuito__in=circuitos_de_esta_seccion)
            veh_propios_de_esta_seccion = VehiculosPropiosSeccion.objects.filter(
                seccion=id_seccion).count()
            veh_contratados_de_esta_seccion = VehiculosContratadosSeccion.objects.filter(
                seccion=id_seccion).count()

            personal_en_esta_seccion = DistribucionPersonalSeccion.objects.filter(
                seccion=id_seccion).count()

            cond_solamente_seccion = Persona.objects.filter(
                Q(tiene_cargo=False) & Q(es_conductor=True) &
                (Q(veh_prop_personal_sec__seccion=id_seccion) |
                Q(veh_cont_personal_sec__seccion=id_seccion))
                ).count()


            auxiliares = AuxiliarLocal.objects.filter(
                seg_interna_local__local__in=locales_de_esta_seccion).values_list('auxiliar', flat=True).count()
            jefe_local = SegInternaLocal.objects.filter(
                local__in=locales_de_esta_seccion).values_list('jefe_local', flat=True).count()

            seg_interna = jefe_local + auxiliares

            seg_externa = SegExternaLocal.objects.filter(
                local__in=locales_de_esta_seccion).aggregate(Sum('cant_efectivos'))
            if not seg_externa['cant_efectivos__sum']:
                seg_externa = 0
            else:
                seg_externa = seg_externa['cant_efectivos__sum']

            nov_baja = 0
            nov_media = 0
            nov_alta = 0
            nov_critica = 0

            for n in NovedadesEnLocal.objects.filter(local__in=locales_de_esta_seccion).select_related('local'):
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
            data['organico_esta_seccion'] = personal_en_esta_seccion + \
                                            cond_solamente_seccion
                                            # veh_propios_de_esta_seccion + veh_contratados_de_esta_seccion
            data['seg_interna'] = jefe_local + auxiliares
            data['seg_externa'] = seg_externa
            data['total_personal_seccion'] = personal_en_esta_seccion + \
                                             cond_solamente_seccion + jefe_local + auxiliares + seg_externa
                                             #seg_interna + seg_externa + veh_propios_de_esta_seccion + \
                                             #veh_contratados_de_esta_seccion
            # Datos de la organizción
            data['organizacion'] = circuitos_de_esta_seccion.count() + \
                                   locales_de_esta_seccion.count()
            data['cant_circuitos'] = circuitos_de_esta_seccion.count()
            data['cant_locales'] = locales_de_esta_seccion.count()
            # Datos de novedades
            data['cant_novedades'] = cant_novedades
            data['nov_baja'] = nov_baja
            data['nov_media'] = nov_media
            data['nov_alta'] = nov_alta
            data['nov_critica'] = nov_critica
            # Datos de vehiculos
            data['total_vehiculos'] = veh_propios_de_esta_seccion + \
                                      veh_contratados_de_esta_seccion
            data['veh_propios'] = veh_propios_de_esta_seccion
            data['veh_contratados'] = veh_contratados_de_esta_seccion

        return JsonResponse(data, safe=False)