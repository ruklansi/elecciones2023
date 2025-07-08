from django.db.models import Value, CharField, F, Case, When
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from model_utils import Choices

from AppElecciones.forms import FormVehiculosPropiosSubdistrito
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Persona, VehiculosPropios, Subdistrito, VehiculosPropiosSubdistrito


class ListarVehiculosPropioEnSubdistritosAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        id_del_subdistrito = request.POST.get('id_del_subdistrito', False)
        ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
        buscar = ['veh_propio__tipo_vehiculo_provisto__tipo_vehiculo_provisto', 'veh_propio__ni_patente_matricula',
                  'conductor__grado__grado', 'conductor__nombre', 'conductor__apellido', 'conductor__dni' 'zona_trabajo']
        columnas = (
        'id', 'veh_propio__tipo_vehiculo_provisto__tipo_vehiculo_provisto', 'veh_propio__ni_patente_matricula',
        'cond_veh_propio', 'zona_trabajo', 'editar', 'eliminar')
        agregados = {'cond_veh_propio': Concat(
            F('conductor__grado__grado'), Value(' '),
            F('conductor__nombre'), Value(' '),
            F('conductor__apellido'), Value(' DNI: '),
            F('conductor__dni'), output_field=CharField())}
        otros_filtros = {'subdistrito': id_del_subdistrito}
        con_permisos = True

        lista_veh_propios_subdistrito = listarParaDatatables(VehiculosPropiosSubdistrito, ORDENAR_COLUMNAS, buscar,
                                                             agregados,
                                                             columnas,
                                                             otros_filtros,
                                                             con_permisos, request.POST)
        resultado = dict()
        resultado['data'] = lista_veh_propios_subdistrito['items']
        resultado['draw'] = lista_veh_propios_subdistrito['draw']
        resultado['recordsTotal'] = lista_veh_propios_subdistrito['total']
        resultado['recordsFiltered'] = lista_veh_propios_subdistrito['count']
        # print(resultado)
        return JsonResponse(resultado, safe=False)


class CrearVehiculoPropioEnSubdistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            id_del_subdistrito = request.POST['id_del_subdistrito']
            if request.is_ajax():
                form = FormVehiculosPropiosSubdistrito(request.POST)
                if form.is_valid():
                    instancia = form.save(commit=False)
                    ##############################
                    # conductor = request.POST['conductor']
                    # if conductor:
                    #     Persona.objects.filter(id=conductor).update(es_conductor=True,
                    #                                                 num_conductor=F('num_conductor') + 1)
                    veh_prop = request.POST['veh_propio']
                    if veh_prop:
                        VehiculosPropios.objects.filter(id=veh_prop).update(tiene_destino=True, cantidad_empleos=F(
                            'cantidad_empleos') + 1)
                    ##############################
                    subdistrito_ = Subdistrito.objects.get(id=id_del_subdistrito)
                    instancia.subdistrito = subdistrito_
                    instancia.save()
                    data['form_es_valido'] = True
                else:
                    data['form_es_valido'] = False
                context = {'form': form}
                data['html_form'] = render_to_string(
                    'AppElecciones/subdistritos/vehpropio/crear.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'GET':
            if request.is_ajax():
                form = FormVehiculosPropiosSubdistrito()
            context = {'form': form}
            data['html_form'] = render_to_string(
                'AppElecciones/subdistritos/vehpropio/crear.html', context, request=request)
        return JsonResponse(data)


class ActualizarVehiculoPropioEnSubdistrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(
                    VehiculosPropiosSubdistrito, pk=kwargs['pk'])
                ##########################################
                if instancia.veh_propio:
                    veh_anterior = instancia.veh_propio
                else:
                    veh_anterior = 0

                # if instancia.conductor:
                #     conductor_anterior = instancia.conductor
                # else:
                #     conductor_anterior = 0
                #########################################
                form = FormVehiculosPropiosSubdistrito(
                    request.POST, instance=instancia)
                if form.is_valid():
                    ####################################
                    # conductor_actual = request.POST['conductor']
                    # if conductor_actual:
                    #     if conductor_actual != conductor_anterior.id:
                    #         # Anterior
                    #         Persona.objects.filter(id=conductor_anterior.id).update(
                    #             num_conductor=F('num_conductor') - 1)
                    #         Persona.objects.filter(id=conductor_anterior.id).update(
                    #             tiene_cargo=Case(When(num_cargos=0, then=False), default=True),
                    #             es_conductor=Case(When(num_conductor=0, then=False), default=True))
                    #         # Actual
                    #         Persona.objects.filter(id=conductor_actual).update( es_conductor=True,
                    #                                                            num_conductor=F('num_conductor') + 1)
                    veh_actual = request.POST['veh_propio']
                    if veh_actual:
                        if veh_actual != veh_anterior.id:
                            # Anterior
                            VehiculosPropios.objects.filter(id=veh_anterior.id).update(
                                cantidad_empleos=F('cantidad_empleos') - 1)
                            VehiculosPropios.objects.filter(id=veh_anterior.id).update(
                                tiene_destino=Case(When(cantidad_empleos=0, then=False), default=True))
                            # Actual
                            VehiculosPropios.objects.filter(id=veh_actual).update(
                                cantidad_empleos=F('cantidad_empleos') + 1)
                            VehiculosPropios.objects.filter(id=veh_actual).update(
                                tiene_destino=Case(When(cantidad_empleos=0, then=False), default=True))
                    ############################################
                    form.save()
                    data['form_es_valido'] = True
                else:
                    data['form_es_valido'] = False
                context = {'form': form}
                data['html_form'] = render_to_string(
                    'AppElecciones/subdistritos/vehpropio/modificar.html', context, request=request)
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            VehiculosPropiosSubdistrito, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                form = FormVehiculosPropiosSubdistrito(instance=instancia)
        context = {'form': form}
        data['html_form'] = render_to_string(
            'AppElecciones/subdistritos/vehpropio/modificar.html', context, request=request)
        return JsonResponse(data)


class EliminarVehiculosPropiosEnSubdstrito(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = dict()
        instancia = get_object_or_404(
            VehiculosPropiosSubdistrito, pk=kwargs['pk'])
        if request.method == 'GET':
            if request.is_ajax():
                ##############################
                if instancia.veh_propio:
                    VehiculosPropios.objects.filter(id=instancia.veh_propio.id).update(
                        cantidad_empleos=F('cantidad_empleos') - 1)
                    VehiculosPropios.objects.filter(id=instancia.veh_propio.id).update(
                        tiene_destino=Case(When(cantidad_empleos=0, then=False), default=True))
                # if instancia.conductor:
                #     Persona.objects.filter(id=instancia.conductor.id).update(num_conductor=F('num_conductor') - 1)
                #     Persona.objects.filter(id=instancia.conductor.id).update(
                #         tiene_cargo=Case(When(num_cargos=0, then=False), default=True),
                #         es_conductor=Case(When(num_conductor=0, then=False), default=True))
                ##############################
                instancia.delete()
                data['permitido'] = True
        return JsonResponse(data)
