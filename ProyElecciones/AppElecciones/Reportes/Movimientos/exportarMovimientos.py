from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateWidget, DateTimeWidget

from AppElecciones.models import Movimientos


class MovimientosRecurso(resources.ModelResource):
    distrito = Field(attribute='distrito__distrito', column_name='Distrito')
    tipo = Field(attribute='tipo__tipo', column_name='Tipo')
    cant_efectivos = Field(attribute='efectivos', column_name='Cant Efectivos')
    cant_vehiculos = Field(attribute='vehiculos', column_name='Cant Vehículos')
    fecha_inicio = Field(attribute='inicio', column_name='Fecha inicio', widget=DateTimeWidget('%d/%m/%Y %H:%M'))
    fecha_fin = Field(attribute='fin', column_name='Fecha fin', widget=DateTimeWidget('%d/%m/%Y %H:%M'))

    class Meta:
        model = Movimientos
        fields = ('distrito', 'tipo', 'cant_efectivos', 'cant_vehiculos', 'fecha_inicio', 'fecha_fin')
        export_order = ('distrito', 'tipo', 'cant_efectivos', 'cant_vehiculos', 'fecha_inicio', 'fecha_fin')