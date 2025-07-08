from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from guardian.mixins import PermissionRequiredMixin as guardianPermisos
from model_utils import Choices

from AppElecciones.forms import NovedadesGenerales, FormNovedadesGenerales
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables


class ListadoNovGeneralesGenerales(ListView):
    model = NovedadesGenerales
    template_name = "AppElecciones/novedadesgenerales/listado.html"
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":

            id_distrito = request.POST['id_distrito']
            tipo_novedad = request.POST['tipo_novedad']
            subsanada = request.POST['subsanada']

            ORDENAR_COLUMNAS = Choices(('1', 'fecha_creacion'))
            buscar = []
            columnas = ('id', 'distrito__distrito', 'fecha', 'tipo__tipo', 'detalle', 'subsanada',
                        'medidas_adoptadas', 'editar', 'eliminar')
            agregados = None

            otros_filtros = {}
            if id_distrito != '':
                otros_filtros['distrito'] = id_distrito
            if tipo_novedad != '':
                otros_filtros['tipo'] = tipo_novedad
            if subsanada != '':
                otros_filtros['subsanada'] = subsanada

            con_permisos = True

            todaslasnovedades = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                     otros_filtros,
                                                     con_permisos, request.POST)

            result = dict()
            result['data'] = todaslasnovedades['items']
            result['draw'] = todaslasnovedades['draw']
            result['recordsTotal'] = todaslasnovedades['total']
            result['recordsFiltered'] = todaslasnovedades['count']
            #print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Novedades fuera de los locales de votación'
        context['listado_url'] = reverse_lazy('listado-de-novedades-generales')
        context['crear_url'] = reverse_lazy('crear-novedades-generales')
        return context


class CrearNovedadesGenerales(PermisoDesdeDjango, SuccessMessageMixin, CreateView):
    model = NovedadesGenerales
    form_class = FormNovedadesGenerales
    template_name = 'AppElecciones/novedadesgenerales/crear.html'
    success_message = 'Novedad agregada'
    success_url = reverse_lazy('listado-de-novedades-generales')
    permission_required = 'AppElecciones.add_novedadesgenerales'
    raise_exception = True

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        if organizacion_del_usuario()['org'] == 'distrito':
            self.object.distrito = organizacion_del_usuario()['instancia']
        else:
            self.object.distrito = organizacion_del_usuario()['sub_instancia']
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar novedad durante la Operación fuera de los locales de votación '
        return context


class ActualizarNovedadesGenerales(guardianPermisos, SuccessMessageMixin, UpdateView):
    model = NovedadesGenerales
    form_class = FormNovedadesGenerales
    template_name = 'AppElecciones/novedadesgenerales/crear.html'
    success_message = 'Novedad actualizada'
    permission_required = 'AppElecciones.change_novedadesgenerales'
    raise_exception = True
    accept_global_perms = False
    success_url = reverse_lazy('listado-de-novedades-generales')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar novedad'
        return context


class EliminarNovedadesGenerales(guardianPermisos, SuccessMessageMixin, DeleteView):
    model = NovedadesGenerales
    template_name = 'AppElecciones/novedadesgenerales/eliminar.html'
    success_url = reverse_lazy('listado-de-novedades-generales')
    raise_exception = True
    accept_global_perms = False
    permission_required = 'AppElecciones.delete_novedadesgenerales'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        # error_url = self.get_error_url()
        try:
            self.object.delete()
            messages.success(self.request, "Novedad eliminada")
            return HttpResponseRedirect(success_url)
        except ProtectedError:
            # print(self.object)
            messages.success(
                self.request, "Imposible eliminar la novedad")
            return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar novedad'
        return context


class DetalleNovedadesGenerales(guardianPermisos, DetailView):
    model = NovedadesGenerales
    template_name = 'AppElecciones/novedadesgenerales/detalle.html'
    raise_exception = True
    accept_global_perms = False
    permission_required = 'AppElecciones.view_novedadesgenerales'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detalle de la novedad: '
        return context


class NovedadesTiempoReal(ListView):
    model = NovedadesGenerales
    template_name = "AppElecciones/novedadesgenerales/listadonovtiemporeal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Novedades NO SUBSANADAS en tiempo real'
        return context


class ListarNoveTiempoRealPorAjax(View):

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.is_ajax():
                accion = request.POST.get('accion')

                # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                # if x_forwarded_for:
                #    ipaddress = x_forwarded_for.split(',')[-1].strip()
                # else:
                # ipaddress = request.META.get('REMOTE_ADDR')

                # print(ipaddress)

                if accion == 'cargar-nov-tiempo-real':
                    #
                    #     # id_seccion = (request.POST['id_seccion'])
                    resultado = dict()
                    novedades = NovedadesGenerales.objects.filter(subsanada='No')
                    cant_criticas = novedades.filter(tipo__nivel='3').count()
                    cant_altas = novedades.filter(tipo__nivel='2').count()
                    cant_medias = novedades.filter(tipo__nivel='1').count()

                    data = []
                    for n in novedades:
                        data.append(
                            {'distrito': n.distrito.distrito, 'fecha_novedad': n.fecha.strftime('%d/%m/%Y %H:%M'),
                             'tipo': n.tipo.tipo, 'detalle': n.detalle, 'subsanada': n.subsanada,
                             'medidas_adoptadas': n.medidas_adoptadas, 'nivel': n.tipo.nivel,
                             'latitud': n.ubicacion.y, 'longitud': n.ubicacion.x,
                             'id': n.id})
                        resultado['datos'] = data
                        resultado['cant_criticas'] = cant_criticas
                        resultado['cant_medias'] = cant_medias
                        resultado['cant_altas'] = cant_altas
            return JsonResponse(resultado, safe=False)
