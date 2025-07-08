from import_export import resources
from import_export.fields import Field

from AppElecciones.models import GuiaAutoridades

class GuiaRecurso(resources.ModelResource):
    organizacion = Field(attribute='org_texto', column_name='Organización')
    grado = Field(attribute='persona_guia__grado', column_name='Grado')
    nombre = Field(attribute='persona_guia__nombre', column_name='Nombre')
    apellido = Field(attribute='persona_guia__apellido', column_name='Apellido')
    dni = Field(attribute='persona_guia__dni', column_name='DNI')
    puesto = Field(attribute='puesto_texto', column_name='Puesto')
    gde = Field(attribute='gde_guia', column_name='Dirección GDE')
    telefono_directo = Field(attribute='tel_guia', column_name='Tel directo/interno')
    cel = Field(attribute='persona_guia__nro_tel', column_name='Celular')

    class Meta:
        model = GuiaAutoridades
        fields = ('grado', 'nombre', 'apellido', 'dni', 'puesto')
        export_order = ()

