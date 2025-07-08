from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from guardian.mixins import PermissionRequiredMixin as guardianPermisos
from model_utils import Choices

from AppElecciones.forms import FormMovimientos
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Movimientos


class ListadoMovimientos(PermisoDesdeDjango, ListView):
    model = Movimientos
    template_name = "AppElecciones/movimientos/listado.html"
    permission_required = 'AppElecciones.view_movimientos'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            id_distrito = request.POST['id_distrito']
            ORDENAR_COLUMNAS = Choices(('1', 'fecha_creacion'))
            buscar = ['tipo__tipo', 'efectivos', 'vehiculos', 'inicio', 'fin', 'distrito__distrito']
            columnas = ('id', 'tipo__tipo', 'efectivos', 'vehiculos', 'inicio', 'fin', 'distrito__distrito',
                        'editar', 'eliminar')
            agregados = None
            otros_filtros = {}
            if id_distrito != '':
                otros_filtros['distrito'] = id_distrito
            con_permisos = True
            movimientos = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                               otros_filtros,
                                               con_permisos, request.POST)
            result = dict()
            result['data'] = movimientos['items']
            result['draw'] = movimientos['draw']
            result['recordsTotal'] = movimientos['total']
            result['recordsFiltered'] = movimientos['count']
            # print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Movimientos'
        context['listado_url'] = reverse_lazy('listado-de-movimientos')
        context['crear_url'] = reverse_lazy('crear-movimiento')
        return context


class CrearMovimiento(PermisoDesdeDjango, SuccessMessageMixin, CreateView):
    model = Movimientos
    form_class = FormMovimientos
    template_name = 'AppElecciones/movimientos/crear.html'
    success_message = 'Movimiento agregado'
    success_url = reverse_lazy('listado-de-movimientos')
    permission_required = 'AppElecciones.add_movimientos'
    raise_exception = True

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        self.object.distrito = organizacion_del_usuario()['instancia']
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar movimiento'
        return context


class ActualizarMovimiento(guardianPermisos, SuccessMessageMixin, UpdateView):
    model = Movimientos
    form_class = FormMovimientos
    template_name = 'AppElecciones/movimientos/crear.html'
    success_message = 'Movimiento actualizado'
    success_url = reverse_lazy('listado-de-movimientos')
    permission_required = 'AppElecciones.change_movimientos'
    raise_exception = True
    accept_global_perms = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar movimiento'
        return context


class EliminarMovimiento(guardianPermisos, SuccessMessageMixin, DeleteView):
    model = Movimientos
    template_name = 'AppElecciones/movimientos/eliminar.html'
    success_url = reverse_lazy('listado-de-movimientos')
    permission_required = 'AppElecciones.delete_movimientos'
    raise_exception = True
    accept_global_perms = False

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        # error_url = self.get_error_url()
        try:
            self.object.delete()
            messages.success(self.request, "Movimiento eliminado")
            return HttpResponseRedirect(success_url)
        except ProtectedError:
            # print(self.object)
            messages.success(
                self.request, "Imposible eliminar el movimiento")
            return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar movimiento'
        return context


class DetalleMovimiento(PermisoDesdeDjango, DetailView):
    model = Movimientos
    template_name = 'AppElecciones/movimientos/detalles.html'
    permission_required = 'AppElecciones.view_movimientos'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Detalle del movimiento'
        return context
