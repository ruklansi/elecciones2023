from django.db.models import Value, CharField, F, Case, When
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from model_utils import Choices

from AppElecciones.forms import FormVehiculosContratadosSubdistrito
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Persona, Subdistrito, VehiculosContratadosSubdistrito, VehiculosContratados


class ListarVehiculosContratadosSubdistritoAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        id_del_subdistrito = request.POST['id_del_subdistrito']
        ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
        buscar = ['vehiculo_contratado__tipo_vehiculo_contratado__tipo_vehiculo_civil', 'zona_trabajo',
                  'responsable__grado__grado', 'responsable__nombre', 'responsable__apellido', 'responsable__dni', 'vehiculo_contratado__patente_matricula']
        columnas = ('id', 'vehiculo_contratado__tipo_vehiculo_contratado__tipo_vehiculo_civil', 'zona_trabajo',
                    'cond_veh_cont', 'vehiculo_contratado__patente_matricula', 'editar', 'eliminar')
        agregados = {'cond_veh_cont': Concat(
            F('responsable__grado__grado'), Value(' '),
            F('responsable__nombre'), Value(' '),
            F('responsable__apellido'), Value(' DNI: '),
            F('responsable__dni'), output_field=CharField())}
        otros_filtros = {'subdistrito': id_del_subdistrito}
        con_permisos = True

        lista_veh_contratados_subdistrito = listarParaDatatables(VehiculosContratadosSubdistrito, ORDENAR_COLUMNAS,
                                                                 buscar,
                                                                 agregados,
                                                                 columnas,
                                                                 otros_filtros,
                                                                 con_permisos, request.POST)

        resultado = dict()
        resultado['data'] = lista_veh_contratados_subdistrito['items']
        resultado['draw'] = lista_veh_contratados_subdistrito['draw']
        resultado['recordsTotal'] = lista_veh_contratados_subdistrito['total']
        resultado['recordsFiltered'] = lista_veh_contratados_subdistrito['count']
        # print(resultado)
        return JsonResponse(resultado, safe=False)


class CrearVehiculoContratadoEnSubdistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            id_del_subdistrito = request.POST['id_del_subdistrito']
            if request.is_ajax():
                form = FormVehiculosContratadosSubdistrito(request.POST)
                if form.is_valid():
                    ################################
                    # responsable = request.POST['responsable']
                    # if responsable:
                    #     Persona.objects.filter(id=responsable).update( es_conductor=True,
                    #                                                   num_conductor=F('num_conductor') + 1)
                    veh_cont = request.POST['vehiculo_contratado']
                    if veh_cont:
                        VehiculosContratados.objects.filter(id=veh_cont).update(tiene_destino=True, cantidad_empleos=F(
                            'cantidad_empleos') + 1)
                    #################################
                    instancia = form.save(commit=False)
                    subdistrito_ = Subdistrito.objects.get(id=id_del_subdistrito)
                    instancia.subdistrito = subdistrito_
                    instancia.save()
                    data['form_es_valido'] = True
                else:
                    data['form_es_valido'] = False
                context = {'form': form}
                data['html_form'] = render_to_string(
                    'AppElecciones/subdistritos/vhcontratado/crear.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'GET':
            if request.is_ajax():
                form = FormVehiculosContratadosSubdistrito()
                context = {'form': form}
                data['html_form'] = render_to_string(
                    'AppElecciones/subdistritos/vhcontratado/crear.html', context, request=request)
        return JsonResponse(data)


class ActualizarVehiculoContratadoEnSubdistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(VehiculosContratadosSubdistrito, pk=kwargs['pk'])
                ################################
                if instancia.vehiculo_contratado:
                    veh_anterior = instancia.vehiculo_contratado
                else:
                    veh_anterior = 0

                # if instancia.responsable:
                #     responsable_anterior = instancia.responsable
                # else:
                #     responsable_anterior = 0
                #################################
                form = FormVehiculosContratadosSubdistrito(request.POST, instance=instancia)
                if form.is_valid():
                    #############################################
                    # responsable_actual = request.POST['responsable']
                    # if responsable_actual:
                    #     if responsable_actual != responsable_anterior.id:
                    #         # Anterior
                    #         Persona.objects.filter(id=responsable_anterior.id).update(
                    #             num_conductor=F('num_conductor') - 1)
                    #         Persona.objects.filter(id=responsable_anterior.id).update(
                    #             tiene_cargo=Case(When(num_cargos=0, then=False), default=True),
                    #             es_conductor=Case(When(num_conductor=0, then=False), default=True))
                    #         # Actual
                    #         Persona.objects.filter(id=responsable_actual).update(es_conductor=True,
                    #                                                              num_conductor=F('num_conductor') + 1)
                    veh_actual = request.POST['vehiculo_contratado']
                    if veh_actual:
                        if veh_actual != veh_anterior.id:
                            # Anterior
                            VehiculosContratados.objects.filter(id=veh_anterior.id).update(
                                cantidad_empleos=F('cantidad_empleos') - 1)
                            VehiculosContratados.objects.filter(id=veh_anterior.id).update(
                                tiene_destino=Case(When(cantidad_empleos=0, then=False), default=True))
                            # Actual
                            VehiculosContratados.objects.filter(id=veh_actual).update(
                                cantidad_empleos=F('cantidad_empleos') + 1)
                            VehiculosContratados.objects.filter(id=veh_actual).update(
                                tiene_destino=Case(When(cantidad_empleos=0, then=False), default=True))
                    #################################################
                    form.save()
                    data['form_es_valido'] = True
                else:
                    data['form_es_valido'] = False
                    context = {'form': form}
                    data['html_form'] = render_to_string(
                        'AppElecciones/subdistritos/vhcontratado/modificar.html', context, request=request)

        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            VehiculosContratadosSubdistrito, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                form = FormVehiculosContratadosSubdistrito(instance=instancia)
                context = {'form': form}
                data['html_form'] = render_to_string(
                    'AppElecciones/subdistritos/vhcontratado/modificar.html', context, request=request)
        return JsonResponse(data)


class EliminarVehiculosContratadoEnSubdistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            VehiculosContratadosSubdistrito, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                ############################################
                if instancia.vehiculo_contratado:
                    VehiculosContratados.objects.filter(id=instancia.vehiculo_contratado.id).update(
                        cantidad_empleos=F('cantidad_empleos') - 1)
                    VehiculosContratados.objects.filter(id=instancia.vehiculo_contratado.id).update(
                        tiene_destino=Case(When(cantidad_empleos=0, then=False), default=True))
                # if instancia.responsable:
                #     Persona.objects.filter(id=instancia.responsable.id).update(num_conductor=F('num_conductor') - 1)
                #     Persona.objects.filter(id=instancia.responsable.id).update(
                #         tiene_cargo=Case(When(num_cargos=0, then=False), default=True),
                #         es_conductor=Case(When(num_conductor=0, then=False), default=True))
                ############################################
                instancia.delete()
                data['permitido'] = True
        return JsonResponse(data)
