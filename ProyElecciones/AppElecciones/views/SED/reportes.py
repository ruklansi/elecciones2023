from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from guardian.shortcuts import get_objects_for_user

from AppElecciones.Reportes.SED.exportarSED import SEDRecurso
from AppElecciones.models import Sed


def exportarSED(request):
    sed_recurso = SEDRecurso()
    usuario = request.user
    queryset = get_objects_for_user(usuario, 'view_sed', Sed, accept_global_perms=False)
    if queryset:
        control = 1
        nombre_archvivo = 'Sucursal-electoral-digital.xls'
        dataset = sed_recurso.export(queryset)
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
