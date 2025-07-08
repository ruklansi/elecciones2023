import os

from django.contrib import messages
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from model_utils import Choices

from AppElecciones.forms import FormNovedadesLocal
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Local, NovedadesEnLocal, CamposEnMayusculas
from django.views import View
import json
from django.db.models import Q, Value, F
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from ProyElecciones import settings


class ListarNovedadesEnLocal(View):

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            id_local = request.POST['id_local']
            ORDENAR_COLUMNAS = Choices(('1', 'fecha_creacion'))
            buscar = ['local__nombre', 'fecha', 'tipo__tipo', 'detalle', 'subsanada', 'medidas_adoptadas']
            columnas = ('id', 'fecha', 'tipo__tipo', 'detalle', 'subsanada', 'medidas_adoptadas', 'editar', 'eliminar')
            agregados = None
            if id_local:
                otros_filtros = {'local': id_local}
            con_permisos = True

            lista_novedades = listarParaDatatables(NovedadesEnLocal, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                               otros_filtros, con_permisos, request.POST)
            data = dict()
            data['data'] = lista_novedades['items']
            data['draw'] = lista_novedades['draw']
            data['recordsTotal'] = lista_novedades['total']
            data['recordsFiltered'] = lista_novedades['count']
            return JsonResponse(data, safe=False)


class CrearNovedadesEnLocal(CreateView):
    model = NovedadesEnLocal
    form_class = FormNovedadesLocal
    template_name = 'AppElecciones/locales/novedades/crear_actualizar.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                form = self.form_class(request.POST)
                if form.is_valid():
                    instancia = form.save(commit=False)
                    id_local = request.POST['id_local']
                    instancia.local = Local.objects.get(id=id_local)
                    instancia.save()
                    data['form_es_valido'] = True
                    data['mensaje'] = 'Datos de novedades en el local agregados'
                else:
                    data['form_es_valido'] = False
                context = {'form': form, 'accion': 'crear'}
                data['html_form'] = render_to_string('AppElecciones/locales/novedades/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')

    def get(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'GET':
            if request.is_ajax():
                form = self.form_class
                context = {'form': form, 'accion': 'crear'}
                data['html_form'] = render_to_string('AppElecciones/locales/novedades/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class ActualizarNovedadesEnLocal(UpdateView):
    model = NovedadesEnLocal
    form_class = FormNovedadesLocal
    template_name = 'AppElecciones/locales/novedades/crear_actualizar.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(self.model, pk=kwargs['pk'])
                id_local = request.POST['id_local']
                form = self.form_class(request.POST, instance=instancia)
                if form.is_valid():
                    dato = form.save(commit=False)
                    dato.local = Local.objects.get(id=id_local)
                    dato.save()
                    data['form_es_valido'] = True
                    data['mensaje'] = 'Datos de novedades en el local modificados'
                else:
                    data['form_es_valido'] = False
                    context = {'form': form, 'accion': 'editar'}
                    data['html_form'] = render_to_string('AppElecciones/locales/novedades/crear_actualizar.html',
                                                         context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            if request.is_ajax():
                data = dict()
                instancia = get_object_or_404(self.model, pk=kwargs['pk'])
                form = self.form_class(instance=instancia)
                context = {'form': form, 'accion': 'editar'}
                data['html_form'] = render_to_string('AppElecciones/locales/novedades/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class EliminarNovedadesEnLocal(DeleteView):
    model = NovedadesEnLocal

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            if request.is_ajax():
                data = dict()
                instancia = get_object_or_404(self.model, pk=kwargs['pk'])
                instancia.delete()
                data['borrado'] = True
                data['mensaje'] = 'Datos de novedades en el local eliminados'
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')

class ListarTodasLasNovedadesEnLocales(ListView):
    model = NovedadesEnLocal
    template_name = "AppElecciones/locales/todas_las_novedades_de_locales.html"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':

            id_distrito = request.POST['id_distrito']
            tipo_novedad = request.POST['tipo_novedad']
            subsanada = request.POST['subsanada']

            ORDENAR_COLUMNAS = Choices(('1', 'fecha_creacion'))
            buscar = ['fecha', 'tipo__tipo', 'detalle', 'subsanada', 'medidas_adoptadas', 'local__nombre']
            columnas = ('id', 'fecha', 'tipo__tipo', 'detalle', 'subsanada', 'medidas_adoptadas', 'local_enlace',
                        'local__circuito__seccion__distrito__distrito')
            local_url = reverse_lazy('detalles-local', args=[23])
            agregados = {'local_enlace': Concat(Value('<a href="' + local_url[:-2]), F('local__id'),
                                 Value('">'), F('local__nombre'), output_field=CamposEnMayusculas())}
            otros_filtros = {}
            if id_distrito != '':
                otros_filtros['local__circuito__seccion__distrito'] = id_distrito
            if tipo_novedad != '':
                otros_filtros['tipo'] = tipo_novedad
            if subsanada != '':
                otros_filtros['subsanada'] = subsanada

            con_permisos = True

            todas_novedades_en_locales = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                     otros_filtros,
                                                     con_permisos, request.POST)

            data = dict()
            data['data'] = todas_novedades_en_locales['items']
            data['draw'] = todas_novedades_en_locales['draw']
            data['recordsTotal'] = todas_novedades_en_locales['total']
            data['recordsFiltered'] = todas_novedades_en_locales['count']
            return JsonResponse(data, safe=False)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # usuario = self.request.user
        context['titulo'] = 'Novedades en los locales de votación'
        context['listado_url'] = reverse_lazy('listado-de-todas-novedades-en-locales')
        context['crear_url'] = reverse_lazy('crear-local')
        return context

