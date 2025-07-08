from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget, IntegerWidget

from AppElecciones.models import Led


# https://django-import-export.readthedocs.io/en/latest/getting_started.html#creating-import-export-resource


class LEDRecurso(resources.ModelResource):
    distrito = Field(attribute='distrito__distrito', column_name='Distrito')
    direccion = Field(attribute='direccion', column_name='Dirección')
    latitud = Field(attribute='ubicacion__y', column_name='Latitud')
    longitud = Field(attribute='ubicacion__x', column_name='Longitud')
    tipo = Field(attribute='tipo__tipo', column_name='Tipo')
    obs = Field(attribute='obs', column_name='Observaciones')
    #cant_seg_ffaa = Field(attribute='cant_seg_ffaa',column_name='Cant Seg FFAA')
    cant_seg_ffseg = Field(attribute='fuerza_seg', column_name='Cant Seg FFSeg',widget=IntegerWidget())
    fecha_inicio =Field(attribute='fecha_ini_seg',column_name='Fecha inicio',widget=DateTimeWidget('%d/%m/%Y %H:%M'))
    fecha_fin=Field(attribute='fecha_fin_seg',column_name='Fecha fin',widget=DateTimeWidget('%d/%m/%Y %H:%M'))
    cant_seg_ffaa = Field(attribute='fuerza_armada', column_name='Cant FFAA',widget=IntegerWidget())
    fecha_inicio_fa = Field(attribute='fecha_ini_seg_fa', column_name='Fecha inicio', widget=DateTimeWidget('%d/%m/%Y %H:%M'))
    fecha_fin_fa = Field(attribute='fecha_fin_seg_fa', column_name='Fecha fin', widget=DateTimeWidget('%d/%m/%Y %H:%M'))

    class Meta:
        model = Led
        fields = ('distrito', 'direccion', 'latitud', 'longitud', 'tipo', 'obs',  'cant_seg_ffseg','fecha_inicio','cant_seg_ffaa', 'fecha_inicio_fa','fecha_fin_fa')
        export_order = ('distrito', 'direccion', 'latitud', 'longitud', 'tipo', 'obs', 'cant_seg_ffseg','fecha_inicio','fecha_fin','cant_seg_ffaa', 'fecha_inicio_fa','fecha_fin_fa')

