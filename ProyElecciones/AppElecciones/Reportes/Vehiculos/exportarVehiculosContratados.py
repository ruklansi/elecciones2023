from django.contrib import messages
from django.shortcuts import redirect
from import_export import resources
from import_export.fields import Field
from AppElecciones.models import VehiculosContratados

# https://django-import-export.readthedocs.io/en/latest/getting_started.html#creating-import-export-resource


class VehContratadosResource(resources.ModelResource):

    distrito = Field(attribute='distrito__distrito', column_name='Distrito')
    tipo_vehiculo_contratado = Field(attribute='tipo_vehiculo_contratado__tipo_vehiculo_civil', column_name='Tipo')
    patente = Field(attribute='patente_matricula', column_name='Patente')
    sensor_ = Field(attribute='sensor', column_name='Posee sensor')
    troncal_ = Field(attribute='troncal1', column_name='Troncal')

    class Meta:
        model = VehiculosContratados
        fields = ('distrito', 'tipo_vehiculo_contratado', 'patente', 'sensor_', 'troncal_')
        export_order = ('distrito', 'tipo_vehiculo_contratado', 'patente', 'sensor_', 'troncal_')



class VehContratadoEmpleoResource(resources.ModelResource):
    tipo_vehiculo_contratado = Field(attribute='tipo_vehiculo_contratado__tipo_vehiculo_civil', column_name='Tipo')
    patente = Field(attribute='patente_matricula', column_name='Patente')
    sensor_ = Field(attribute='sensor', column_name='Spot/Celular')
    troncal_ = Field(attribute='troncal1', column_name='Troncal')


    organizacion = Field(attribute='organizacion', column_name='Organizacion')
    cantidad_pasajeros = Field(attribute='cantidad_pasajeros', column_name='Pasajeros')
    tareas = Field(attribute='tareas', column_name='Tareas')
    zona_trabajo = Field(attribute='zona_trabajo', column_name='Zona de trabajo')
    desde = Field(attribute='desde', column_name='Desde')
    hasta = Field(attribute='hasta', column_name='Hasta')
    kilometros_a_recorrer = Field(attribute='kilometros_a_recorrer', column_name='Distancia')
    obs = Field(attribute='obs', column_name='Observaciones')
    responsable = Field(attribute='responsable', column_name='Responsable')
    class Meta:
        model = VehiculosContratados
        fields = ('tipo_vehiculo_contratado', 'patente', 'sensor_', 'troncal_', 'organizacion', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde', 'hasta', 'kilometros_a_recorrer', 'obs', 'responsable')
        export_order = ('tipo_vehiculo_contratado', 'patente',  'sensor_', 'troncal_', 'organizacion', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde', 'hasta', 'kilometros_a_recorrer', 'obs', 'responsable')

    def before_export(self, queryset, *args, **kwargs):
        print(queryset)
        pass