import json

from crum import get_current_user
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, Case, Value, When, Subquery, OuterRef, Count, F, Sum, \
    IntegerField
from django.db.models.functions import Concat, Coalesce
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from guardian.mixins import PermissionRequiredMixin as guardianPermisos
from guardian.shortcuts import get_objects_for_user
from model_utils import Choices

from AppElecciones.forms import *
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import CamposEnMayusculas


class ListadoCircuitosFiltrados(PermisoDesdeDjango, ListView):
    model = Circuito
    template_name = "AppElecciones/circuitos/listado.html"
    permission_required = 'AppElecciones.view_circuito'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":

            id_distrito = request.POST['id_distrito']
            id_subdistrito = request.POST['id_subdistrito']
            id_seccion = request.POST['id_seccion']

            situacion = request.POST['situacion']
            tienelocal = request.POST['tienelocal']
            urnasentregadas = request.POST['urnasentregadas']

            ORDENAR_COLUMNAS = Choices(('1', 'fecha_creacion'), ('7', 'total_locales'))

            buscar = ['circuito', 'situacion']

            columnas = (
                'id', 'circuito', 'seccion__seccion', 'seccion__subdistrito__subdistrito',
                'seccion__distrito__distrito', 'situacion', 'entrego_urna_en_led', 'total_locales',
                'editar', 'eliminar')

           # agregados = {'total_locales': Value(0)}
            agregados={ 'total_locales': Subquery(Local.objects.filter(circuito=OuterRef('pk')).values('circuito__pk').annotate(locales=Count('pk')).values('locales'))}
            otros_filtros = {}

            if id_distrito != '':
                otros_filtros['seccion__distrito'] = id_distrito
            if id_subdistrito != '':
                otros_filtros['seccion__subdistrito'] = id_subdistrito
            if id_seccion != '':
                otros_filtros['seccion'] = id_seccion

            if situacion != '':
                otros_filtros['situacion'] = situacion
            if tienelocal != '':
                usuario = get_current_user()
                query = get_objects_for_user(usuario, 'view_circuito', self.model, accept_global_perms=False)
                if tienelocal == 'conlocal':
                    otros_filtros['id__in'] = query.filter(locales_en_circuito__isnull=False)
                if tienelocal == 'sinlocal':
                    otros_filtros['id__in'] = query.filter(locales_en_circuito__isnull=True)
            if urnasentregadas != '':
                if urnasentregadas == 'entregadas':
                    otros_filtros['entrego_urna_en_led'] = True
                if urnasentregadas == 'noentregadas':
                    otros_filtros['entrego_urna_en_led'] = False

            con_permisos = True

            circuitos = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas, otros_filtros,
                                             con_permisos, request.POST)
            result = dict()
            result['data'] = circuitos['items']
            result['draw'] = circuitos['draw']
            result['recordsTotal'] = circuitos['total']
            result['recordsFiltered'] = circuitos['count']
            # print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Circuitos'
        usuario = get_current_user()
        circuitos = get_objects_for_user(usuario, 'view_circuito', Circuito, accept_global_perms=False)
        context['circuitos_sin_local'] = circuitos.filter(locales_en_circuito__isnull=True).count()
        context['listado_url'] = reverse_lazy('listado-de-circuitos-filtrados')
        context['crear_url'] = reverse_lazy('crear-circuito')
        context['tiene_subdistrito'] = organizacion_del_usuario()['tiene_subdistrito']
        return context


class CrearCircuito(PermisoDesdeDjango, SuccessMessageMixin, CreateView):
    model = Circuito
    form_class = FormCircuito
    template_name = 'AppElecciones/circuitos/crear.html'
    success_message = 'Circuito agregado'
    permission_required = 'AppElecciones.add_circuito'
    raise_exception = True

    def get_success_url(self):
        return reverse('listado-de-circuitos-filtrados')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar circuito'
        return context


class ActualizarCircuito(guardianPermisos, SuccessMessageMixin, UpdateView):
    model = Circuito
    form_class = FormCircuito
    template_name = 'AppElecciones/circuitos/crear.html'
    permission_required = 'AppElecciones.change_circuito'
    success_message = 'Circuito actualizado'
    raise_exception = True
    accept_global_perms = False

    def get_success_url(self):
        return reverse('listado-de-circuitos-filtrados')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar Circuito'
        return context


class EliminarCircuito(guardianPermisos, SuccessMessageMixin, DeleteView):
    model = Circuito
    template_name = 'AppElecciones/circuitos/eliminar.html'
    success_url = reverse_lazy('listado-de-circuitos-filtrados')
    permission_required = 'AppElecciones.delete_circuito'
    raise_exception = True
    accept_global_perms = False

    def delete(self, request, *args, **kwargs):

        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()
            messages.success(self.request, ("Circuito eliminado"))
            return HttpResponseRedirect(success_url)
        except ProtectedError:

            messages.success(self.request, ("Imposible eliminar el Circuito " + str(self.object) + "porque tiene "
                                                                                                   "Locales que le "
                                                                                                   "dependen"))
            return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Circuito'
        return context


