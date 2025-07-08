from django.contrib import messages
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import ProtectedError, Case, When, F, Value, CharField, Func
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.list import ListView
from model_utils import Choices

from AppElecciones.forms import FormVehiculoContratado
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import VehiculosContratados, CamposEnMayusculas
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from guardian.mixins import PermissionRequiredMixin as guardianPermisos


class ListadoVehiculosContratados(PermisoDesdeDjango, ListView):
    model = VehiculosContratados
    template_name = "AppElecciones/vehiculos-contratados/listado.html"
    permission_required = 'AppElecciones.view_vehiculoscontratados'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            id_distrito = request.POST['id_distrito']
            puesto = request.POST['puesto']
            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
            buscar = ['tipo_vehiculo_contratado__tipo_vehiculo_civil', 'patente_matricula']
            columnas = ('id', 'distrito__distrito', 'tipo_vehiculo_contratado__tipo_vehiculo_civil',
                        'patente_matricula', 'puesto','sensor_rastreo', 'troncal_', 'editar', 'eliminar')
            agregados = {'puesto': Case(When(tiene_destino=True, then=Value('Si')), default=Value('No'),
                                        output_field=CharField()),
                         'sensor_rastreo': Case(When(posee_sensor_rastreo=True, then=Value('Si')), default=Value('No'),
                                        output_field=CharField()),
                         'troncal_': Case(
                                         When(troncal=Value(1), then=Value('Primaria')),
                                         When(troncal=Value(2), then=Value('Secundaria')),
                                         default=Value('--'),
                                         output_field=CharField()
                                     ),
                         }
            otros_filtros = {}
            if puesto != '':
                if puesto == 'conpuesto':
                    otros_filtros['tiene_destino'] = True
                if puesto == 'sinpuesto':
                    otros_filtros['tiene_destino'] = False
            if id_distrito != '':
                otros_filtros['distrito'] = id_distrito
            con_permisos = True
            vehiculos_contratados = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                         otros_filtros,
                                                         con_permisos, request.POST)

            result = dict()
            result['data'] = vehiculos_contratados['items']
            result['draw'] = vehiculos_contratados['draw']
            result['recordsTotal'] = vehiculos_contratados['total']
            result['recordsFiltered'] = vehiculos_contratados['count']

        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Vehículos contratados'
        context['listado_url'] = reverse_lazy('listado-vehiculos-contratados')
        return context


