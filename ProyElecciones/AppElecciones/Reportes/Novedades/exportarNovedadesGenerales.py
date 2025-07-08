from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget

from AppElecciones.models import NovedadesGenerales


class NovedadesGeneralesRecurso(resources.ModelResource):
    distrito = Field(attribute='distrito__distrito', column_name='Distrito')
    fecha = Field(attribute='fecha', column_name='Fecha', widget=DateTimeWidget('%d/%m/%Y %H:%M'))
    tipo = Field(attribute='tipo__tipo', column_name='Tipo')
    detalle = Field(attribute='detalle', column_name='Detalle')
    subsanada = Field(attribute='subsanada', column_name='Solucionada')
    medidas_adoptadas = Field(attribute='medidas_adoptadas', column_name='Medidas adoptadas')
    latitud = Field(attribute='ubicacion__y', column_name='Latitud')
    longitud = Field(attribute='ubicacion__x', column_name='Longitud')
    class Meta:
        model = NovedadesGenerales
        fields = ('distrito', 'fecha', 'latitud', 'longitud', 'tipo', 'detalle', 'subsanada', 'medidas_adoptadas')
        export_order = ('distrito', 'fecha', 'latitud', 'longitud', 'tipo', 'detalle', 'subsanada', 'medidas_adoptadas')
