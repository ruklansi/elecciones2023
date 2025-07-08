import mimetypes
import datetime
from math import pi
import pandas as pd

from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.palettes import Bright6, Category20c
from bokeh.plotting import figure
from bokeh.transform import cumsum
from django.contrib import messages
from django.db.models import ProtectedError, Case, When, Value, Func, F, CharField
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from model_utils import Choices
from pytz import timezone

from AppAdministracion.Reportes.Usuarios.exportarUsuarios import UsuarioRecurso
from AppAdministracion.forms import UsuarioForm
from AppAdministracion.listadoParaDatatebles import listarParaDatatables
from AppAdministracion.models import Usuario, ManualLectorCGE, Estado, ManualPersonalCGE, ManualDistrito, \
    ManualLogisticaCGE, ManualSubdistrito, ManualTableros
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango

# from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango


class ListadoUsuarios(PermisoDesdeDjango, ListView):
    # es_admin_django = True
    model = Usuario
    template_name = "AppAdministracion/usuarios/listado.html"
    permission_required = 'AppAdministracion.view_usuario'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            ORDENAR_COLUMNAS = Choices(('0', 'fecha_registro_usuario'), ('1', 'username'), ('2', 'first_name'),
                                       ('3', 'last_name'), )
            buscar = ['username', 'first_name', 'last_name', 'rol', 'dni', 'nro_tel', 'fecha_reseteo', 'grupo_organizacion__name']
            columnas = ('id', 'first_name', 'last_name', 'is_superuser', 'username', 'dni', 'nro_tel', 'rol', 'email',
                        'fecha_reseteo', 'tipo_reset', 'last_login', 'grupo_organizacion__name')
            agregados = {
                'tipo_reset': Case(When(tipo_reseteo=1, then=Value('Por admin')), When(tipo_reseteo=2, then=Value('Usuario')), default=Value('No reseteado'))}
            otros_filtros = {'is_staff':  False}
            con_permisos = False
            usuarios = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas, otros_filtros,
                                            con_permisos, request.POST)
            resultado = dict()
            resultado['data'] = usuarios['items']
            resultado['draw'] = usuarios['draw']
            resultado['recordsTotal'] = usuarios['total']
            resultado['recordsFiltered'] = usuarios['count']
            # resultado['puede_chang_y_del_user'] = get_current_user().has_perm(
            #     'appLogin.delete_usuario') and get_current_user().has_perm('appLogin.change_usuario')
        return JsonResponse(resultado, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de usuarios'
        context['crear_url'] = reverse_lazy('crear-usuario')
        # a = 'prueba'
        # print(a / 10)
        return context


class CrearUsuario(PermisoDesdeDjango, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'AppAdministracion/usuarios/crear.html'
    success_message = 'Usuario agregado'
    permission_required = 'AppAdministracion.add_usuario'
    raise_exception = True

    def get_success_url(self):
        return reverse('listado-de-usuarios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar Usuario'
        return context


class ActualizarUsuario(PermisoDesdeDjango, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'AppAdministracion/usuarios/crear.html'
    success_message = 'Usuario actualizado'
    permission_required = 'AppAdministracion.change_usuario'
    raise_exception = True


    def form_valid(self, form):
        # form.save(commit=False)
        # form.save_m2m()
        return super(ActualizarUsuario, self).form_valid(form)

    def get_success_url(self):
        return reverse('listado-de-usuarios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar Usuario'
        return context


class EliminarUsuario(PermisoDesdeDjango, DeleteView):
    model = Usuario
    permission_required = ('AppAdministracion.delete_usuario',)
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = dict()
        if request.is_ajax():
            instancia = get_object_or_404(Usuario, pk=kwargs['pk'])
            if request.method == 'GET':
                if request.is_ajax():
                    try:
                        instancia.delete()
                        data['borrado'] = True
                        data['mensaje'] = 'Usuario eliminado'
                    except (ProtectedError):
                        data[
                            'mierror'] = 'No se puede eliminar porque esta asignado a una organización del CGE'
                        data['borrado'] = False
            return JsonResponse(data)
        messages.error(request, 'No tiene permisos para llevar a cabo esa acción')
        return redirect('inicio')


class UsuariosTiempoReal(TemplateView):
    template_name = 'AppAdministracion/usuarios/listadousertiemporeal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fecha_y_hora_actuales = datetime.datetime.now()
        zona_horaria = timezone('America/Argentina/Buenos_Aires')
        fecha_y_hora_bs_as = fecha_y_hora_actuales.astimezone(zona_horaria)
        fecha = fecha_y_hora_bs_as.strftime('%d/%m/%Y %H:%M')

        usuarios = Estado.objects.filter(user__is_staff=False).annotate(
            datos_user=Func(F('user__first_name'), Value(' '),
                            F('user__last_name'), Value('  DNI:  '),
                            F('user__dni'), Value(' Nro tel: '),
                            F('user__nro_tel'), Value('  Organizacion:  '),
                            F('user__grupo_organizacion__name'), Value('  Inicio sesion:  ' + str(fecha)),
                            function='CONCAT')
        )
        # https://docs.bokeh.org/en/2.4.3/docs/gallery/pie_chart.html
        # https://docs.bokeh.org/en/3.1.0/docs/user_guide/topics/pie.html  # wedge
        cant_usuarios = Usuario.objects.filter(is_staff=False).count()
        cant_usuarios_log = Estado.objects.all().count()
        off_line = cant_usuarios - cant_usuarios_log
        porcentaje_en_linea = cant_usuarios_log * 100 / cant_usuarios
        x = {
            'Off-line': off_line,
            'On-line': cant_usuarios_log,
        }

        data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'usuarios'})
        data['angle'] = data['value'] / data['value'].sum() * 2 * pi
        # data['color'] = Category20c[len(x)]
        data['color'] = ('#ff5050', '#33cc33',)

        f = figure(height=300, width=300, title="Usuarios en línena", toolbar_location=None,
                   tools="hover", tooltips="@usuarios: @value", x_range=(-0.5, 1.0))

        f.wedge(x=0, y=1, radius=0.4,
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                line_color="white", fill_color='color', legend_field='usuarios', source=data)

        f.axis.axis_label = None
        f.axis.visible = False
        f.grid.grid_line_color = None
        script, div = components(f)

        context['script'] = script
        context['div'] = div
        context['cant_usuarios'] = cant_usuarios
        context['cant_usuarios_log'] = cant_usuarios_log
        context['cant_usuarios_nolog'] = off_line
        context['porcentaje_en_linea'] = porcentaje_en_linea
        context['titulo'] = 'Reporte de usuarios en tiempo real'
        context['usuarios'] = list(usuarios.values('datos_user', 'id'))
        return context


# ###Las dos líneas son ayuda para manejar archivos
# https://djangoadventures.com/how-to-create-file-download-links-in-django/
# https://docs.python.org/2/tutorial/inputoutput.html#reading-and-writing-files---> porque usar 'rb' en open() ###
# -->>Usar funciones para decoradores para dar permisos:
# https://stackoverflow.com/questions/51308060/possible-to-use-mixins-in-function-based-views

def exportarUsuarios(request):
    usuario_recurso = UsuarioRecurso()
    lista_rol = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    queryset = Usuario.objects.filter(is_staff=False, rol__in=lista_rol)
    if queryset:
        dataset = usuario_recurso.export(queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Listado-de-usuarios.xls"'
        return response
    messages.warning(request, "No hay registros para exportar")
    return redirect("reportes")


def DescargarManualLectorCGE(request):
    manual = ManualLectorCGE.objects.first()
    try:
        path_to_file = manual.manual.path
    except:
        messages.warning(request, 'El manual para el usuario Lector del CGE se encuentra en elaboración, será cargado oportunamente.')
        return redirect('inicio')
    mime_type, _ = mimetypes.guess_type(path_to_file)
    path = open(path_to_file, 'rb')
    response = FileResponse(path)
    return response

def DescargarManualPersonalCGE(request):
    manual = ManualPersonalCGE.objects.first()
    try:
        path_to_file = manual.manual.path
    except:
        messages.warning(request, 'El manual para el usuario del área de Personal del CGE se encuentra en elaboración, será cargado oportunamente.')
        return redirect('inicio')
    mime_type, _ = mimetypes.guess_type(path_to_file)
    path = open(path_to_file, 'rb')
    response = FileResponse(path)
    return response

def DescargarManualLogisticaCGE(request):
    manual = ManualLogisticaCGE.objects.first()
    try:
        path_to_file = manual.manual.path
    except:
        messages.warning(request, 'El manual para el usuario del área de Material del CGE se encuentra en elaboración, será cargado oportunamente.')
        return redirect('inicio')
    mime_type, _ = mimetypes.guess_type(path_to_file)
    path = open(path_to_file, 'rb')
    response = FileResponse(path)
    return response

def DescargarManualDistrito(request):
    manual = ManualDistrito.objects.first()
    try:
        path_to_file = manual.manual.path
    except:
        messages.warning(request, 'El manual para el usuario del Distrito Electoral se encuentra en elaboración, será cargado oportunamente.')
        return redirect('inicio')
    mime_type, _ = mimetypes.guess_type(path_to_file)
    path = open(path_to_file, 'rb')
    response = FileResponse(path)
    return response

def DescargarManualSubdistrito(request):
    manual = ManualSubdistrito.objects.first()
    try:
        path_to_file = manual.manual.path
    except:
        messages.warning(request, 'El manual para el usuario del Subdistrito Electoral se encuentra en elaboración, será cargado oportunamente.')
        return redirect('inicio')
    mime_type, _ = mimetypes.guess_type(path_to_file)
    path = open(path_to_file, 'rb')
    response = FileResponse(path)
    return response

def DescargarManualTableros(request):
    manual = ManualTableros.objects.first()
    try:
        path_to_file = manual.manual.path
    except:
        messages.warning(request, 'El manual del Tablero de Visualización se encuentra en elaboración, será cargado oportunamente.')
        return redirect('inicio')
    mime_type, _ = mimetypes.guess_type(path_to_file)
    path = open(path_to_file, 'rb')
    response = FileResponse(path)
    return response