class CrearVehiculoContratado(PermisoDesdeDjango, CreateView):
    model = VehiculosContratados
    form_class = FormVehiculoContratado
    template_name = 'AppElecciones/vehiculos-contratados/crear_actualizar.html'
    permission_required = 'AppElecciones.add_vehiculoscontratados'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                form = self.form_class(request.POST)
                if form.is_valid():
                    instancia = form.save(commit=False)
                    if organizacion_del_usuario()['org'] == 'distrito':
                        instancia.distrito = organizacion_del_usuario()['instancia']
                    elif organizacion_del_usuario()['org'] == 'subdistrito':
                        instancia.distrito = organizacion_del_usuario()['sub_instancia']
                    instancia.save()
                    data['form_es_valido'] = True
                    data['mensaje'] = 'Vehículo agregado'
                else:
                    data['form_es_valido'] = False
                context = {'form': form, 'accion': 'crear'}
                data['html_form'] = render_to_string('AppElecciones/vehiculos-contratados/crear_actualizar.html',
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
                data['html_form'] = render_to_string('AppElecciones/vehiculos-contratados/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class ActualizarVehiculoContratado(guardianPermisos, UpdateView):
    model = VehiculosContratados
    form_class = FormVehiculoContratado
    template_name = 'AppElecciones/vehiculos-contratados/crear_actualizar.html'
    permission_required = 'AppElecciones.change_vehiculoscontratados'
    raise_exception = True
    accept_global_perms = False

    def post(self, request, *args, **kwargs):
        data = dict()
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(self.model, pk=kwargs['pk'])
                form = self.form_class(request.POST, instance=instancia)
                if form.is_valid():
                    dato = form.save(commit=False)
                    dato.save()
                    data['form_es_valido'] = True
                    data['mensaje'] = 'Vehículo actualizado'
                else:
                    data['form_es_valido'] = False
                    context = {'form': form, 'accion': 'editar'}
                    data['html_form'] = render_to_string('AppElecciones/vehiculos-contratados/crear_actualizar.html',
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
                data['html_form'] = render_to_string('AppElecciones/vehiculos-contratados/crear_actualizar.html',
                                                     context, request=request)
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class EliminarVehiculoContratado(guardianPermisos, DeleteView):
    model = VehiculosContratados
    permission_required = 'AppElecciones.delete_vehiculoscontratados'
    raise_exception = True
    accept_global_perms = False

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            if request.is_ajax():
                data = dict()
                instancia = get_object_or_404(self.model, pk=kwargs['pk'])

                try:
                    instancia.delete()
                    data['borrado'] = True
                    data['mensaje'] = 'Vehículo eliminado'
                except ProtectedError as mierror:
                    data['borrado'] = False
                    data['mierror'] = 'Imposible eliminar el vehículo porque está asignado en la organización'
                return JsonResponse(data)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class DetalleVehiculoContratado(guardianPermisos, DetailView):
    model = VehiculosContratados
    template_name = 'AppElecciones/vehiculos-contratados/detalle.html'
    permission_required = 'AppElecciones.view_vehiculoscontratados'
    raise_exception = True
    accept_global_perms = False

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(self.model, pk=kwargs['pk'])
                resultado = dict()

                cge = self.model.objects.filter(id=instancia.id, vehiculo_contratado_cge__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('vehiculo_contratado_cge__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('vehiculo_contratado_cge__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('vehiculo_contratado_cge__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('vehiculo_contratado_cge__tareas__tareas'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona', flat=True).first()
                try:
                    datos_cge = list(cge)
                except:
                    datos_cge = []

                distrito = self.model.objects.filter(id=instancia.id, vehiculo_contratado_distrito__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('vehiculo_contratado_distrito__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('vehiculo_contratado_distrito__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(
                                                      F('vehiculo_contratado_distrito__hasta'),
                                                      Value('dd/MM/yyyy'),
                                                      function='to_char',
                                                      output_field=CharField()
                                                  ),
                                                  Value(' Tarea: '),
                                                  F('vehiculo_contratado_distrito__tareas__tareas'),
                                                  Value(' Distrito: '),
                                                  F('vehiculo_contratado_distrito__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_distrito = list(distrito)
                except:
                    datos_distrito = []


                subdistrito = self.model.objects.filter(id=instancia.id, vehiculo_contratado_subdistrito__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('vehiculo_contratado_subdistrito__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('vehiculo_contratado_subdistrito__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('vehiculo_contratado_subdistrito__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('vehiculo_contratado_subdistrito__tareas__tareas'),
                                                  Value(' Subdistrito: '),
                                                  F('vehiculo_contratado_subdistrito__subdistrito__subdistrito'),
                                                  Value(' Distrito: '),
                                                  F('vehiculo_contratado_subdistrito__subdistrito__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_subdistrito = list(subdistrito)
                except:
                    datos_subdistrito = []

                seccion = self.model.objects.filter(id=instancia.id, vehiculo_contratado_seccion__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('vehiculo_contratado_seccion__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('vehiculo_contratado_seccion__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('vehiculo_contratado_seccion__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('vehiculo_contratado_seccion__tareas__tareas'),
                                                  Value(' Sección: '),
                                                  F('vehiculo_contratado_seccion__seccion__seccion'),
                                                  Value(' Subdistrito: '),
                                                  F('vehiculo_contratado_seccion__seccion__subdistrito__subdistrito'),
                                                  Value(' Distrito: '),
                                                  F('vehiculo_contratado_seccion__seccion__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_seccion = list(seccion)
                except:
                    datos_seccion = []

                context = {'vehiculo': {'patente': instancia.patente_matricula,
                                        'tipo': instancia.tipo_vehiculo_contratado.tipo_vehiculo_civil,
                                        'cge': datos_cge,
                                        'distrito': datos_distrito,
                                        'subdistrito': datos_subdistrito,
                                        'seccion': datos_seccion,
                                        }}
                resultado['resultado'] = render_to_string('AppElecciones/vehiculos-contratados/detalle.html',
                                                          context, request=request)
                return JsonResponse(resultado, safe=False)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')

