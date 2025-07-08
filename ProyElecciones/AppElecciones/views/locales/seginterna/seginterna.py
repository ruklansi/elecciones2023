# Aca el ecuatoriano explica sobre error csrf
# https://www.youtube.com/watch?v=yJMyXc2gaCo&list=PLxm9hnvxnn-j5ZDOgQS63UIBxQytPdCG7&index=24

from django.contrib import messages
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from model_utils import Choices

from AppElecciones.forms import FormSeguridadInternaLocal
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import SegInternaLocal, Local, Persona, AuxiliarLocal


class ListarSegInterna(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':

            id_local = request.POST['id_local']
            ORDENAR_COLUMNAS = Choices(('0', 'jefe_local'))
            buscar = []
            columnas = ('id', 'jefe', 'editar', 'eliminar')
            agregados = {'jefe': Concat(
                F('jefe_local__grado__grado'), Value(' '),
                F('jefe_local__nombre'), Value(' '),
                F('jefe_local__apellido'), Value(' DNI: '),
                F('jefe_local__dni'), output_field=CharField())}
            if id_local:
                otros_filtros = {'local': id_local}
            con_permisos = True

            lista_seg_interna = listarParaDatatables(SegInternaLocal, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                     otros_filtros, con_permisos, request.POST)

            data = dict()
            data['data'] = lista_seg_interna['items']
            data['draw'] = lista_seg_interna['draw']
            data['recordsTotal'] = lista_seg_interna['total']
            data['recordsFiltered'] = lista_seg_interna['count']
            # print(data)
            return JsonResponse(data, safe=False)


class CrearSegInterna(CreateView):
    model = SegInternaLocal
    form_class = FormSeguridadInternaLocal
    template_name = 'AppElecciones/locales/seg-interna/crear_actualizar.html'

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
                    aux = form.cleaned_data['auxiliares']
                    j_local = form.cleaned_data['jefe_local']
                    ######################
                    Persona.objects.filter(id=j_local.id).update(tiene_cargo=True, num_cargos=F('num_cargos') + 1)
                    Persona.objects.filter(id__in=aux).update(tiene_cargo=True, num_cargos=F('num_cargos') + 1)
                    ######################
                    instancia.local = Local.objects.get(id=id_local)
                    instancia.save()
                    AuxiliarLocal.objects.bulk_create([AuxiliarLocal(seg_interna_local=instancia,
                                                                     auxiliar=x) for x in aux], ignore_conflicts=True)
                    data['form_es_valido'] = True
                    data['mensaje'] = 'Datos de seguridad interna agregados'
                else:
                    data['form_es_valido'] = False
                context = {'form': form, 'accion': 'crear'}
                data['html_form'] = render_to_string('AppElecciones/locales/seg-interna/crear_actualizar.html',
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
                data['html_form'] = render_to_string('AppElecciones/locales/seg-interna/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class ActualizarSegInterna(UpdateView):
    model = SegInternaLocal
    form_class = FormSeguridadInternaLocal
    template_name = 'AppElecciones/locales/seg-interna/crear_actualizar.html'

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(self.model, pk=kwargs['pk'])
                # Proceso el jefe de local
                j_local_actual = request.POST['jefe_local']

                if j_local_actual != instancia.jefe_local.id:
                    # Proceso el anterior
                    Persona.objects.filter(id=instancia.jefe_local.id).update(
                        tiene_cargo=False, num_cargos=0)
                    # Proceso el actual
                    Persona.objects.filter(id=j_local_actual).update(
                        tiene_cargo=True, num_cargos=1)
                form = self.form_class(request.POST, instance=instancia)
                if form.is_valid():
                    dato = form.save(commit=False)
                    id_local = request.POST['id_local']
                    aux_actuales = form.cleaned_data['auxiliares']
                    instancia.local = Local.objects.get(id=id_local)
                    instancia.save()
                    # Proceso los aux anteriores
                    reg_aux = AuxiliarLocal.objects.filter(seg_interna_local=instancia)
                    Persona.objects.filter(id__in=reg_aux.values_list('auxiliar')).update(tiene_cargo=False,
                                                                                          num_cargos=0)
                    reg_aux.delete()
                    # Proceso los aux actuales
                    AuxiliarLocal.objects.bulk_create([
                        AuxiliarLocal(seg_interna_local=instancia, auxiliar=x) for x in aux_actuales],
                        ignore_conflicts=True)
                    Persona.objects.filter(id__in=aux_actuales).update(tiene_cargo=True, num_cargos=F('num_cargos') + 1)
                    dato.save()
                    data['form_es_valido'] = True
                    data['mensaje'] = 'Datos de seguridad interna modificados'
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
                data['html_form'] = render_to_string('AppElecciones/locales/seg-interna/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class EliminarSegInterna(DeleteView):
    model = SegInternaLocal

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            if request.is_ajax():
                data = dict()
                instancia = get_object_or_404(self.model, pk=kwargs['pk'])
                ###############################
                # Proceso el jefe de local
                Persona.objects.filter(id=instancia.jefe_local.id).update(
                    tiene_cargo=False, num_cargos=0)
                # Proceso los aux anteriores
                reg_aux = AuxiliarLocal.objects.filter(seg_interna_local=instancia)
                Persona.objects.filter(id__in=reg_aux.values_list('auxiliar')).update(tiene_cargo=False, num_cargos=0)
                reg_aux.delete()
                ###############################
                instancia.delete()
                data['borrado'] = True
                data['mensaje'] = 'Datos de seguridad interna eliminados'
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class MostrarAuxiliares(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':

            if request.is_ajax():
                data = dict()
                seg_interna = get_object_or_404(SegInternaLocal, pk=kwargs['pk'])
                auxiliares = AuxiliarLocal.objects.filter(seg_interna_local=seg_interna)
                if auxiliares:
                    data['hay_dato'] = True
                    data['auxiliares'] = [x.auxiliar.NombreCompleto() for x in auxiliares]
                else:
                    data['hay_dato'] = False
                return JsonResponse(data, safe=False)
