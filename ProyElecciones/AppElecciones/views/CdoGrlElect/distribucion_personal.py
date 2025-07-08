from django.db.models import Value, CharField, F
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from model_utils import Choices

from AppElecciones.forms import FormDistribucionPersonalCdoGrlElect
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import CdoGrlElect, DistribucionPersonalCdoGrlElect, Persona


class ListarDistribucionCdoGrlElectAjax(View):

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        id_del_cge = request.POST['id_cge']
        ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
        buscar = ['cargo__cargo', 'designacion', 'integrante__grado__grado', 'integrante__dni', 'integrante__nombre',
                  'integrante__apellido']
        columnas = ('id', 'cargo__cargo', 'designacion', 'persona', 'editar', 'eliminar')
        agregados = {'persona': Concat(
            F('integrante__grado__grado'), Value(' '),
            F('integrante__nombre'), Value(' '),
            F('integrante__apellido'), Value(' DNI: '),
            F('integrante__dni'), output_field=CharField())}
        otros_filtros = {'cge': id_del_cge, 'cargo__guia': False}
        con_permisos = True

        org_cge = listarParaDatatables(DistribucionPersonalCdoGrlElect, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                       otros_filtros,
                                       con_permisos, request.POST)
        resultado = dict()
        resultado['data'] = org_cge['items']
        resultado['draw'] = org_cge['draw']
        resultado['recordsTotal'] = org_cge['total']
        resultado['recordsFiltered'] = org_cge['count']
        #print(resultado)
        return JsonResponse(resultado, safe=False)


class CrearDistribucionEnCdoGrlElect(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            id_del_cge = request.POST['id_cge']
            if request.is_ajax():
                ######################
                integrante = request.POST['integrante']
                if integrante:
                    Persona.objects.filter(id=integrante).update(tiene_cargo=True, num_cargos=F('num_cargos') + 1)
                ######################
            form = FormDistribucionPersonalCdoGrlElect(request.POST)
            if form.is_valid():
                instancia = form.save(commit=False)
                CdoGrlElect_ = CdoGrlElect.objects.get(id=id_del_cge)
                instancia.cge = CdoGrlElect_
                instancia.save()
                data['form_es_valido'] = True
            else:
                data['form_es_valido'] = False
                context = {'form': form}
                data['html_form'] = render_to_string(
                    'AppElecciones/CdoGrlElect/crearDistPers.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'GET':
            if request.is_ajax():
                form = FormDistribucionPersonalCdoGrlElect()
        context = {'form': form}
        data['html_form'] = render_to_string(
            'AppElecciones/CdoGrlElect/crearDistPers.html', context, request=request)
        return JsonResponse(data)


class ActualizarDistribucionEnCdoGrlElect(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(DistribucionPersonalCdoGrlElect, pk=kwargs['pk'])
                ####################################
                integrante_actual = request.POST['integrante']
                if integrante_actual:
                    if integrante_actual != instancia.integrante.id:
                        # Proceso el anterior
                        Persona.objects.filter(id=instancia.integrante.id).update(
                            tiene_cargo=False, num_cargos=0)
                        # Proceso el actual
                        Persona.objects.filter(id=integrante_actual).update(
                            tiene_cargo=True, num_cargos=1)
                ####################################
                form = FormDistribucionPersonalCdoGrlElect(request.POST, instance=instancia)

                if form.is_valid():
                    form.save()
                    data['form_es_valido'] = True
                else:
                    data['form_es_valido'] = False
                    context = {'form': form}
                    data['html_form'] = render_to_string(
                        'AppElecciones/CdoGrlElect/modificarDistPers.html', context, request=request)

        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            DistribucionPersonalCdoGrlElect, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                form = FormDistribucionPersonalCdoGrlElect(instance=instancia)
        context = {'form': form}
        data['html_form'] = render_to_string(
            'AppElecciones/CdoGrlElect/modificarDistPers.html', context, request=request)
        return JsonResponse(data)


class EliminarDistribucionEnCdoGrlElect(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            DistribucionPersonalCdoGrlElect, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                ###############################
                Persona.objects.filter(id=instancia.integrante.id).update(
                    tiene_cargo=False, num_cargos=0)
                ###############################
                instancia.delete()
                data['permitido'] = True
        return JsonResponse(data)
