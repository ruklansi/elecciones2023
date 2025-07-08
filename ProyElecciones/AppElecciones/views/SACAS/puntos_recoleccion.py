import json
import os

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, When, Value, Case, F, DateTimeField, OuterRef, Subquery
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.template import loader
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from guardian.shortcuts import remove_perm, GroupObjectPermission, assign_perm
from model_utils import Choices
from xhtml2pdf import pisa

from AppElecciones.forms import FormSACAPuntoRecoleccion
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import SACASPuntosRecoleccion, SACASHistorialPuntosRecoleccion, \
    SACASHistorialCircuitosRecoleccion, SACACircuitoRecoleccion
from ProyElecciones import settings
from guardian.mixins import PermissionRequiredMixin as guardianPermisos

class ListarPuntosRecoleccionSACAS(PermisoDesdeDjango, ListView):
    model = SACASPuntosRecoleccion
    template_name = "AppElecciones/SACAS/puntos_recoleccion/listado.html"
    permission_required = 'AppElecciones.view_sacaspuntosrecoleccion'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            campo = dict(SACASHistorialPuntosRecoleccion._meta.get_field('estado').flatchoices)
            lista = [When(estado_prs__estado=k, then=Value(v)) for k, v in campo.items()]
            estado = Case(*lista)

            ORDENAR_COLUMNAS = Choices(('1', 'fecha_creacion'))
            buscar = ['distrito__distrito']
            columnas = ('id', 'distrito__distrito', 'direccion', 'denominacion_puesto', 'cant_sacas',
                        'estado_prs__fecha', 'estado', 'estado_prs__estado', 'cant_uupp', 'editar','eliminar')

            agregados = {'estado': estado}

            otros_filtros = None
            con_permisos = True
            lista_puntos_recoleccion = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados, columnas,
                                                            otros_filtros, con_permisos, request.POST)
            data = dict()
            data['data'] = lista_puntos_recoleccion['items']
            data['draw'] = lista_puntos_recoleccion['draw']
            data['recordsTotal'] = lista_puntos_recoleccion['total']
            data['recordsFiltered'] = lista_puntos_recoleccion['count']
            # print(data)
            return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Puntos de Reunión de SACAS'
        context['listado_url'] = reverse_lazy('listado-puntos-recoleccion-sacas')
        context['crear_url'] = reverse_lazy('crear-punto-recoleccion-sacas')
        return context


class CrearPuntosRecoleccionSACAS(PermisoDesdeDjango, SuccessMessageMixin, CreateView):
    model = SACASPuntosRecoleccion
    form_class = FormSACAPuntoRecoleccion
    template_name = 'AppElecciones/SACAS/puntos_recoleccion/crear.html'
    success_message = 'Punto creado'
    success_url = reverse_lazy('listado-puntos-recoleccion-sacas')
    permission_required = 'AppElecciones.add_sacaspuntosrecoleccion'
    raise_exception = True

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        self.object.save()
        h_puntos = SACASHistorialPuntosRecoleccion()
        h_puntos.estado = 0
        h_puntos.fecha = now()
        h_puntos.prs = self.object
        h_puntos.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar Punto de Recolección de SACAS'
        return context


class ActualizarPuntoRecoleccionSACAS(guardianPermisos, SuccessMessageMixin, UpdateView):
    model = SACASPuntosRecoleccion
    form_class = FormSACAPuntoRecoleccion
    template_name = 'AppElecciones/SACAS/puntos_recoleccion/crear.html'
    success_message = 'Punto actualizado'
    success_url = reverse_lazy('listado-puntos-recoleccion-sacas')
    permission_required = 'AppElecciones.change_sacaspuntosrecoleccion'
    raise_exception = True
    accept_global_perms = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar punto de recolección de SACAS'
        return context


