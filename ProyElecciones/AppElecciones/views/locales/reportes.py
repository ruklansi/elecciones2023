import json
import os

from crum import get_current_user
from django.contrib import messages
from django.db.models import Q, Case, When, CharField, Value
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.loader import get_template, render_to_string
from django.views import View
from guardian.shortcuts import get_objects_for_user
from xhtml2pdf import pisa

from AppElecciones.Reportes.Locales.exportarLocales import LocalesResource
from AppElecciones.Reportes.Novedades.exportarNovedadesEnLocales import NovedadesEnLocalesRecurso
from AppElecciones.Reportes.Vehiculos.exportarVehiculosPropios import VehPropiosResource
from AppElecciones.models import Local, NovedadesEnLocal, VehiculosPropios, exportarlocales
from ProyElecciones import settings

def reporteLocales(request):
    recurso = LocalesResource()
    usuario = get_current_user()
    local_permiso = get_objects_for_user(usuario, 'view_local', Local, accept_global_perms=False)
    queryset = exportarlocales.objects.filter(id__in=local_permiso)
    if queryset:
        control = 1
        nombre_archvivo = 'Locales.xls'
        dataset = recurso.export(queryset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="archivo.xlsx"'
        response['X-control'] = control
        response['X-nombre-archivo'] = nombre_archvivo
        return response
    else:
        control = 0
        response =  HttpResponse()
        # Agregar los parámetros como encabezados
        response['X-control'] = control
        return response

def exportarNovedadEnLocal(request):
    nov_en_local_recurso = NovedadesEnLocalesRecurso()
    usuario = get_current_user()
    queryset = get_objects_for_user(usuario, 'view_novedadesenlocal', NovedadesEnLocal, accept_global_perms=False)
    if queryset:
        control = 1
        nombre_archvivo = 'Novedad-en-locales.xls'
        dataset = nov_en_local_recurso.export(queryset)
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

class NovedadesEnLocalesPdf(View):
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
        id_local = kwargs['pk']
        lista_id_novedades = json.loads(request.GET['lista_id'])

        lista = []
        for d in lista_id_novedades:
            lista.append(d['id'])
        # usuario = request.user
        # filtro_local = get_objects_for_user(usuario, 'view_local', Local).all()
        # local = filtro_local.filter(id=id_local)


        # filtro_novedades = get_objects_for_user(
        #     usuario, 'view_novedadesenlocal', NovedadesEnLocal).all()
        filtro_novedades = NovedadesEnLocal.objects.all()
        nov_en_local = filtro_novedades.filter(Q(local=id_local) & Q(id__in=lista))

        template = get_template(
            'AppElecciones/locales/novedades/pdf.html')
        context = {
            'nov_en_local': nov_en_local,
            'logo': '{}{}'.format(settings.STATIC_URL, 'coffaa/logo.png'),
        }

        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')

        # Si lo activamos se descarga el archivo
        # response['Content-Disposition'] = 'attachment; filename="novedades.pdf"'

        pisa_status = pisa.CreatePDF(
            html, dest=response,
            link_callback=self.link_callback
        )
        if pisa_status.err:
            return HttpResponse('Tenemos algunos errores <pre>' + html + '</pre>')
        return response

class TodasNovedadesEnLocalesPdf(View):
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
        todas_novedades = get_objects_for_user(usuario, 'view_novedadesenlocal', NovedadesEnLocal, accept_global_perms=False).order_by(
            '-fecha_creacion')
        if todas_novedades:
            template = get_template(
                'AppElecciones/locales/novedades/todas_novedades_pdf.html')
            context = {
                'todas_nov_en_locales': todas_novedades,
                'logo': '{}{}'.format(settings.STATIC_URL, 'coffaa/logo.png'),
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')

            # Si lo activamos se descarga el archivo
            # response['Content-Disposition'] = 'attachment; filename="novedades.pdf"'

            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback
            )
            if pisa_status.err:
                return HttpResponse('Tenemos algunos errores <pre>' + html + '</pre>')
            return response
        messages.warning(request, "No hay registros para exportar")
        return redirect("reportes")
