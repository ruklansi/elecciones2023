from django.contrib.postgres.aggregates import StringAgg
from django.db.models import Sum
from import_export import resources
from import_export.widgets import Widget
from import_export.fields import Field
from AppElecciones.models import *


# https://django-import-export.readthedocs.io/en/latest/getting_started.html#creating-import-export-resource
# https://simpleisbetterthancomplex.com/tutorial/2016/07/29/how-to-export-to-excel.html--->>>>Este link es para manejar excel
# https://simpleisbetterthancomplex.com/packages/2016/08/11/django-import-export.html--->>>>Este link es de import_export

class LocalesResource(resources.ModelResource):
    nombre = Field(attribute='nombre', column_name='Nombre')
    localidad = Field(attribute='localidad', column_name='Localidad')
    direccion = Field(attribute='direccion', column_name='Dirección')
    circuito = Field(attribute='circuito', column_name='Circuito')
    seccion = Field(attribute='seccion', column_name='Sección')
    subdistrito = Field(attribute='subdistrito', column_name='Subdistrito')
    distrito = Field(attribute='distrito', column_name='Distrito')
    latitud = Field(attribute='ubicacion__y', column_name='Latitud')
    longitud = Field(attribute='ubicacion__x', column_name='Longitud')
    estado_local = Field(attribute='estado_local', column_name='Estado del local')
    nro_mesas = Field(attribute='nro_mesas', column_name='Numero de mesas')
    cant_mesas = Field(attribute='cant_mesas', column_name='Cantidad de mesas')
    cant_electores = Field(attribute='cant_electores', column_name='Cantidad de electores')
    cant_seg_ext = Field(attribute='cant_seg_ext', column_name='Cantidad de Seg Externa')
    cant_seg_interna = Field(attribute='cant_seg_interna', column_name='Cantidad de Seg Interna')
    transmite_telegrama = Field(attribute='transmite_telegrama', column_name='Transmite telegrama')

    class Meta:
        model = exportarlocales
        fields = ('nombre', 'localidad', 'direccion', 'circuito', 'seccion', 'subdistrito', 'distrito',
                  'latitud', 'longitud','nro_mesas', 'cant_mesas', 'cant_electores', 'cant_seg_ext', 'cant_seg_interna',
                  'transmite_telegrama')
        export_order = ('nombre', 'direccion', 'localidad','circuito', 'seccion', 'subdistrito', 'distrito',
                  'latitud', 'longitud','nro_mesas', 'cant_mesas', 'cant_electores', 'cant_seg_ext', 'cant_seg_interna',
                  'transmite_telegrama')











# class LocalesResource(resources.ModelResource):
#     nombre = Field(attribute='nombre', column_name='Nombre')
#     localidad = Field(attribute='localidad', column_name='Localidad')
#     direccion = Field(attribute='direccion', column_name='Direccion')
#     circuito = Field(attribute='circuito__circuito', column_name='Circuito')
#     seccion = Field(attribute='circuito__seccion__seccion', column_name='Sección')
#     subdistrito = Field(attribute='circuito__seccion__subdistrito__subdistrito', column_name='Subdistrito')
#     distrito = Field(attribute='circuito__seccion__distrito__distrito', column_name='Distrito')
#     latitud = Field(attribute='ubicacion__y', column_name='Latitud')
#     longitud = Field(attribute='ubicacion__x', column_name='Longitud')
#     mesa = Field(attribute='cantmesas', column_name="Cant de mesas")
#     detalleMesas = Field(column_name='Nro de mesa')
#     electores = Field(column_name="Cant de Electores")
#     segInterna = Field(column_name='Cant Seg Interna')
#     segExterna = Field(column_name='Cant Seg Externa')
#     validado = Field(attribute='get_validado_display', column_name='Validado')
#     transmite_telegrama = Field(column_name='Transmite telegrama')
#     class Meta:
#         model = Local
#         fields = ('nombre', 'localidad', 'direccion', 'circuito', 'seccion', 'subdistrito', 'sistrito',
#                   'latitud', 'longitud', 'mesa', 'detalleMesas', 'electores', 'tipoDeMesas', 'segExterna',
#                   'segInterna', 'transmite_telegrama')
#
#         export_order = ()
#     def dehydrate_transmite_telegrama(self, local):
#
#         if local.transmite_telegrama:
#             transmite = 'Sí'
#         else:
#             transmite = 'No'
#         return transmite
#
#
#     def dehydrate_electores(self, local):
#         cant_electores = MesasEnLocal.objects.filter(local=local).aggregate(Sum('cant_electores'))
#         if not cant_electores['cant_electores__sum']:
#             electores = 0
#         else:
#             electores = cant_electores['cant_electores__sum']
#         return electores
#
#     def dehydrate_segInterna(self, local):
#         j_local = SegInternaLocal.objects.filter(local=local).count()
#         auxiliares = AuxiliarLocal.objects.filter(seg_interna_local__local=local).count()
#         total_seg_interna = j_local + auxiliares
#         return total_seg_interna
#
#     def dehydrate_segExterna(self, local):
#         seg_externa = SegExternaLocal.objects.filter(
#             local=local).aggregate(Sum('cant_efectivos'))
#         if not seg_externa['cant_efectivos__sum']:
#             seg_externa = 0
#         else:
#             seg_externa = seg_externa['cant_efectivos__sum']
#         return seg_externa
#
#     def dehydrate_detalleMesas(self, local):
#         detalle_mesas = MesasEnLocal.objects.filter(local=local).aggregate(arr=StringAgg('mesas', ' - '))
#         return detalle_mesas['arr']
