from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import ProtectedError, Value, Case, When, F, Func, CharField
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from guardian.mixins import PermissionRequiredMixin as guardianPermisos
from model_utils import Choices

from AppAdministracion.models import CamposEnMayusculas
from AppElecciones.forms import FormVehiculoPropio
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import VehiculosPropios, Distrito, Fuerza, Subdistrito, Seccion, Circuito


class ListadoVehiculosPropios(PermisoDesdeDjango, ListView):
    model = VehiculosPropios
    template_name = "AppElecciones/vehiculos-propios/listado.html"
    permission_required = 'AppElecciones.view_vehiculospropios'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            id_distrito = request.POST['id_distrito']
            puesto = request.POST['puesto']
            fuerza = request.POST['fuerza']

            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
            buscar = ['tipo_vehiculo_provisto__tipo_vehiculo_provisto', 'ni_patente_matricula', 'unidad__nombre']
            columnas = (
            'id', 'distrito__distrito', 'tipo_vehiculo_provisto__tipo_vehiculo_provisto', 'ni_patente_matricula',
            'unidad__nombre', 'puesto', 'sensor_rastreo', 'troncal_', 'editar', 'eliminar')
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
            if fuerza != '':
                otros_filtros['fuerza'] = fuerza
            if puesto != '':
                if puesto == 'conpuesto':
                    otros_filtros['tiene_destino'] = True
                if puesto == 'sinpuesto':
                    otros_filtros['tiene_destino'] = False
            if id_distrito != '':
                otros_filtros['distrito'] = id_distrito
            con_permisos = True
            vehiculos_propios = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                     otros_filtros,
                                                     con_permisos, request.POST)

            result = dict()
            result['data'] = vehiculos_propios['items']
            result['draw'] = vehiculos_propios['draw']
            result['recordsTotal'] = vehiculos_propios['total']
            result['recordsFiltered'] = vehiculos_propios['count']
            # print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Vehículos provistos'
        context['listado_url'] = reverse_lazy('listado-de-vehiculos-propios')
        context['crear_url'] = reverse_lazy('crear-vehiculo-propio')
        return context


class CrearVehiculoPropio(PermisoDesdeDjango, SuccessMessageMixin, CreateView):
    model = VehiculosPropios
    form_class = FormVehiculoPropio
    template_name = 'AppElecciones/vehiculos-propios/crear.html'
    success_message = 'Vehículo agregado'
    success_url = reverse_lazy('listado-de-vehiculos-propios')
    permission_required = 'AppElecciones.add_vehiculospropios'
    raise_exception = True

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        if organizacion_del_usuario()['org'] == 'distrito':
            self.object.distrito = organizacion_del_usuario()['instancia']
        elif organizacion_del_usuario()['org'] == 'subdistrito':
            self.object.distrito = organizacion_del_usuario()['sub_instancia']
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar vehículo provisto'
        return context


class ActualizarVehiculoPropio(guardianPermisos, SuccessMessageMixin, UpdateView):
    model = VehiculosPropios
    form_class = FormVehiculoPropio
    template_name = 'AppElecciones/vehiculos-propios/crear.html'
    success_message = 'Vehículo actualizado'
    success_url = reverse_lazy('listado-de-vehiculos-propios')
    permission_required = 'AppElecciones.change_vehiculospropios'
    raise_exception = True
    accept_global_perms = False

    # permission_required = 'change_vehiculospropios'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar vehículo provisto'
        return context


class EliminarVehiculoPropio(guardianPermisos, SuccessMessageMixin, DeleteView):
    model = VehiculosPropios
    template_name = 'AppElecciones/vehiculos-propios/eliminar.html'
    success_url = reverse_lazy('listado-de-vehiculos-propios')
    permission_required = 'AppElecciones.delete_vehiculospropios'
    raise_exception = True
    accept_global_perms = False

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()
            messages.success(
                self.request, "Vehículo provisto eliminado")
            return HttpResponseRedirect(success_url)
        except ProtectedError:
            messages.success(
                self.request, (
                    "Imposible eliminar este vehículo porque esta asignado en la organización. Primero elimínelo de la misma."))
            return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar vehículo provisto'
        return context


