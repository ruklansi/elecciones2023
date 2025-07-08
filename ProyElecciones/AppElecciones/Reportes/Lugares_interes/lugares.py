from import_export import resources
from import_export.fields import Field

from AppElecciones.models import LugarInteres


# https://django-import-export.readthedocs.io/en/latest/getting_started.html#creating-import-export-resource


class LugarRecurso(resources.ModelResource):
    distrito = Field(attribute='distrito__distrito', column_name='Distrito')
    tipo = Field(attribute='tipo_lugar', column_name='Tipo')
    autoridad = Field(attribute='autoridad', column_name='Autoridad')
    direccion = Field(attribute='direccion', column_name='Dirección')
    latitud = Field(attribute='ubicacion__y', column_name='Latitud')
    longitud = Field(attribute='ubicacion__x', column_name='Longitud')
    telefono = Field(attribute='telefono', column_name='Telefono')
    obs = Field(attribute='obs', column_name='Observaciones')

    class Meta:
        model = LugarInteres
        fields = ('distrito', 'tipo', 'autoridad', 'direccion', 'latitud', 'longitud', 'telefono', 'obs')
        export_order = ('distrito', 'tipo', 'autoridad', 'direccion', 'latitud', 'longitud', 'telefono', 'obs')

