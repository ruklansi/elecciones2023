from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget

from AppElecciones.models import NovedadesEnLocal


class NovedadesEnLocalesRecurso(resources.ModelResource):
    fecha = Field(attribute='fecha', column_name='Fecha', widget=DateTimeWidget('%d/%m/%Y %H:%M'))
    tipo = Field(attribute='tipo__tipo', column_name='Tipo')
    detalle = Field(attribute='detalle', column_name='Detalle')
    subsanada = Field(attribute='subsanada', column_name='Solucionada')
    medidas_adoptadas = Field(attribute='medidas_adoptadas', column_name='Medidas adoptadas')
    nombre_local = Field(attribute='local__nombre', column_name='Local')
    latitud_local = Field(attribute='local__ubicacion__y', column_name='Latitud')
    longitud_local = Field(attribute='local__ubicacion__x', column_name='Longitud')
    distrito = Field(attribute='local__circuito__seccion__distrito__distrito', column_name='Distrito')
    subdistrito = Field(attribute='local__circuito__seccion__subdistrito__subdistrito', column_name='Subdistrito')
    seccion = Field(attribute='local__circuito__seccion__seccion', column_name='Sección')
    circuito = Field(attribute='local__circuito__circuito', column_name='Circuito')
    class Meta:
        model = NovedadesEnLocal
        fields = ('fecha', 'tipo', 'detalle', 'subsanada', 'medidas_adoptadas', 'nombre_local', 'latitud_local',
                  'longitud_local', 'distrito', 'subdistrito', 'seccion', 'circuito')
        export_order = ('fecha', 'tipo', 'detalle', 'subsanada', 'medidas_adoptadas', 'nombre_local',
                        'latitud_local', 'longitud_local', 'distrito', 'subdistrito', 'seccion', 'circuito')