class DetalleCircuito(guardianPermisos, DetailView):
    model = Circuito
    template_name = 'AppElecciones/circuitos/detalles.html'
    permission_required = 'AppElecciones.view_circuito'
    raise_exception = True
    accept_global_perms = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Circuito Electoral '
        return context


class FiltraCamposCircuitoAjax(View):
    """
    Select anidados desde el Distrito y Subdistrito para obtener la Seccion para crear un Circuito
    """

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        resultado = dict()
        accion = (request.POST['accion'])

        if accion == 'filtrar-subdistritos-en-circuito':
            if Subdistrito.objects.filter(distrito_id=request.POST['id']).exists():
                data = []
                organizacion = organizacion_del_usuario()['org']
                if organizacion == 'subdistrito':
                    instancia_subdistrito = organizacion_del_usuario()['instancia']
                    sub = Subdistrito.objects.get(id=instancia_subdistrito.id)
                    data.append({'id': sub.id, 'subdistrito': sub.subdistrito})
                else:
                    for s in Subdistrito.objects.filter(distrito_id=request.POST['id']):
                        data.append({'id': s.id, 'subdistrito': s.subdistrito})
                resultado['datos'] = data
                resultado['hay_subdistrito'] = True
            else:
                data = []
                for t in Seccion.objects.filter(distrito_id=request.POST['id']):
                    data.append({'id': t.id, 'seccion': t.seccion})
                resultado['datos'] = data
                resultado['hay_subdistrito'] = False
        if accion == 'filtrar-seccion-en-circuito':
            data = []
            # aca el id es un subdistrito
            for s in Seccion.objects.filter(subdistrito_id=request.POST['id']):
                data.append({'id': s.id, 'seccion': s.seccion})
            resultado['datos'] = data
            resultado['hay_secciones'] = True
        return JsonResponse(resultado, safe=False)


