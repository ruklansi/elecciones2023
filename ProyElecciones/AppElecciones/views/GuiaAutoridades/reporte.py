from crum import get_current_user
from django.http import HttpResponse
from django.shortcuts import redirect
from guardian.shortcuts import get_objects_for_user

from AppElecciones.Reportes.Guia_autoridades.exportar_guia import GuiaRecurso
from AppElecciones.models import GuiaAutoridades
from django.contrib import messages

def exportarGuia(request):
    guia_recurso = GuiaRecurso()
    usuario = get_current_user()
    queryset = get_objects_for_user(usuario, 'view_guiaautoridades', GuiaAutoridades, accept_global_perms=False).order_by('org_texto')
    if queryset:
        control = 1
        nombre_archvivo = 'Guia-de-autoridades.xls'
        dataset = guia_recurso.export(queryset)
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