import json
import os

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as PermisoDesdeDjango
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, When, Value, Case, Subquery, OuterRef, F, DateTimeField
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.template import loader
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from model_utils import Choices
from xhtml2pdf import pisa

from AppElecciones.forms import FormSACACircuitoRecoleccion
from AppElecciones.funciones_comunes import organizacion_del_usuario
from AppElecciones.listadoParaDatatebles import listarParaDatatables
from AppElecciones.models import SACACircuitoRecoleccion, SACASHistorialCircuitosRecoleccion, Circuito_Punto
from ProyElecciones import settings
from guardian.mixins import PermissionRequiredMixin as guardianPermisos


class ListarCircuitosRecoleccionSACAS(PermisoDesdeDjango, ListView):
    model = SACACircuitoRecoleccion
    template_name = "AppElecciones/SACAS/circuitos_recoleccion/listado.html"
    permission_required = 'AppElecciones.view_sacacircuitorecoleccion'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            campo = dict(SACASHistorialCircuitosRecoleccion._meta.get_field('estado').flatchoices)
            lista = [When(estado=k, then=Value(v)) for k, v in campo.items()]
            estados = SACASHistorialCircuitosRecoleccion.objects.filter(crs=OuterRef('pk')).order_by('-fecha').annotate(
                estado_u=Case(*lista))

            ORDENAR_COLUMNAS = Choices(('1', 'fecha_creacion'))
            buscar = ['distrito__distrito']
            columnas = ('id', 'distrito__distrito', 'ctrs', 'cant_personal', 'vehiculo', 'estado', 'id_estado',
                        'editar','eliminar')
            agregados = {'estado': Subquery(estados.values('estado_u')[:1]),
                         'id_estado': Subquery(estados.values('estado')[:1])}

            otros_filtros = None
            con_permisos = True
            lista_circuitos_recoleccion = listarParaDatatables(self.model, ORDENAR_COLUMNAS, buscar, agregados,
                                                               columnas,
                                                               otros_filtros, con_permisos, request.POST)
            data = dict()
            data['data'] = lista_circuitos_recoleccion['items']
            data['draw'] = lista_circuitos_recoleccion['draw']
            data['recordsTotal'] = lista_circuitos_recoleccion['total']
            data['recordsFiltered'] = lista_circuitos_recoleccion['count']
            # print(data)
            return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Circuitos de Recolección de SACAS'
        context['listado_url'] = reverse_lazy('listado-circuitos-recoleccion-sacas')
        context['crear_url'] = reverse_lazy('crear-circuitos-recoleccion-sacas')
        return context


class CrearCircuitoRecoleccionSACAS(PermisoDesdeDjango, SuccessMessageMixin, CreateView):
    model = SACACircuitoRecoleccion
    form_class = FormSACACircuitoRecoleccion
    template_name = 'AppElecciones/SACAS/circuitos_recoleccion/crear.html'
    success_message = 'Circuito creado'
    success_url = reverse_lazy('listado-circuitos-recoleccion-sacas')
    permission_required = 'AppElecciones.add_sacacircuitorecoleccion'
    raise_exception = True


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar Circuito de Recolección de SACAS'
        return context


class ActualizarCircuitoRecoleccionSACAS(guardianPermisos, SuccessMessageMixin, UpdateView):
    model = SACACircuitoRecoleccion
    form_class = FormSACACircuitoRecoleccion
    template_name = 'AppElecciones/SACAS/circuitos_recoleccion/crear.html'
    success_message = 'Circuito actualizado'
    success_url = reverse_lazy('listado-circuitos-recoleccion-sacas')
    permission_required = 'AppElecciones.change_sacacircuitorecoleccion'
    raise_exception = True
    accept_global_perms = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Actualizar Circuito de recolección de SACAS'
        return context


