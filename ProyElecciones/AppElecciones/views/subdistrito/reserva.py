from django.db.models import Value, CharField, F
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from model_utils import Choices

from AppElecciones.forms import FormReservaSubdistrito
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Persona, ReservaSubdistrito, Subdistrito


class ListarReservaSubdistritoAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        id_del_subdistrito = request.POST['id_subdistrito']
        ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
        buscar = ['integrante__grado__grado', 'integrante__dni', 'integrante__nombre', 'integrante__apellido']
        columnas = ('id', 'persona', 'obs', 'editar', 'eliminar')
        agregados = {'persona': Concat(
            F('integrante__grado__grado'), Value(' '),
            F('integrante__nombre'), Value(' '),
            F('integrante__apellido'), Value(' DNI: '),
            F('integrante__dni'), output_field=CharField())}

        otros_filtros = {'subdistrito': id_del_subdistrito}
        con_permisos = True

        reserva_subdis = listarParaDatatables(ReservaSubdistrito, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                              otros_filtros,
                                              con_permisos, request.POST)
        resultado = dict()
        resultado['data'] = reserva_subdis['items']
        resultado['draw'] = reserva_subdis['draw']
        resultado['recordsTotal'] = reserva_subdis['total']
        resultado['recordsFiltered'] = reserva_subdis['count']
        # print(resultado)
        return JsonResponse(resultado, safe=False)


class CrearReservaEnSubdistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            id_del_subdistrito = request.POST['id_subdistrito']
            if request.is_ajax():
                #############################
                integrante = request.POST['integrante']
                if integrante:
                    Persona.objects.filter(id=integrante).update(tiene_cargo=True,  num_cargos=F('num_cargos') + 1)
                ############################
            form = FormReservaSubdistrito(request.POST)
            if form.is_valid():
                instancia = form.save(commit=False)
                subdistrito_ = Subdistrito.objects.get(id=id_del_subdistrito)
                instancia.subdistrito = subdistrito_
                instancia.save()
                data['form_es_valido'] = True
            else:
                data['form_es_valido'] = False
                context = {'form': form}
                data['html_form'] = render_to_string(
                    'AppElecciones/subdistritos/reserva/crear.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'GET':
            if request.is_ajax():
                form = FormReservaSubdistrito()
        context = {'form': form}
        data['html_form'] = render_to_string(
            'AppElecciones/subdistritos/reserva/crear.html', context, request=request)
        return JsonResponse(data)


class ActualizarReservaEnSubdistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(
                    ReservaSubdistrito, pk=kwargs['pk'])
                #############################################
                integrante_actual = request.POST['integrante']
                if integrante_actual:
                    if integrante_actual != instancia.integrante.id:
                        # Proceso el anterior
                        Persona.objects.filter(id=instancia.integrante.id).update(
                            tiene_cargo=False, num_cargos=0)
                        # Proceso el actual
                        Persona.objects.filter(id=integrante_actual).update(
                            tiene_cargo=True, num_cargos=1)
                #############################################
                form = FormReservaSubdistrito(
                    request.POST, instance=instancia)
                if form.is_valid():
                    form.save()
                    data['form_es_valido'] = True
                else:
                    data['form_es_valido'] = False
                    context = {'form': form}
                    data['html_form'] = render_to_string(
                        'AppAlecciones/subdistritos/reserva/modificar.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            ReservaSubdistrito, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                form = FormReservaSubdistrito(instance=instancia)
        context = {'form': form}
        data['html_form'] = render_to_string(
            'AppElecciones/subdistritos/reserva/modificar.html', context, request=request)
        return JsonResponse(data)


class EliminarReservaEnSubdistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            ReservaSubdistrito, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                ########################################################
                Persona.objects.filter(id=instancia.integrante.id).update(
                    tiene_cargo=False, num_cargos=0)
                ########################################################
                instancia.delete()
                data['permitido'] = True
        return JsonResponse(data)