class DetalleVehiculoPropio(DetailView):
    model = VehiculosPropios
    template_name = 'AppElecciones/vehiculos-propios/detalle.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.is_ajax():
                instancia = get_object_or_404(self.model, pk=kwargs['pk'])
                resultado = dict()
                # Evalúo si se lo empleo en el CGE
                cge = self.model.objects.filter(id=instancia.id, veh_propio_cge__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_propio_cge__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_propio_cge__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('veh_propio_cge__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('veh_propio_cge__tareas__tareas'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona', flat=True).first()
                try:
                    datos_cge = list(cge)
                except:
                    datos_cge = []
                # Evalúo si se lo empleo en el Distrito
                distrito = self.model.objects.filter(id=instancia.id, veh_propio_distrito__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_propio_distrito__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_propio_distrito__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(
                                                      F('veh_propio_distrito__hasta'),
                                                      Value('dd/MM/yyyy'),
                                                      function='to_char',
                                                      output_field=CharField()
                                                  ),
                                                  Value(' Tarea: '),
                                                  F('veh_propio_distrito__tareas__tareas'),
                                                  Value(' Distrito: '),
                                                  F('veh_propio_distrito__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_distrito = list(distrito)
                except:
                    datos_distrito = []

                # Evalúo si se lo empleo en el Distrito
                subdistrito = self.model.objects.filter(id=instancia.id, veh_prop_sub__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_prop_sub__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_prop_sub__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('veh_prop_sub__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('veh_prop_sub__tareas__tareas'),
                                                  Value(' Subdistrito: '),
                                                  F('veh_prop_sub__subdistrito__subdistrito'),
                                                  Value(' Distrito: '),
                                                  F('veh_prop_sub__subdistrito__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_subdistrito = list(subdistrito)
                except:
                    datos_subdistrito = []

                seccion = self.model.objects.filter(id=instancia.id, veh_prop_sec__isnull=False). \
                    annotate(zona=ArrayAgg(Concat(Value('Zona: '),
                                                  F('veh_prop_sec__zona_trabajo'),
                                                  Value(' Desde: '),
                                                  Func(F('veh_prop_sec__desde'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Hasta: '),
                                                  Func(F('veh_prop_sec__hasta'),
                                                       Value('dd/MM/yyyy'),
                                                       function='to_char',
                                                       output_field=CharField()
                                                       ),
                                                  Value(' Tarea: '),
                                                  F('veh_prop_sec__tareas__tareas'),
                                                  Value(' Sección: '),
                                                  F('veh_prop_sec__seccion__seccion'),
                                                  Value(' Subdistrito: '),
                                                  F('veh_prop_sec__seccion__subdistrito__subdistrito'),
                                                  Value(' Distrito: '),
                                                  F('veh_prop_sec__seccion__distrito__distrito'),
                                                  output_field=CamposEnMayusculas())
                                           )).values_list('zona',
                                                          flat=True).first()
                try:
                    datos_seccion = list(seccion)
                except:
                    datos_seccion = []

                context = {'vehiculo': {'patente': instancia.ni_patente_matricula,
                                        'tipo': instancia.tipo_vehiculo_provisto.tipo_vehiculo_provisto,
                                        'unidad': instancia.unidad.nombre,
                                        'cge': datos_cge,
                                        'distrito': datos_distrito,
                                        'subdistrito': datos_subdistrito,
                                        'seccion': datos_seccion,
                                        }}
                resultado['resultado'] = render_to_string('AppElecciones/vehiculos-propios/detalle.html',
                                                          context, request=request)
                return JsonResponse(resultado, safe=False)
            messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
            return redirect('inicio')


class FiltrosParaVehPropiosAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        resultado = dict()
        accion = (request.POST['accion'])
        if accion == 'cargar-distritos':
            data = []
            # usuario = request.user
            # for i in get_objects_for_user(usuario, 'view_distrito', Distrito).all().order_by('distrito'):
            for i in Distrito.objects.all().order_by('distrito'):
                if i.distrito != '--':
                    data.append({'id': i.id, 'distrito': i.distrito})
            resultado['datos'] = data
            resultado['hay_distritos'] = True
        if accion == 'cargar-fuerzas':
            data = []
            for f in Fuerza.objects.all().order_by('fuerza'):
                data.append({'id': f.id, 'fuerza': f.fuerza})
            resultado['datos'] = data
            resultado['hay_fuerza'] = True

        if accion == 'filtrar-subdistritos':
            sub = Subdistrito.objects.filter(distrito_id=request.POST['id'])
            if sub:
                data = []
                for s in Subdistrito.objects.filter(distrito_id=request.POST['id']):
                    data.append({'id': s.id, 'subdistrito': s.subdistrito})
                resultado['datos'] = data
                resultado['hay_subdistrito'] = True
            elif not sub:
                data = []
                for t in Seccion.objects.filter(distrito_id=request.POST['id']):
                    data.append({'id': t.id, 'seccion': t.seccion})
                resultado['datos'] = data
                resultado['hay_subdistrito'] = False
        if accion == 'filtrar-seccion':
            data = []
            # aca el id es un subdistrito
            for s in Seccion.objects.filter(subdistrito_id=request.POST['id']):
                data.append({'id': s.id, 'seccion': s.seccion})
            resultado['datos'] = data
            resultado['hay_seccion'] = True
        if accion == 'filtrar-circuito':
            data = []
            for c in Circuito.objects.filter(seccion_id=request.POST['id']):
                data.append({'id': c.id, 'circuito': c.circuito})
            resultado['datos'] = data
            resultado['hay_circuito'] = True
        return JsonResponse(resultado, safe=False)
