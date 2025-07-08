from django.contrib import messages
from django.db.models import Case, When, Sum, F
from django.db.models import Value
from django.http import HttpResponse
from django.shortcuts import redirect
from guardian.shortcuts import get_objects_for_user

from AppElecciones.Reportes.LED.exportarLED import LEDRecurso
from AppElecciones.models import Led


def exportarLED(request):
    led_recurso = LEDRecurso()
    usuario = request.user
    queryset = get_objects_for_user(usuario, 'view_led', Led, accept_global_perms=False).annotate(fuerza_seg=F('led_seg_ffseg__cant_personal'),
                                                                                                  fecha_ini_seg=F('led_seg_ffseg__fecha_inicio'),
                                                                                                  fecha_fin_seg = F('led_seg_ffseg__fecha_fin'),
                                                                                                  fuerza_armada=F('led_seg_ffaa__cant_personal'),
                                                                                                  fecha_ini_seg_fa = F('led_seg_ffaa__fecha_inicio'),
                                                                                                  fecha_fin_seg_fa = F('led_seg_ffaa__fecha_fin'),
                                                                                                  )


    # queryset = get_objects_for_user(usuario, 'view_led', Led, accept_global_perms=False).annotate(cant_seg_ffaa=Case(
    #     When(led_seg_ffaa__isnull=False,
    #          then=F('led_seg_ffaa__cant_personal')),
    #     default=Value(0)),fecha_inicio=Case(When(led_seg_ffaa__isnull=False,then='led_seg_ffseg__fecha_inicio'),
    #                                         When(led_seg_ffseg__isnull=False,then=F('led_seg_ffaa__fecha_inicio')),defaul=None
    #
    #                                         ), fecha_fin=Case(When(led_seg_ffaa__isnull=False,then='led_seg_ffseg__fecha_fin'),
    #                                                           When(led_seg_ffseg__isnull=False,then=F('led_seg_ffaa__fecha_fin')), defaul=None
    #
    #                                                           )
    #
    #
    #
    # ).annotate(cant_seg_ffseg=Case(
    #     When(led_seg_ffseg__isnull=False,
    #          then=F('led_seg_ffseg__cant_personal')),
    #     default=Value(0)))
    if queryset:
        control = 1
        nombre_archvivo = 'Lugar-escrutinio-definitivo.xls'
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