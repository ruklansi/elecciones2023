import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import user_logged_in, user_logged_out
from django.db.models import Value, F, CharField, Func
from django.db.models.signals import post_save
from django.dispatch import receiver
from pytz import timezone

from AppAdministracion.models import Estado, Usuario
from AppElecciones.models import NovedadesGenerales


@receiver(user_logged_in)
def inicio(sender, **kwargs):
    estado,creado=Estado.objects.get_or_create(user=kwargs.get('user'))
    fecha_y_hora_actuales = datetime.datetime.now()
    zona_horaria = timezone('America/Argentina/Buenos_Aires')
    fecha_y_hora_bs_as = fecha_y_hora_actuales.astimezone(zona_horaria)
    fecha = fecha_y_hora_bs_as.strftime('%d/%m/%Y %H:%M')

    usuario = Usuario.objects.filter(id=kwargs.get('user').id).annotate(
        datos_user=Func(F('first_name'), Value(' '),
                        F('last_name'), Value('  DNI:  '),
                        F('dni'), Value('  Nro tel:  '),
                        F('nro_tel'), Value('  Organizacion:  '),
                        F('grupo_organizacion__name'), Value('  Inicio sesion:  '+str(fecha)),
                        function='CONCAT')
    ).annotate(accion=Value('inicio_sesion'),id_estado=Value(estado.id))
    canal = get_channel_layer()

    data = list(usuario.values('datos_user', 'accion','id_estado'))

    async_to_sync(canal.group_send)(
        'novedades', {
            'type': 'publicar_datos',
            'datos_logueo': data
        }
    )


@receiver(user_logged_out)
def fin(sender, **kwargs):
    d = Estado.objects.filter(user=kwargs.get('user'))


    canal = get_channel_layer()
    data = list(d.values('id'))
    async_to_sync(canal.group_send)(
        'novedades', {
            'type': 'publicar_datos',
            'datos_logueo': data
        }
    )
    Estado.objects.filter(user=kwargs.get('user')).delete()

@receiver(post_save, sender=NovedadesGenerales)
def crear_novedad(sender, instance, created, **kwargs):
    if created:

        canal = get_channel_layer()
        novedades = NovedadesGenerales.objects.filter(subsanada='No')
        cant_criticas = novedades.filter(tipo__nivel='3').count()
        cant_altas = novedades.filter(tipo__nivel='2').count()
        cant_medias = novedades.filter(tipo__nivel='1').count()
        data = {
            'mapa': {'distrito': instance.distrito.distrito, 'fecha_novedad': instance.fecha.strftime('%d/%m/%Y %H:%M'),
                     'tipo': instance.tipo.tipo, 'nivel': instance.tipo.nivel,
                     'detalle': instance.detalle, 'subsanada': instance.subsanada,
                     'medidas_adoptadas': instance.medidas_adoptadas, 'latitud': instance.ubicacion.y,
                     'longitud': instance.ubicacion.x},
            'contadores': {'cant_criticas': cant_criticas, 'cant_altas': cant_altas, 'cant_medias': cant_medias}
        }
        if data['mapa']['subsanada'] == 'No':
            async_to_sync(canal.group_send)(
                'novedades', {
                    'type': 'publicar_novedad',
                    'datos': data
                }
            )