class EliminarCircuitoRecoleccionSACAS(PermisoDesdeDjango, SuccessMessageMixin, DeleteView):
    model = SACACircuitoRecoleccion
    template_name = 'AppElecciones/SACAS/circuitos_recoleccion/eliminar.html'
    success_url = reverse_lazy('listado-circuitos-recoleccion-sacas')
    permission_required = 'AppElecciones.delete_sacacircuitorecoleccion'
    raise_exception = True

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            SACASHistorialCircuitosRecoleccion.objects.filter(crs=self.object).delete()
            self.object.delete()
            messages.success(self.request, "Circuito eliminado")
            return HttpResponseRedirect(success_url)
        except ProtectedError:
            # print(self.object)
            messages.error(
                self.request, "Imposible eliminar el Circuito")
        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Circuito de Recolección de SACAS'
        return context


class CircuitosRecoleccionPDF(View):
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
        lista_de_crs = json.loads(request.GET['lista_id'])
        # usuario = request.user
        # filtro_prs = get_objects_for_user(
        #     usuario, 'view_sacapuntosreunion', SACASPuntosRecoleccion).all()
        # lista_prs_a_imprimir = filtro_prs.filter(pk__in=lista_de_prs)
        campo = dict(SACASHistorialCircuitosRecoleccion._meta.get_field('estado').flatchoices)
        lista = [When(estado=k, then=Value(v)) for k, v in campo.items()]
        estados = SACASHistorialCircuitosRecoleccion.objects.filter(crs=OuterRef('pk')).order_by('-fecha').annotate(
            estado_u=Case(*lista))

        lista_crs_a_imprimir = SACACircuitoRecoleccion.objects.filter(pk__in=lista_de_crs)
        lista_crs_a_imprimir = lista_crs_a_imprimir.annotate(estado=
                                                             Subquery(estados.values('estado_u')[:1])).annotate(fecha=
        Case(
            When(estado_crs__isnull=False,
                 then=F('estado_crs__fecha')),
            output_field=DateTimeField())
        )
        if organizacion_del_usuario()['org'] == 'distrito':
            distrito_ = organizacion_del_usuario()['instancia']
        template = loader.get_template('AppElecciones/SACAS/circuitos_recoleccion/listado-pdf.html')
        context = {
            'lista_crs_a_imprimir': lista_crs_a_imprimir,
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


class CambiarEstadoCircuitoRecoleccionSACAS(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        data = dict()

        id_crs = (request.POST['id_crs'])
        crs = SACACircuitoRecoleccion.objects.get(id=id_crs)
        h_crs = SACASHistorialCircuitosRecoleccion.objects.filter(crs=id_crs).last()
        if h_crs:
            if h_crs.estado == 0:
                h_estado = SACASHistorialCircuitosRecoleccion()
                h_estado.fecha = now()
                h_estado.estado = 1
                h_estado.crs = crs
                h_estado.save()

            if h_crs.estado == 1:
                h_estado = SACASHistorialCircuitosRecoleccion()
                h_estado.fecha = now()
                h_estado.estado = 2
                h_estado.crs = crs
                h_estado.save()

            if h_crs.estado == 2:
                h_estado = SACASHistorialCircuitosRecoleccion()
                h_estado.fecha = now()
                h_estado.estado = 3
                h_estado.crs = crs
                h_estado.save()

        data['cambio_estado'] = True
        return JsonResponse(data, safe=False)


class MostrarHijosCircutoRecoleccionSACAS(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = []
        id_ctrs = (request.POST['id_ctrs'])
        ctrs = SACACircuitoRecoleccion.objects.get(id=id_ctrs)
        if ctrs:
            prs = [c_p.punto for c_p in Circuito_Punto.objects.filter(circuito=ctrs)]
            for p in prs:
                data.append({'direccion': p.direccion,
                             'puesto': p.denominacion_puesto,
                             'fecha': p.estado_prs.all().first().fecha,
                             'estado': p.estado_prs.all().first().get_estado_display(),
                             'cant_sacas': p.cant_sacas})
            return JsonResponse(data, safe=False)
