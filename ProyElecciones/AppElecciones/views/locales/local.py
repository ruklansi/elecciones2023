import json

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Max, Sum, Subquery, OuterRef, Case, When, Value, Count, F
from django.db.models import ProtectedError
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from guardian.mixins import PermissionRequiredMixin as guardianPermisos
from guardian.shortcuts import get_objects_for_user
from model_utils import Choices

from AppElecciones.forms import *
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import ControlDeVotos, HoraControlVoto, EstadosLocal, TransmisionTelegramas, EstadosMesas

class ListadoLocalesValidados(PermisoDesdeDjango, ListView):

    model = Local
    template_name = "AppElecciones/locales/listado_validados.html"
    permission_required = 'AppElecciones.view_local'
    raise_exception = True


    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            seg_int = request.POST['seg_int']
            seg_ext = request.POST['seg_ext']
            mesas = request.POST['mesas']
            estado_local = request.POST['estado_local']
            id_distrito_local = request.POST['id_distrito_local']
            id_subdistrito_local = request.POST['id_subdistrito_local']
            id_seccion_local = request.POST['id_seccion_local']
            id_circuito_local = request.POST['id_circuito_local']
            ORDENAR_COLUMNAS = Choices(('1', 'fecha_creacion'))
            buscar = ['nombre', 'circuito__seccion__distrito__distrito', 'circuito__seccion__subdistrito__subdistrito',
                      'circuito__seccion__seccion', 'circuito__circuito', 'estado__estado', 'estado__causa']
            columnas = (
                'id', 'nombre', 'circuito__seccion__distrito__distrito', 'circuito__seccion__subdistrito__subdistrito',
                'circuito__seccion__seccion', 'circuito__circuito', 'porcentaje', 'estado__estado', 'estado__causa',
                'cant_mesas', 'cant_nov', 'cant_seg_ext', 'cant_seg_int', 'editar', 'eliminar')
            agregados = {'porcentaje': Subquery(ControlDeVotos.objects.filter(local=OuterRef('pk')).values(
                'local__pk').annotate(porcen=Max('cant_votos')).values('porcen')),
                         'cant_mesas': Subquery(MesasEnLocal.objects.filter(local=OuterRef('pk')).values(
                             'local__pk').annotate(cantidad=Count('mesas')).values('cantidad')),
                         'cant_nov': Subquery(NovedadesEnLocal.objects.filter(local=OuterRef('pk')).values(
                             'local__pk').annotate(nov=Count('detalle')).values('nov')),
                         'cant_seg_ext': Subquery(SegExternaLocal.objects.filter(local=OuterRef('pk')).values(
                             'local__pk').annotate(cantsegext=Sum('cant_efectivos')).values('cantsegext')),

                         'cant_seg_int_j': Subquery(SegInternaLocal.objects.filter(local=OuterRef('pk')).values(
                             'local__pk').annotate(j_local=Count('jefe_local')).values('j_local')),
                         'cant_seg_int_a': Coalesce(
                             Subquery(AuxiliarLocal.objects.filter(seg_interna_local__local=OuterRef('pk')).values(
                                 'seg_interna_local__local__pk').annotate(aux=Count('auxiliar')).values('aux')), 0),
                         'cant_seg_int': F('cant_seg_int_a') + F('cant_seg_int_j'),

                         }

            otros_filtros = {'validado': 1}
            if id_distrito_local != '':
                otros_filtros['circuito__seccion__distrito'] = id_distrito_local
            if id_subdistrito_local != '':
                otros_filtros['circuito__seccion__subdistrito'] = id_subdistrito_local
            if id_seccion_local != '':
                otros_filtros['circuito__seccion'] = id_seccion_local
            if id_circuito_local != '':
                otros_filtros['circuito'] = id_circuito_local

            if estado_local != '':
                otros_filtros['estado__estado'] = estado_local
            if mesas != '':
                if mesas == '1':
                    otros_filtros['mesas_en_local__isnull'] = False
                if mesas == '0':
                    otros_filtros['mesas_en_local__isnull'] = True
            if seg_int != '':
                if seg_int == '2':
                    otros_filtros['local_seguridad_interna__isnull'] = False
                if seg_int == '3':
                    otros_filtros['local_seguridad_interna__isnull'] = True
            if seg_ext != '':
                if seg_ext == '4':
                    otros_filtros['local_seguridad_externa__isnull'] = False
                if seg_ext == '5':
                    otros_filtros['local_seguridad_externa__isnull'] = True

            con_permisos = True

            locales_validados = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                     otros_filtros,
                                                     con_permisos, request.POST)
            result = dict()
            result['data'] = locales_validados['items']
            result['draw'] = locales_validados['draw']
            result['recordsTotal'] = locales_validados['total']
            result['recordsFiltered'] = locales_validados['count']
            # print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        # locales = get_objects_for_user(usuario, 'view_local', Local).all()

        # context['mesas'] = locales.annotate(suma=Coalesce(Count('mesas_en_local'),0)).count()

        # context['todos_locales'] = locales.count()
        # context['locales_validados'] = locales.filter(validado=1).count()
        # context['locales_no_validados'] = locales.filter(validado=0).count()
        context['titulo'] = 'Locales validados'
        context['listado_url'] = reverse_lazy('listado-de-locales-validados')
        context['crear_url'] = reverse_lazy('crear-local')
        context['tiene_subdistrito'] = organizacion_del_usuario()['tiene_subdistrito']
        return context