class CircuitoAdelante(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            id_circuito = request.POST['id']
            circuito = Circuito.objects.get(id=id_circuito)
        # Si el circuito esta en la situación no iniciada, lo cambio a inicio despliegue
        if circuito.situacion == 'Actividades no iniciadas':
            circuito.situacion = 'Inicio despliegue'
            circuito.save()
            data['cambio_estado'] = True
        # Si el circuito esta en la situación inicio despliegue, lo cambio a desplegado
        elif circuito.situacion == 'Inicio despliegue':
            circuito.situacion = 'Desplegado'
            circuito.save()
            data['cambio_estado'] = True
        # Si el circuito esta en la situación de despliegado, lo cambio a inicio repliegue
        elif circuito.situacion == 'Desplegado':
            circuito.situacion = 'Inicio repliegue'
            circuito.save()
            data['cambio_estado'] = True
        # Si el circuito esta en la situación de inicio repliegue, lo cambio a replegado
        elif circuito.situacion == 'Inicio repliegue':
            circuito.situacion = 'Replegado'
            circuito.save()
            data['cambio_estado'] = True

        return JsonResponse(data, safe=False)


class CircuitoDesplegar(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            lista_id = []
            lista_id_ = json.loads(request.POST['lista_id'])
            accion = request.POST['accion']
            # print(accion)
            for x in lista_id_:
                lista_id.append(x['id'])

            if accion == 'desplegar':
                circuitos = Circuito.objects.filter(id__in=lista_id)

                circuitos.update(
                    situacion=Case(When(situacion='Actividades no iniciadas', then=Value('Inicio despliegue')),
                                   When(situacion='Inicio despliegue', then=Value('Desplegado')),
                                   When(situacion='Desplegado', then=Value('Inicio repliegue')),
                                   When(situacion='Inicio repliegue', then=Value('Replegado')),
                                   default=Value('Replegado')
                                   ))

            if accion == 'replegar':
                circuitos = Circuito.objects.filter(id__in=lista_id)
                circuitos.update(situacion=Case(
                    When(situacion='Replegado', then=Value('Inicio repliegue')),
                    When(situacion='Inicio despliegue', then=Value('Actividades no iniciadas')),
                    When(situacion='Desplegado', then=Value('Inicio despliegue')),
                    When(situacion='Inicio repliegue', then=Value('Desplegado')),
                    default=Value('Actividades no iniciadas')
                ))
            if accion == 'resetear':
                circuitos = Circuito.objects.filter(id__in=lista_id)
                circuitos.update(situacion='Actividades no iniciadas')
            if accion == 'entregar_urnas_led':
                circuitos = Circuito.objects.filter(id__in=lista_id)
                circuitos.update(entrego_urna_en_led=True)
            if accion == 'no_entregar_urnas_led':
                circuitos = Circuito.objects.filter(id__in=lista_id)
                circuitos.update(entrego_urna_en_led=False)
        return JsonResponse(data, safe=False)


class ListarLocalesDelCircuito(View):
    """
    Lista los locales del circuito para mostrarlos en el resumen del mismo
    """

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            id_circuito = request.POST['id_circuito']

            ORDENAR_COLUMNAS = Choices(('0', 'nombre'))
            buscar = ['nombre', 'jefe_local', 'cant_aux', 'cant_seg_ext', 'cant_nov', 'estado__estado', 'nov_subsanada',
                      'cant_mesas']
            columnas = (
                'id', 'nombre', 'jefe_local', 'cant_aux', 'cant_seg_ext', 'cant_nov', 'estado__estado', 'nov_subsanada',
                'cant_mesas')
            agregados = {'jefe_local': Subquery(SegInternaLocal.objects.filter(local=OuterRef('pk')).values(
                'local__pk').annotate(j_local=Concat(
                F('jefe_local__grado__grado'), Value(' '),
                F('jefe_local__nombre'), Value(' '),
                F('jefe_local__apellido'), Value(' DNI: '),
                F('jefe_local__dni'), output_field=CamposEnMayusculas())).values('j_local')),
                         'cant_aux': Coalesce(
                             Subquery(AuxiliarLocal.objects.filter(seg_interna_local__local=OuterRef('pk')).values(
                                 'seg_interna_local__local__pk').annotate(aux=Count('auxiliar')).values('aux')), 0),
                         'cant_seg_ext': Subquery(SegExternaLocal.objects.filter(local=OuterRef('pk')).values(
                             'local__pk').annotate(cantsegext=Sum('cant_efectivos')).values('cantsegext')),
                         'cant_nov': Count('novedad_en_el_local__id'),
                         'nov_subsanada': Count(
                             Case(When(novedad_en_el_local__subsanada='No', then=1), output_field=IntegerField())),
                         'cant_mesas': Subquery(MesasEnLocal.objects.filter(local=OuterRef('pk')).values(
                             'local__pk').annotate(cant_mesas_=Count('mesas')).values('cant_mesas_')),
                         }
            otros_filtros = {'circuito': id_circuito}
            con_permisos = False
            locales_en_circuito = listarParaDatatables(Local, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                       otros_filtros,
                                                       con_permisos, request.POST)
            result = dict()

            result['data'] = locales_en_circuito['items']
            result['draw'] = locales_en_circuito['draw']
            result['recordsTotal'] = locales_en_circuito['total']
            result['recordsFiltered'] = locales_en_circuito['count']
            # print(result)
        return JsonResponse(result, safe=False)


class DetallesDelCircuitoAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        if request.POST:
            id = (request.POST['id'])  # id del circuito
            # https://riptutorial.com/es/django/example/13050/promedio--minimo--maximo--suma-de-queryset
            locales = Local.objects.filter(circuito=id)

            # sumo la seg_interna en el front-end y no aca
            auxiliares = AuxiliarLocal.objects.filter(seg_interna_local__local__in=
                                                      locales).values_list('auxiliar', flat=True).count()
            jefe_local = SegInternaLocal.objects.filter(
                local__in=locales).values_list('jefe_local', flat=True).count()

            seg_externa = SegExternaLocal.objects.filter(
                local__in=locales).aggregate(Sum('cant_efectivos'))
            if not seg_externa['cant_efectivos__sum']:
                seg_externa = 0
            else:
                seg_externa = seg_externa['cant_efectivos__sum']

            nov_baja = 0
            nov_media = 0
            nov_alta = 0
            nov_critica = 0

            for n in NovedadesEnLocal.objects.filter(local__in=locales).select_related('local'):
                if n.tipo.nivel == '0':
                    nov_baja += 1
                if n.tipo.nivel == '1':
                    nov_media += 1
                if n.tipo.nivel == '2':
                    nov_alta += 1
                if n.tipo.nivel == '3':
                    nov_critica += 1
            cant_novedades = nov_baja + nov_media + nov_alta + nov_critica

            data['jefe_local'] = jefe_local
            data['auxiliares'] = auxiliares
            data['seg_externa'] = seg_externa
            data['cant_novedades'] = cant_novedades
            cant_locales = locales.count()
            data['cant_locales'] = cant_locales

        return JsonResponse(data, safe=False)


def CircuitoReset(request):
    data = dict()
    if request.method == 'POST':
        id_circuito = request.POST['id']
        circuito = Circuito.objects.get(id=id_circuito)
        # Si el circuito esta en la situación de replegado, lo cambio a inicio repliegue
        if circuito.situacion == 'Replegado':
            circuito.situacion = 'Inicio repliegue'
            circuito.save()
            data['reset_estado'] = True
        # Si el circuito esta en la situación de inicio repliegue, lo cambio a desplegado
        elif circuito.situacion == 'Inicio repliegue':
            circuito.situacion = 'Desplegado'
            circuito.save()
            data['reset_estado'] = True
        # Si el circuito esta en la situación de desplegado, lo cambio a inicio despliegue
        elif circuito.situacion == 'Desplegado':
            circuito.situacion = 'Inicio despliegue'
            circuito.save()
            data['reset_estado'] = True
        # Si el circuito esta en la situación de inicio despliegue, lo cambio a actividades no iniciadas
        elif circuito.situacion == 'Inicio despliegue':
            circuito.situacion = 'Actividades no iniciadas'
            circuito.save()
            data['reset_estado'] = True
    return JsonResponse(data, safe=False)

