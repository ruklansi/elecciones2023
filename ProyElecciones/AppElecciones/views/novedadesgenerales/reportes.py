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

from AppElecciones.Reportes.Novedades.exportarNovedadesGenerales import NovedadesGeneralesRecurso
from AppElecciones.models import NovedadesGenerales
from ProyElecciones import settings


def exportarNovedadesGenerales(request):
    nov_grl_recurso = NovedadesGeneralesRecurso()
    usuario = request.user
    queryset = get_objects_for_user(usuario, 'view_novedadesgenerales', NovedadesGenerales, accept_global_perms=False)
    if queryset:
        control = 1
        nombre_archvivo = 'Novedades-generales.xls'
        dataset = nov_grl_recurso.export(queryset)
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

class NovedadesGeneralesPdf(View):
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
        lista_id_nov_grl = json.loads(request.GET['lista_id'])
        usuario = get_current_user()
        queryset = get_objects_for_user(usuario, 'view_novedadesgenerales', NovedadesGenerales, accept_global_perms=False)
        lista_id = []
        for d in lista_id_nov_grl:
            lista_id.append(d['id'])
        nov_generales = queryset.filter(id__in=lista_id)
        template = loader.get_template(
            'AppElecciones/novedadesgenerales/nov-generales-pdf.html')
        context = {
            'lista_nov_generales': nov_generales,
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

class TodasNovedadesGeneralesPdf(View):
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
        todas_nov_generales = get_objects_for_user(usuario, 'view_novedadesgenerales', NovedadesGenerales, accept_global_perms=False).order_by('-fecha_creacion')
        if todas_nov_generales:
            template = loader.get_template(
                'AppElecciones/novedadesgenerales/todas-nov-generales-pdf.html')
            context = {
                'lista_todas_nov_generales': todas_nov_generales,
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