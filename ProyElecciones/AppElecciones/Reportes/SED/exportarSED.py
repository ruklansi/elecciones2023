from import_export import resources
from import_export.fields import Field

from AppElecciones.models import Sed


# https://django-import-export.readthedocs.io/en/latest/getting_started.html#creating-import-export-resource


class SEDRecurso(resources.ModelResource):
    distrito = Field(attribute='distrito__distrito', column_name='Distrito')
    direccion = Field(attribute='direccion', column_name='Dirección')
    latitud = Field(attribute='ubicacion__y', column_name='Latitud')
    longitud = Field(attribute='ubicacion__x', column_name='Longitud')
    sed = Field(attribute='sed', column_name='Sucursal Electoral Digital')
    localidad = Field(attribute='localidad', column_name='Localidad')
    telefono = Field(attribute='telefono',column_name='Telefono local/responsable')


    class Meta:
        model = Sed
        fields = ('distrito', 'direccion', 'latitud', 'longitud', 'sed', 'localidad', 'telefono')
        export_order = ('distrito', 'direccion', 'latitud', 'longitud', 'sed', 'localidad', 'telefono')

