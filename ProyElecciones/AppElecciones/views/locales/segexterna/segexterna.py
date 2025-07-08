from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from model_utils import Choices

from AppElecciones.forms import FormSeguridadExternaLocal
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Local, SegExternaLocal


class ListarSegExterna(View):
    def dispatch(self, request, *args, **kwargs):

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        global otros_filtros
        if request.method == 'POST':
            id_local = request.POST['id_local']

            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
            buscar = []
            columnas = ('id', 'fuerza__fuerza_seg', 'cant_efectivos', 'editar', 'eliminar')
            agregados = None
            if id_local:
                otros_filtros = {'local': id_local}
            con_permisos = True

            lista_seg_externa = listarParaDatatables(SegExternaLocal, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                     otros_filtros, con_permisos, request.POST)

            data = dict()
            data['data'] = lista_seg_externa['items']
            data['draw'] = lista_seg_externa['draw']
            data['recordsTotal'] = lista_seg_externa['total']
            data['recordsFiltered'] = lista_seg_externa['count']

            return JsonResponse(data, safe=False)


class CrearSegExterna(CreateView):
    model = SegExternaLocal
    form_class = FormSeguridadExternaLocal
    template_name = 'AppElecciones/locales/seg-externa/crear_actualizar.html'

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
                    data['mensaje'] = 'Datos de seguridad externa agregados'
                else:
                    data['form_es_valido'] = False
                context = {'form': form, 'accion': 'crear'}
                data['html_form'] = render_to_string('AppElecciones/locales/seg-externa/crear_actualizar.html',
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
                data['html_form'] = render_to_string('AppElecciones/locales/seg-externa/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class ActualizarSegExterna(UpdateView):
    model = SegExternaLocal
    form_class = FormSeguridadExternaLocal
    template_name = 'AppElecciones/locales/seg-externa/crear_actualizar.html'

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
                    data['mensaje'] = 'Datos de seguridad externa modificados'
                else:
                    data['form_es_valido'] = False
                    context = {'form': form, 'accion': 'editar'}
                    data['html_form'] = render_to_string('AppElecciones/locales/seg-interna/crear_actualizar.html',
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
                data['html_form'] = render_to_string('AppElecciones/locales/seg-externa/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class EliminarSegExterna(DeleteView):
    model = SegExternaLocal

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            if request.is_ajax():
                data = dict()
                instancia = get_object_or_404(self.model, pk=kwargs['pk'])
                instancia.delete()
                data['borrado'] = True
                data['mensaje'] = 'Datos de seguridad externa eliminados'
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')