class ListadoLocalesNoValidados(PermisoDesdeDjango, ListView):
    model = Local
    template_name = "AppElecciones/locales/listado_novalidados.html"
    permission_required = 'AppElecciones.ver_locals_no_validados_local'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            id_distrito_local = request.POST['id_distrito_local']
            id_subdistrito_local = request.POST['id_subdistrito_local']
            id_seccion_local = request.POST['id_seccion_local']
            id_circuito_local = request.POST['id_circuito_local']
            ORDENAR_COLUMNAS = Choices(('0', 'fecha_creacion'))
            buscar = ['nombre', 'direccion', 'localidad', 'circuito__seccion__distrito__distrito', 'circuito__circuito',
                      'circuito__seccion__seccion',
                      'circuito__seccion__subdistrito__subdistrito']
            columnas = (
                'id', 'nombre', 'circuito__seccion__distrito__distrito', 'direccion', 'localidad', 'circuito__circuito',
                'circuito__seccion__seccion', 'circuito__seccion__subdistrito__subdistrito', 'editar', 'eliminar')
            agregados = None

            otros_filtros = {'validado': 0}
            if id_distrito_local != '':
                otros_filtros['circuito__seccion__distrito'] = id_distrito_local
            if id_subdistrito_local != '':
                otros_filtros['circuito__seccion__subdistrito'] = id_subdistrito_local
            if id_seccion_local != '':
                otros_filtros['circuito__seccion'] = id_seccion_local
            if id_circuito_local != '':
                otros_filtros['circuito'] = id_circuito_local

            con_permisos = True

            locales_no_validados = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                        otros_filtros,
                                                        con_permisos, request.POST)
            result = dict()
            locales = Local.objects.all()
            result['data'] = locales_no_validados['items']
            result['draw'] = locales_no_validados['draw']
            result['recordsTotal'] = locales_no_validados['total']
            result['recordsFiltered'] = locales_no_validados['count']
            result['locales_no_validados'] = locales.filter(validado=0).count()
            # print(result)
        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Locales sin validar'
        context['listado_url'] = reverse_lazy('listado-de-locales-novalidados')
        context['crear_url'] = reverse_lazy('crear-local')
        context['tiene_subdistrito'] = organizacion_del_usuario()['tiene_subdistrito']
        return context


