import json
import os

from crum import get_current_user
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views import View
from guardian.shortcuts import get_objects_for_user
from xhtml2pdf import pisa

from AppElecciones.Reportes.Movimientos.exportarMovimientos import MovimientosRecurso
from AppElecciones.models import Movimientos
from ProyElecciones import settings


def exportarMovimientos(request):
    movimiento_recurso = MovimientosRecurso()
    usuario = request.user
    queryset = get_objects_for_user(usuario, 'view_movimientos', Movimientos, accept_global_perms=False)
    if queryset:
        control = 1
        nombre_archvivo = 'Movimientos.xls'
        dataset = movimiento_recurso.export(queryset)
        response = HttpResponse(dataset.xls,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="archivo.xlsx"'
        response['X-control'] = control
        response['X-nombre-archivo'] = nombre_archvivo
        return response
    else:
        control = 0
        response = HttpResponse()
        # Agregar los parámetros como encabezados
        response['X-control'] = control
        return response

class MovimientosPdf(View):
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
        lista_id_movimientos = json.loads(request.GET['lista_id'])
        usuario = get_current_user()
        queryset = get_objects_for_user(usuario, 'view_movimientos', Movimientos, accept_global_perms=False)
        lista_id = []
        for d in lista_id_movimientos:
            lista_id.append(d['id'])
        movimientos = queryset.filter(id__in=lista_id)
        template = loader.get_template(
            'AppElecciones/movimientos/movimientos-pdf.html')
        context = {
            'lista_movimientos': movimientos,
            'logo': '{}{}'.format(settings.STATIC_URL, 'coffaa/logo.png'),
        }

        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')

        # Si lo activamos se descarga el archivo
        # response['Content-Disposition'] = 'attachment; filename="Movimientos.pdf"'

        pisa_status = pisa.CreatePDF(
            html,
            dest=response,
            link_callback=self.link_callback
        )
        if pisa_status.err:
            return HttpResponse('Tenemos algunos errores <pre>' + html + '</pre>')
        return response

class TodosMovimientosPdf(View):
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

        usuario = get_current_user()
        todos_movimientos = get_objects_for_user(usuario, 'view_movimientos', Movimientos, accept_global_perms=False)
        if todos_movimientos:
            template = loader.get_template(
                'AppElecciones/movimientos/todos-movimientos-pdf.html')
            context = {
                'lista_todos_movimientos': todos_movimientos,
                'logo': '{}{}'.format(settings.STATIC_URL, 'coffaa/logo.png'),
            }

            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')

            # Si lo activamos se descarga el archivo
            # response['Content-Disposition'] = 'attachment; filename="Movimientos.pdf"'

            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback
            )
            if pisa_status.err:
                return HttpResponse('Tenemos algunos errores <pre>' + html + '</pre>')
            return response

        messages.warning(request, "No hay registros para exportar")
        return redirect("reportes")