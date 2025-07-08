from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateTimeWidget

from AppAdministracion.models import Usuario


# https://django-import-export.readthedocs.io/en/latest/getting_started.html#creating-import-export-resource


class UsuarioRecurso(resources.ModelResource):
    grado_nombre = Field(attribute='first_name', column_name='Grado y nombres')
    apellido = Field(attribute='last_name', column_name='Apellido')
    email = Field(attribute='email', column_name='Email')
    dni = Field(attribute='dni', column_name='DNI')
    nro_tel = Field(attribute='nro_tel', column_name='Número de tel')
    # rol = Field(attribute='get_rol_display', column_name='Rol')
    grupo = Field(attribute='grupo_organizacion', column_name='Operador de')
    ultimo_logueo = Field(attribute='last_login', column_name='Último ingreso', widget=DateTimeWidget('%d/%m/%Y %H:%M'))

    class Meta:
        model = Usuario
        fields = ('grado_nombre', 'apellido', 'dni', 'email', 'nro_tel', 'grupo', 'ultimo_logueo')
        export_order = ('grado_nombre', 'apellido', 'dni', 'email', 'nro_tel', 'grupo', 'ultimo_logueo')

