from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from guardian.mixins import PermissionRequiredMixin as guardianPermiso
from model_utils import Choices

from AppElecciones.forms import FormSed, FormLugarInteres
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import Sed, LugarInteres


class ListaLugarInteres(PermisoDesdeDjango, ListView):
    model = LugarInteres
    template_name = "AppElecciones/lugar/listado.html"
    permission_required = 'AppElecciones.view_lugarinteres'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            id_distrito = request.POST['id_distrito']
            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
            buscar = ['distrito__distrito', 'direccion', 'tipo_lugar__tipo', 'telefono', 'obs', 'autoridad']
            columnas = ('id', 'distrito__distrito', 'direccion', 'autoridad','tipo_lugar__tipo', 'telefono', 'obs', 'editar', 'eliminar')
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
            #print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Instituciones'
        context['listado_url'] = reverse_lazy('listado-lugar-interes')
        context['crear_url'] = reverse_lazy('crear-lugar-interes')
        return context


class CrearLugarInteres(PermisoDesdeDjango, SuccessMessageMixin, CreateView):
    model = LugarInteres
    form_class = FormLugarInteres
    template_name = 'AppElecciones/lugar/crear.html'
    success_message = 'Lugar de interés agregado'
    success_url = reverse_lazy('listado-lugar-interes')
    permission_required = 'AppElecciones.add_lugarinteres'
    raise_exception = True

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        self.object.distrito = organizacion_del_usuario()['instancia']
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar lugar de interés'
        return context


class ActualizarLugarInteres(guardianPermiso, SuccessMessageMixin, UpdateView):
    model = LugarInteres
    form_class = FormLugarInteres
    template_name = 'AppElecciones/lugar/crear.html'
    success_message = 'Lugar de interés actualizado'
    success_url = reverse_lazy('listado-lugar-interes')
    permission_required = 'AppElecciones.change_lugarinteres'
    raise_exception = True
    ccept_global_perms = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar lugar de interés'
        return context


class EliminarLugarInteres(guardianPermiso, SuccessMessageMixin, DeleteView):
    model = LugarInteres
    template_name = 'AppElecciones/lugar/eliminar.html'
    success_url = reverse_lazy('listado-lugar-interes')
    permission_required = 'AppElecciones.delete_lugarinteres'
    raise_exception = True
    ccept_global_perms = True

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        # error_url = self.get_error_url()
        try:
            self.object.delete()
            messages.success(
                self.request, "Lugar de interés eliminado")
            return HttpResponseRedirect(success_url)
        except ProtectedError:
            # print(self.object)
            messages.success(
                self.request, (
                    "Imposible eliminar el lugar de interés"))
            return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar lugar de interés'
        return context


class DetalleLugarInteres(PermisoDesdeDjango, DetailView):
    model = LugarInteres
    template_name = 'AppElecciones/lugar/detalles.html'
    permission_required = 'AppElecciones.view_lugarinteres'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Información del '
        return context