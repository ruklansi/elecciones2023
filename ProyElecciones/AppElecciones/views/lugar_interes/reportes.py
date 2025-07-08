from django.contrib import messages
from django.db.models import Case, When, Sum
from django.db.models import Value
from django.http import HttpResponse
from django.shortcuts import redirect
from guardian.shortcuts import get_objects_for_user

from AppElecciones.Reportes.Lugares_interes.lugares import LugarRecurso
from AppElecciones.models import LugarInteres


def exportarLugar(request):
    led_recurso = LugarRecurso()
    usuario = request.user
    queryset = get_objects_for_user(usuario, 'view_lugarinteres', LugarInteres, accept_global_perms=False)
    if queryset:
        control = 1
        nombre_archvivo = 'Lugar-de-interes.xls'
        dataset = led_recurso.export(queryset)
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