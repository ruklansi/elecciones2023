import json

from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.db.models import When, Value, Case
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from model_utils import Choices

from AppElecciones.forms import FormMesasLocal
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import MesasEnLocal, Local, EstadosMesas


class ListarMesasEnLocalAjax(View):
    permission_required = 'AppElecciones.view_mesasenlocal'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            id_local = request.POST['id_local']
            campo = dict(MesasEnLocal._meta.get_field('voto').flatchoices)
            lista = [When(voto=k, then=Value(v)) for k, v in campo.items()]
            voto_ = Case(*lista)
            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
            buscar = ['mesas', 'voto_']
            columnas = ('id', 'mesas', 'voto_', 'editar', 'eliminar')
            agregados = {'voto_': voto_}
            if id_local:
                otros_filtros = {'local': id_local}
            con_permisos = True

            lista_mesas = listarParaDatatables(MesasEnLocal, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                               otros_filtros,
                                               con_permisos, request.POST)
            data = dict()
            data['data'] = lista_mesas['items']
            data['draw'] = lista_mesas['draw']
            data['recordsTotal'] = lista_mesas['total']
            data['recordsFiltered'] = lista_mesas['count']
            # print(data)
            return JsonResponse(data, safe=False)


class ListarMesasParaIniciarAjax(PermisoDesdeDjango, ListView):
    model = MesasEnLocal
    template_name = "AppElecciones/locales/mesas/controlinicio.html"
    permission_required = 'AppElecciones.view_mesasenlocal'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            estado = request.POST['estado']
            id_distrito = request.POST['id_distrito']
            id_subdistrito = request.POST['id_subdistrito']
            id_seccion = request.POST['id_seccion']
            id_circuito = request.POST['id_circuito']
            id_local = request.POST['id_local']
            tipo_mesa = request.POST['tipo_mesa']

            ORDENAR_COLUMNAS = Choices(('1', 'fecha_creacion'))
            buscar = ['mesas', 'local__nombre', 'local__circuito__circuito', 'local__circuito__seccion__seccion',
                      'estado__estado', 'estado__causa']
            columnas = ('id', 'local__id', 'mesas', 'estado__estado', 'estado__causa', 'local__nombre',
                        'local__circuito__circuito', 'local__circuito__seccion__seccion',
                        'local__circuito__seccion__distrito__distrito',
                        'local__circuito__seccion__subdistrito__subdistrito')
            agregados = None

            otros_filtros = {}

            if id_distrito != '':
                otros_filtros['local__circuito__seccion__distrito'] = id_distrito
            if id_subdistrito != '':
                otros_filtros['local__circuito__seccion__subdistrito'] = id_subdistrito
            if id_seccion != '':
                otros_filtros['local__circuito__seccion'] = id_seccion
            if id_circuito != '':
                otros_filtros['local__circuito'] = id_circuito
            if id_local != '':
                otros_filtros['local'] = id_local
            if estado != '':
                otros_filtros['estado'] = estado
            if tipo_mesa != '':
                otros_filtros['voto'] = tipo_mesa

            con_permisos = True

            lista_mesas_para_iniciar = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                            otros_filtros,
                                                            con_permisos, request.POST)

            data = dict()
            data['data'] = lista_mesas_para_iniciar['items']
            data['draw'] = lista_mesas_para_iniciar['draw']
            data['recordsTotal'] = lista_mesas_para_iniciar['total']
            data['recordsFiltered'] = lista_mesas_para_iniciar['count']
            # print(data)
            return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Control de mesas'
        context['listado_url'] = reverse_lazy(
            'listado-de-mesas-en-local-para-iniciar')
        context['tiene_subdistrito'] = organizacion_del_usuario()['tiene_subdistrito']
        return context


class CrearMesaEnLocal(CreateView):

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *arg, **kwargs):
        data = dict()
        if request.method == 'POST':
            id_local = request.POST['id_local']
            if request.is_ajax():
                form = FormMesasLocal(request.POST)
                if form.is_valid():
                    instancia = form.save(commit=False)
                    local = Local.objects.get(id=id_local)
                    instancia.local = local
                    instancia.save()
                    data['form_es_valido'] = True
                    data['mensaje'] = 'Datos de mesas en el local agregados'
                else:
                    data['form_es_valido'] = False
                context = {'form': form, 'accion': 'crear'}
                data['html_form'] = render_to_string(
                    'AppElecciones/locales/mesas/crear_actualizar.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'GET':
            if request.is_ajax():
                form = FormMesasLocal()
        context = {'form': form, 'accion': 'crear'}
        data['html_form'] = render_to_string(
            'AppElecciones/locales/mesas/crear_actualizar.html', context, request=request)
        return JsonResponse(data)


class ActualizarMesaEnLocal(UpdateView):

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(
                    MesasEnLocal, pk=kwargs['pk'])
                # id_local = request.POST['id_local']
                form = FormMesasLocal(
                    request.POST, instance=instancia)
                if form.is_valid():
                    form.save()
                    data['form_es_valido'] = True
                    data['mensaje'] = 'Datos de mesas en el local actualizados'
                else:
                    data['form_es_valido'] = False
                    context = {'form': form, 'accion': 'editar'}
                    data['html_form'] = render_to_string(
                        'AppElecciones/locales/mesas/crear_actualizar.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            MesasEnLocal, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                form = FormMesasLocal(instance=instancia)
        context = {'form': form, 'accion': 'editar'}
        data['html_form'] = render_to_string(
            'AppElecciones/locales/mesas/crear_actualizar.html', context, request=request)
        return JsonResponse(data)


class EliminarMesaEnLocal(DeleteView):

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            MesasEnLocal, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                instancia.delete()
                data['borrado'] = True
                data['mensaje'] = 'Datos de mesas en el local eliminados'
        return JsonResponse(data)


class CargarCausaNoInicioMesasAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = []
        for m in EstadosMesas.objects.all():
            data.append({'id': m.id, 'estado': m.estado, 'causa': m.causa})

        return JsonResponse(data, safe=False)


class EntradaAjaxMesas(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = []
        accion = (request.POST['accion'])

        if accion == 'ejecutar_accion_en_mesas':
            tipo_causa_mesas = (request.POST['tipo_causa_mesas'])
            lista_id_mesas = json.loads(request.POST['lista_id'])
            lista_id = [x['id'] for x in lista_id_mesas]
            mesas = MesasEnLocal.objects.filter(pk__in=lista_id)
            estado = EstadosMesas.objects.get(id=tipo_causa_mesas)
            mesas.update(estado=estado)
            # print(data)
        return JsonResponse(data, safe=False)