class CrearLocal(PermisoDesdeDjango, SuccessMessageMixin, CreateView):
    model = Local
    form_class = FormLocal
    template_name = 'AppElecciones/locales/crear.html'
    success_message = 'Local registrado'
    permission_required = 'AppElecciones.add_local'
    raise_exception = True

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        try:
            self.object.estado = EstadosLocal.objects.get(id=1)
        except:
            pass
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.validado:
            # return reverse('seg-votos-otros-datos', kwargs={'pk': self.object.pk})
            return reverse('listado-de-locales-validados')
        else:
            return reverse('listado-de-locales-novalidados')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar local'
        return context


class ActualizarLocal(guardianPermisos, SuccessMessageMixin, UpdateView):
    model = Local
    form_class = FormLocal
    template_name = 'AppElecciones/locales/crear.html'
    success_message = 'Local actualizado'
    permission_required = 'AppElecciones.change_local'
    raise_exception = True
    accept_global_perms = False

    def form_valid(self, form):
        self.object = form.save()
        self.object.validado = 1
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.validado:
            # return reverse('seg-votos-otros-datos', kwargs={'pk': self.object.pk})
            return reverse('listado-de-locales-validados')
        else:
            return reverse('listado-de-locales-novalidados')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar local'
        return context


class EliminarLocal(guardianPermisos, SuccessMessageMixin, DeleteView):
    model = Local
    template_name = 'AppElecciones/locales/eliminar.html'
    success_url = reverse_lazy('listado-de-locales-validados')
    permission_required = 'AppElecciones.delete_local'
    raise_exception = True
    accept_global_perms = False



    def delete(self, request, *args, **kwargs):

        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()
            messages.success(self.request, ('Local "' +
                                            str(self.object) + '" eliminado.'))
            return HttpResponseRedirect(success_url)
        except ProtectedError:
            messages.error(self.request, ("Imposible eliminar el Local " +
                                          str(self.object) + "porque tiene asociado datos de seguridad interna (Jefe "
                                                             "de local y Auxiliares), Seguridad externa, Novedades o "
                                                             "Mesas asignadas. Elimine esos datos primero"))

        return HttpResponseRedirect(success_url)

    def get_success_url(self):


        if self.kwargs['tipo_local'] == '777':

             return reverse('listado-de-locales-novalidados')  # Redireccionar a una URL específica
        
        # # elif condition2:
        #     return reverse('nombre_url2')  # Redireccionar a otra URL específica
        else:

             return super().get_success_url()  # Utilizar la URL de redireccionamiento predeterminada

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar local'
        if self.kwargs['tipo_local'] == '777':
            context['redirigir'] = 'no_validado'
        else:
            context['redirigir'] = 'validado'
        return context


class DetalleLocal(guardianPermisos, DetailView):
    model = Local
    template_name = 'AppElecciones/locales/detalles.html'
    permission_required = 'AppElecciones.view_local'
    raise_exception = True
    accept_global_perms = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = ''
        return context


class DetallesDelLocalAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        # data = []
        if request.POST:
            id = (request.POST['id'])

            # Seguridad interna
            seg_interna = SegInternaLocal.objects.filter(local=id)
            if seg_interna:
                jefe_local = 1
            else:
                jefe_local = 0

            cant_auxiliares = 0
            total_seg_interna = 0
            cant_auxiliares = AuxiliarLocal.objects.filter(seg_interna_local__local=id).count()
            total_seg_interna = cant_auxiliares + jefe_local
            data['seg_interna'] = total_seg_interna

            # Seguridad externa
            # https://riptutorial.com/es/django/example/13050/promedio--minimo--maximo--suma-de-queryset
            seg_externa = SegExternaLocal.objects.filter(
                local=id).aggregate(Sum('cant_efectivos'))
            if not seg_externa['cant_efectivos__sum']:
                seg_externa['cant_efectivos__sum'] = 0
            data['seg_externa'] = seg_externa

            # Novedades
            cant_novedades = NovedadesEnLocal.objects.filter(local=id).count()
            data['cant_novedades'] = cant_novedades

            # Mayor porcentaje de votos en el local-->> Book.objects.all().aggregate(Max('price'))
            porc_votos = ControlDeVotos.objects.filter(
                local=id).aggregate(Max('cant_votos'))
            if porc_votos['cant_votos__max'] == None:
                porc_votos['cant_votos__max'] = 0

            cant_mesas = MesasEnLocal.objects.filter(local=id).count()
            data['cant_mesas'] = cant_mesas

            data['cant_votos'] = porc_votos

        return JsonResponse(data, safe=False)


