
from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget, DateWidget

from AppElecciones.models import VehiculosPropios

# https://django-import-export.readthedocs.io/en/latest/getting_started.html#creating-import-export-resource


class VehPropiosResource(resources.ModelResource):
    distrito = Field(attribute='distrito__distrito', column_name='Distrito')
    unidad = Field(attribute='unidad__nombre', column_name='Unidad')
    tipo_vehiculo_provisto = Field(attribute='tipo_vehiculo_provisto__tipo_vehiculo_provisto', column_name='Tipo')
    patente = Field(attribute='ni_patente_matricula', column_name='Patente')
    consumo = Field(attribute='consumo_en_litros_horas_voladas', column_name='Consumo')
    tipo_conbustible = Field(attribute='tipo_combustible', column_name='Tipo combustible')
    sensor_ = Field(attribute='sensor', column_name='Posee sensor')
    troncal_ = Field(attribute='troncal1', column_name='Troncal')
    class Meta:
        model = VehiculosPropios
        fields = ('distrito', 'unidad', 'tipo_vehiculo_provisto',
                  'patente', 'consumo', 'tipo_conbustible', 'sensor_', 'troncal_')
        export_order = ('distrito', 'unidad', 'tipo_vehiculo_provisto',
                        'patente', 'consumo', 'tipo_conbustible', 'sensor_', 'troncal_')


class VehPropioEmpleoResource(resources.ModelResource):
    unidad = Field(attribute='unidad__nombre', column_name='Unidad')
    tipo_vehiculo_provisto = Field(attribute='tipo_vehiculo_provisto__tipo_vehiculo_provisto', column_name='Tipo')
    patente = Field(attribute='ni_patente_matricula', column_name='Patente')
    consumo = Field(attribute='consumo_en_litros_horas_voladas', column_name='Consumo')
    tipo_conbustible = Field(attribute='tipo_combustible', column_name='Tipo combustible')
    sensor_ = Field(attribute='sensor', column_name='Spot/Celular')
    troncal_ = Field(attribute='troncal1', column_name='Troncal')


    organizacion = Field(attribute='organizacion', column_name='Organizacion')
    tareas = Field(attribute='tareas', column_name='Tareas')
    zona_trabajo = Field(attribute='zona_trabajo', column_name='Zona de trabajo')
    desde = Field(attribute='desde', column_name='Desde')
    hasta = Field(attribute='hasta', column_name='Hasta')
    kilometros_a_recorrer = Field(attribute='kilometros_a_recorrer', column_name='Distancia')
    obs = Field(attribute='obs', column_name='Observaciones')
    conductor = Field(attribute='conductor', column_name='Conductor')
    class Meta:
        model = VehiculosPropios
        fields = ('unidad', 'tipo_vehiculo_provisto', 'patente', 'consumo', 'tipo_combustible', 'sensor_', 'troncal_', 'organizacion', 'tareas', 'zona_trabajo', 'desde', 'hasta', 'kilometros_a_recorrer', 'obs', 'conductor')
        export_order = ('unidad', 'tipo_vehiculo_provisto', 'patente', 'consumo', 'tipo_combustible', 'sensor_', 'troncal_', 'organizacion', 'tareas', 'zona_trabajo', 'desde', 'hasta', 'kilometros_a_recorrer', 'obs', 'conductor')
