from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from guardian.mixins import PermissionRequiredMixin as guardianPermiso
from model_utils import Choices

from AppElecciones.forms import FormLed
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Led


class ListadoLed(PermisoDesdeDjango, ListView):
    model = Led
    template_name = "AppElecciones/LED/listado.html"
    permission_required = 'AppElecciones.view_led'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            id_distrito = request.POST['id_distrito']
            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
            buscar = ['distrito__distrito', 'direccion', 'tipo__tipo', 'obs']
            columnas = ('id', 'distrito__distrito', 'direccion', 'tipo__tipo', 'obs', 'editar', 'eliminar')
            agregados = None
            otros_filtros = {}
            if id_distrito != '':
                otros_filtros['distrito'] = id_distrito
            con_permisos = True
            lista_led = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                             otros_filtros,
                                             con_permisos, request.POST)
            result = dict()
            result['data'] = lista_led['items']
            result['draw'] = lista_led['draw']
            result['recordsTotal'] = lista_led['total']
            result['recordsFiltered'] = lista_led['count']
            # print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Lugar de Escrutinio Definitivo (LED)'
        context['listado_url'] = reverse_lazy('listado-de-led')
        context['crear_url'] = reverse_lazy('crear-led')
        return context


class CrearLed(PermisoDesdeDjango, SuccessMessageMixin, CreateView):
    model = Led
    form_class = FormLed
    template_name = 'AppElecciones/LED/crear.html'
    success_message = 'LED agregado'
    success_url = reverse_lazy('listado-de-led')
    permission_required = 'AppElecciones.add_led'
    raise_exception = True

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        self.object.distrito = organizacion_del_usuario()['instancia']
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar Lugar de Escrutinio Definitivo (LED)'
        return context


class ActualizarLed(guardianPermiso, SuccessMessageMixin, UpdateView):
    model = Led
    form_class = FormLed
    template_name = 'AppElecciones/LED/crear.html'
    success_message = 'LED actualizado'
    success_url = reverse_lazy('listado-de-led')
    permission_required = 'AppElecciones.change_led'
    raise_exception = True
    ccept_global_perms = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar Lugar de Escrutinio Definitivo (LED)'
        return context


class EliminarLed(guardianPermiso, SuccessMessageMixin, DeleteView):
    model = Led
    template_name = 'AppElecciones/LED/eliminar.html'
    success_url = reverse_lazy('listado-de-led')
    permission_required = 'AppElecciones.delete_led'
    raise_exception = True
    ccept_global_perms = True

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        # error_url = self.get_error_url()
        try:
            self.object.delete()
            messages.success(
                self.request, "LED eliminado")
            return HttpResponseRedirect(success_url)
        except ProtectedError:
            # print(self.object)
            messages.error(
                self.request, (
                    "Imposible eliminar el LED porque tiene seguridad asignada. Elimínela primero."))
            return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar LED'
        return context


class DetalleLed(PermisoDesdeDjango, DetailView):
    model = Led
    template_name = 'AppElecciones/LED/detalles.html'
    permission_required = 'AppElecciones.view_led'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Información del LED'
        return context