class FiltraCamposLocalAjax(View):
    """
    Select anidados desde el Distrito, Subdistrito, Sección para obtener el Circuito al crear un Local
    """

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        resultado = dict()
        accion = (request.POST['accion'])

        if accion == 'filtrar-subdistritos-en-local':
            sub = Subdistrito.objects.filter(distrito_id=request.POST['id'])
            if sub:
                data = []
                organizacion = organizacion_del_usuario()['org']
                if organizacion == 'subdistrito':
                    instancia_subdistrito = organizacion_del_usuario()['instancia']
                    sub = Subdistrito.objects.get(id=instancia_subdistrito.id)
                    data.append({'id': sub.id, 'subdistrito': sub.subdistrito})
                else:
                    for s in Subdistrito.objects.filter(distrito_id=request.POST['id']):
                        data.append({'id': s.id, 'subdistrito': s.subdistrito})
                resultado['datos'] = data
                resultado['hay_subdistrito'] = True

            else:
                data = []
                for t in Seccion.objects.filter(distrito_id=request.POST['id']):
                    data.append({'id': t.id, 'seccion': t.seccion})
                resultado['datos'] = data
                resultado['hay_subdistrito'] = False

        if accion == 'filtrar-seccion-en-local':
            data = []
            # aca el id es un subdistrito
            for s in Seccion.objects.filter(subdistrito_id=request.POST['id']):
                data.append({'id': s.id, 'seccion': s.seccion})
            resultado['datos'] = data
            resultado['hay_secciones'] = True

        if accion == 'filtrar-circuito-en-local':
            data = []
            for c in Circuito.objects.filter(seccion_id=request.POST['id']):
                data.append({'id': c.id, 'circuito': c.circuito})
            resultado['datos'] = data
            resultado['hay_circuitos'] = True
        return JsonResponse(resultado, safe=False)


class EntradaAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = []
        accion = (request.POST['accion'])

        if accion == 'cargar-horario-control-voto':
            data = []
            for h in HoraControlVoto.objects.all():
                data.append({'id': h.id, 'hora': h.hora})

        if accion == 'cargar-causa-en-local':
            data = []
            for t in EstadosLocal.objects.all():
                data.append({'id': t.id, 'estado': t.estado, 'causa': t.causa})

        if accion == 'ejecutar_accion':
            tipo_causa_local = (request.POST['tipo_causa_local'])
            lista_id_locales = json.loads(request.POST['lista_id'])
            lista_id = [x['id'] for x in lista_id_locales]
            locales = Local.objects.filter(pk__in=lista_id)

            estado = EstadosLocal.objects.get(id=tipo_causa_local)
            locales.update(estado=estado)

        if accion == 'registrar_votos':
            id_horario_por_votos = (request.POST['horario_por_votos'])
            porcentaje_votos = (request.POST['porcentaje_votos'])
            porcentaje_votos_formateado = float(porcentaje_votos)
            lista_id_locales = json.loads(request.POST['lista_id'])
            lista_id = [x['id'] for x in lista_id_locales]
            horario = HoraControlVoto.objects.get(id=id_horario_por_votos)
            ControlDeVotos.objects.bulk_create([ControlDeVotos(local=Local.objects.get(pk=i), horario=horario,
                                                               cant_votos=porcentaje_votos_formateado)
                                                for i in lista_id], ignore_conflicts=True)

        return JsonResponse(data, safe=False)


class ListadoLocalesEnMapa(PermisoDesdeDjango, ListView):
    model = Local
    template_name = "AppElecciones/locales/listadoenmapa.html"
    permission_required = 'AppElecciones.ver_locals_a_validar_en_mapa_local'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Validar locales desde el mapa'
        usuario = self.request.user
        locales = get_objects_for_user(usuario, 'view_local', Local).all()
        context['todos_locales'] = locales.count()
        context['locales_validados'] = locales.filter(validado=1).count()
        context['locales_no_validados'] = locales.filter(validado=0).count()
        context['tiene_subdistrito'] = organizacion_del_usuario()['tiene_subdistrito']
        return context


class EnviarLocalesPorAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST:
            accion = (request.POST['accion'])

            if accion == 'todos-los-locales':
                id_circuito = (request.POST['id_cir'])
                resultado = dict()
                if id_circuito:
                    # locales_ = get_objects_for_user(usuario, 'view_local', Local).all()
                    locales = Local.objects.filter(circuito=id_circuito)

                    cant_locales_seccion = locales.count()
                    cant_locales_validados = locales.filter(validado=1).count()
                    cant_locales_no_validados = locales.filter(validado=0).count()
                    # datos = json.loads(serialize("geojson", locales))
                    # resultado['datos'] = datos
                    data = []
                    for s in locales:
                        data.append({'id': s.id, 'nombre': s.nombre, 'localidad': s.localidad,
                                     'direccion': s.direccion,
                                     'latitud': s.ubicacion.y,
                                     'longitud': s.ubicacion.x,
                                     'estado': s.get_validado_display(),
                                     'circuito': s.circuito.circuito,
                                     'seccion': s.circuito.seccion.seccion,
                                     'subdistrito': s.circuito.seccion.subdistrito.subdistrito,
                                     'distrito': s.circuito.seccion.distrito.distrito})
                        resultado['hay_datos'] = True
                        resultado['datos'] = data
                        resultado['cant_loc'] = cant_locales_seccion
                        resultado['cant_loc_validados'] = cant_locales_validados
                        resultado['cant_loc_no_validados'] = cant_locales_no_validados
                else:
                    resultado['hay_datos'] = False
        return JsonResponse(resultado, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['titulo'] = 'Novedades en locales'
        # context['listado_url'] = reverse_lazy('listado-de-locales-filtrados')
        context['crear_url'] = reverse_lazy('listado-de-locales-enmapa')
        return context


class ListadoLocalesParaMaterialVotacionyUrnas(PermisoDesdeDjango, ListView):
    model = Local
    template_name = "AppElecciones/locales/listadoparamatelecyurnas.html"
    permission_required = 'AppElecciones.view_local'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":

            estado = request.POST['estado']

            id_distrito = request.POST['id_distrito']
            id_subdistrito = request.POST['id_subdistrito']
            id_seccion = request.POST['id_seccion']
            id_circuito = request.POST['id_circuito']

            ORDENAR_COLUMNAS = Choices(('1', 'fecha_creacion'))
            buscar = ['nombre', 'circuito__seccion__distrito__distrito']
            columnas = (
                'id', 'nombre', 'circuito__circuito', 'circuito__seccion__seccion',
                'recepciono_mat_elec', 'entrego_urna', 'transmitio', 'circuito__seccion__distrito__distrito',
                'circuito__seccion__subdistrito__subdistrito', 'cant_mesas_1', 'transmite_tel_en_local')
            agregados = {'transmitio': Subquery(TransmisionTelegramas.objects.filter(local=OuterRef('pk')).values(
                'local__pk').annotate(
                transmitio=Case(When(transmite_telegrama=True, then=Value('Sí')), default=Value('No'))).values(
                'transmitio')),

                'transmite_tel_en_local': Case(When(transmite_telegrama=True, then=Value('Sí')), default=Value('No')),

                'cant_mesas_1': Subquery(MesasEnLocal.objects.filter(local=OuterRef('pk')).values(
                    'local__pk').annotate(cantidad= Coalesce(Count('mesas'), 0)).values('cantidad')),
            }

            # otros_filtros = {'validado': 1, 'mesas_en_local__isnull': False }
            otros_filtros = {'validado': 1, 'cant_mesas_1__gt': 0 }
            if id_distrito != '':
                otros_filtros['circuito__seccion__distrito'] = id_distrito
            if id_subdistrito != '':
                otros_filtros['circuito__seccion__subdistrito'] = id_subdistrito
            if id_seccion != '':
                otros_filtros['circuito__seccion'] = id_seccion
            if id_circuito != '':
                otros_filtros['circuito'] = id_circuito

            if estado != '':
                if estado == 'recmatele':
                    otros_filtros['recepciono_mat_elec'] = True
                if estado == 'norecmatele':
                    otros_filtros['recepciono_mat_elec'] = False
                if estado == 'entregarurna':
                    otros_filtros['entrego_urna'] = True
                if estado == 'noentregarurna':
                    otros_filtros['entrego_urna'] = False
                if estado == 'transmitiotelegrama':
                    otros_filtros['telegramas_en_local__transmite_telegrama'] = False
                if estado == 'notransmitiotelegrama':
                    otros_filtros['telegramas_en_local__isnull'] = True

            con_permisos = True

            locales_urnas = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                 otros_filtros,
                                                 con_permisos, request.POST)

            result = dict()

            result['data'] = locales_urnas['items']
            result['draw'] = locales_urnas['draw']
            result['recordsTotal'] = locales_urnas['total']
            result['recordsFiltered'] = locales_urnas['count']

        return JsonResponse(result, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Control de urnas - Solo se listan los locales con urnas cargadas'
        context['tiene_subdistrito'] = organizacion_del_usuario()['tiene_subdistrito']
        return context


class EntradaAjaxUrnas(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        global lista_id
        data = []
        accion = request.POST['accion']
        lista_id_ = request.POST.get('lista_id', False)
        if lista_id_:
            lista_id = json.loads(lista_id_)
            locales = Local.objects.filter(pk__in=lista_id)
        if accion == 'transmitiotelegrama':
            # https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create-->>>ignore_conflicts
            TransmisionTelegramas.objects.bulk_create(
                [TransmisionTelegramas(local=Local.objects.get(pk=i), transmite_telegrama=True) for i in lista_id],
                ignore_conflicts=True)
        if accion == 'notransmitiotelegrama':
            locales_que_no_trans = TransmisionTelegramas.objects.filter(local__in=lista_id)
            locales_que_no_trans.delete()
        if accion == 'recmatele':
            locales.update(recepciono_mat_elec=True)
        if accion == 'norecmatele':
            locales.update(recepciono_mat_elec=False)
        if accion == 'entregarurna':
            locales.update(entrego_urna=True)
        if accion == 'noentregarurna':
            locales.update(entrego_urna=False)
            data.append({'accion': 'ok'})
        return JsonResponse(data, safe=False)


class EntradaAjaxMesas(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = []
        accion = (request.POST['accion'])

        if accion == 'cargar-secciones':
            data = []

            # usuario = request.user
            # distrito = get_objects_for_user(usuario, 'view_distrito', Distrito).all()
            distrito = Distrito.objects.all()
            temp = 0
            for i in distrito:
                temp = i.id
                for y in Seccion.objects.filter(distrito__id=temp):
                    # for y in Seccion.objects.all():
                    data.append({'id': y.id, 'seccion': y.seccion})

        if accion == 'filtrar-circuito':

            data = []
            for c in Circuito.objects.filter(seccion_id=request.POST['id']):
                data.append({'id': c.id, 'circuito': c.circuito})

        if accion == 'filtrar-local':
            data = []
            for l in Local.objects.filter(circuito_id=request.POST['id']):
                data.append({'id': l.id, 'nombre_local': l.nombre})

        if accion == 'ejecutar_accion_en_mesas':
            tipo_causa_mesas = (request.POST['tipo_causa_mesas'])
            lista_id_mesas = json.loads(request.POST['lista_id'])
            lista_id = [x['id'] for x in lista_id_mesas]
            mesas = MesasEnLocal.objects.filter(pk__in=lista_id)

            estado = EstadosMesas.objects.get(id=tipo_causa_mesas)
            mesas.update(estado=estado)
            # print(data)

        return JsonResponse(data, safe=False)
