from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from guardian.mixins import PermissionRequiredMixin as guardianPermiso
from model_utils import Choices

from AppElecciones.forms import FormSed
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Sed


class ListaDeSed(PermisoDesdeDjango, ListView):
    model = Sed
    template_name = "AppElecciones/SED/listado.html"
    permission_required = 'AppElecciones.view_sed'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            id_distrito = request.POST['id_distrito']
            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
            buscar = ['distrito__distrito', 'direccion', 'sed', 'localidad', 'telefono']
            columnas = ('id', 'distrito__distrito', 'direccion', 'sed', 'localidad', 'telefono', 'editar', 'eliminar')
            agregados = None
            otros_filtros = {}
            if id_distrito != '':
                otros_filtros['distrito'] = id_distrito
            con_permisos = True
            lista_sed = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                             otros_filtros,
                                             con_permisos, request.POST)
            result = dict()
            result['data'] = lista_sed['items']
            result['draw'] = lista_sed['draw']
            result['recordsTotal'] = lista_sed['total']
            result['recordsFiltered'] = lista_sed['count']
            # print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Sucursal Electoral Digital (SED)'
        context['listado_url'] = reverse_lazy('listado-de-sed')
        context['crear_url'] = reverse_lazy('crear-sed')
        return context


class CrearSed(PermisoDesdeDjango, SuccessMessageMixin, CreateView):
    model = Sed
    form_class = FormSed
    template_name = 'AppElecciones/SED/crear.html'
    success_message = 'Sucursal Electoral Digital agregada'
    success_url = reverse_lazy('listado-de-sed')
    permission_required = 'AppElecciones.add_sed'
    raise_exception = True

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        self.object.distrito = organizacion_del_usuario()['instancia']
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar SED'
        return context


class ActualizarSed(guardianPermiso, SuccessMessageMixin, UpdateView):
    model = Sed
    form_class = FormSed
    template_name = 'AppElecciones/SED/crear.html'
    success_message = 'Sucursal Electoral Digital actualizada'
    success_url = reverse_lazy('listado-de-sed')
    permission_required = 'AppElecciones.change_sed'
    raise_exception = True
    ccept_global_perms = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar Sucursal Electoral Digital'
        return context


class EliminarSed(guardianPermiso, SuccessMessageMixin, DeleteView):
    model = Sed
    template_name = 'AppElecciones/SED/eliminar.html'
    success_url = reverse_lazy('listado-de-sed')
    permission_required = 'AppElecciones.delete_sed'
    raise_exception = True
    ccept_global_perms = True

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        # error_url = self.get_error_url()
        try:
            self.object.delete()
            messages.success(
                self.request, "Sucursal Electoral Digital eliminada")
            return HttpResponseRedirect(success_url)
        except ProtectedError:
            # print(self.object)
            messages.success(
                self.request, (
                    "Imposible eliminar la Sucursal Electoral Digital (SED)"))
            return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Sucursal Electoral Digital'
        return context