class EliminarPuntoRecoleccionSACAS(PermisoDesdeDjango, SuccessMessageMixin, DeleteView):
    model = SACASPuntosRecoleccion
    template_name = 'AppElecciones/SACAS/puntos_recoleccion/eliminar.html'
    success_url = reverse_lazy('listado-puntos-recoleccion-sacas')
    permission_required = 'AppElecciones.delete_sacaspuntosrecoleccion'
    raise_exception = True

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            SACASHistorialPuntosRecoleccion.objects.filter(prs=self.object).delete()
            self.object.delete()
            messages.success(self.request, "Punto eliminado")
            return HttpResponseRedirect(success_url)
        except ProtectedError:
            # print(self.object)
            messages.error(
                self.request, "Imposible eliminar el Punto")
        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Punto de Recolección de SACAS'
        return context


class PuntosRecoleccionPDF(View):
    def link_callback(self, uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        # use short variable names
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /static/media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri  # handle absolute uri (ie: http://some.tld/foo.png)

        # make sure that file exists
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
        return path

    def get(self, request, *args, **kwargs):
        lista_de_prs = json.loads(request.GET['lista_id'])
        campo = dict(SACASHistorialPuntosRecoleccion._meta.get_field('estado').flatchoices)
        lista = [When(estado=k, then=Value(v)) for k, v in campo.items()]
        estados = SACASHistorialPuntosRecoleccion.objects.filter(prs=OuterRef('pk')).order_by('-fecha').annotate(
            estado_u=Case(*lista))

        lista_prs_a_imprimir = SACASPuntosRecoleccion.objects.filter(pk__in=lista_de_prs).annotate(estado=
                                                                                                   Subquery(
                                                                                                       estados.values(
                                                                                                           'estado_u')[
                                                                                                       :1])).annotate(
            fecha=
            Case(
                When(estado_prs__isnull=False,
                     then=F('estado_prs__fecha')),
                output_field=DateTimeField())
        )

        if organizacion_del_usuario()['org'] == 'distrito':
            distrito_ = organizacion_del_usuario()['instancia']
        template = loader.get_template('AppElecciones/SACAS/puntos_recoleccion/listado-pdf.html')
        context = {
            'lista_prs_a_imprimir': lista_prs_a_imprimir,
            'distrito': distrito_,
            'logo': '{}{}'.format(settings.STATIC_URL, 'coffaa/logo.png'),
        }

        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')

        # Si lo activamos se descarga el archivo
        # response['Content-Disposition'] = 'attachment; filename="Novedades-generales.pdf"'

        pisa_status = pisa.CreatePDF(
            html,
            dest=response,
            link_callback=self.link_callback
        )
        if pisa_status.err:
            return HttpResponse('Tenemos algunos errores <pre>' + html + '</pre>')

        return response


class CambiarEstadoPuntorRecoleccionSACAS(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = dict()
        id_prs = (request.POST['id_prs'])
        historial = SACASHistorialPuntosRecoleccion.objects.get(prs=id_prs)
        if historial.estado == 0:
            historial.fecha = now()
            historial.estado = 1
            ins=SACASPuntosRecoleccion.objects.get(id=id_prs)
            #GroupObjectPermission.objects.filter(object_pk=id_prs, content_type=ContentType.objects.get_for_model(SACASPuntosRecoleccion)).delete()
            remove_perm('change_sacaspuntosrecoleccion',ins.distrito.grupo,ins)

            historial.save()
            h_circuito = SACASHistorialCircuitosRecoleccion()
            h_circuito.estado = 0
            h_circuito.fecha = now()
            # print(id_prs)
            # h_circuito.crs =SACACircuitoRecoleccion.objects.filter(circuito__punto=id_prs).last()
            h_circuito.crs = SACACircuitoRecoleccion.objects.filter(prs=id_prs).first()
            circuito=SACACircuitoRecoleccion.objects.filter(prs=id_prs).first()
            remove_perm('change_sacacircuitorecoleccion', circuito.distrito.grupo, circuito)
            # print(h_circuito.crs)
            h_circuito.save()
        data['cambio_estado'] = True
        return JsonResponse(data, safe=False)
