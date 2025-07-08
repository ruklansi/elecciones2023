from import_export import resources
from import_export.fields import Field

from AppElecciones.models import Persona, exportarpersonal


# https://django-import-export.readthedocs.io/en/latest/getting_started.html#creating-import-export-resource

class PersonaRecurso(resources.ModelResource):
    grado = Field(attribute='grado', column_name='Grado')
    nombre = Field(attribute='nombre', column_name='Nombre')
    apellido = Field(attribute='apellido', column_name='Apellido')
    dni = Field(attribute='dni', column_name='DNI')
    nro_tel = Field(attribute='nro_tel', column_name='Nro de teléfono')
    fuerza = Field(attribute='fuerza', column_name='Fuerza')
    cargo = Field(attribute='cargo', column_name='Cargo')
    cge = Field(attribute='cge', column_name='Cge')
    distrito = Field(attribute='distrito', column_name='Distrito')
    subdistrito = Field(attribute='subdistrito', column_name='Subdistrito')
    seccion = Field(attribute='seccion', column_name='Sección')
    circuito = Field(attribute='circuito', column_name='Circuito')
    nombre_local = Field(attribute='nombre_local', column_name='Local')
    direccion = Field(attribute='direccion', column_name='Dirección')
    localidad = Field(attribute='localidad', column_name='Localidad')
    reserva = Field(attribute='reserva', column_name='Reserva')
    seg_interna_local = Field(attribute='seg_interna_local', column_name='Seguridad interna en el local')
    latitud = Field(attribute='latitud', column_name='Latitud del local')
    longitud = Field(attribute='longitud', column_name='Longitud del local')
    tipo_armamento = Field(attribute='tipo_armamento', column_name='Tipo de Armamento')
    nro_armamento = Field(attribute='nro_armamento', column_name='Nro armamento')


    class Meta:
        model = exportarpersonal
        fields = ('grado', 'nombre', 'apellido', 'dni', 'nro_tel', 'fuerza', 'distrito','subdistrito','seccion','circuito', 'cargo', 'cge', 'reserva', 'tipo_armamento', 'nro_armamento', 'seg_interna_local', 'nombre_local','direccion', 'localidad', 'latitud', 'longitud')
        export_order = ('grado', 'nombre', 'apellido', 'dni', 'nro_tel', 'fuerza', 'distrito','subdistrito','seccion','circuito', 'cargo', 'cge', 'reserva', 'tipo_armamento', 'nro_armamento', 'seg_interna_local', 'nombre_local','direccion', 'localidad', 'latitud', 'longitud')


    # class PersonaRecurso(resources.ModelResource):
#     grado = Field(attribute='grado', column_name='Grado')
#     nombre = Field(attribute='nombre', column_name='Nombre')
#     apellido = Field(attribute='apellido', column_name='Apellido')
#     dni = Field(attribute='dni', column_name='DNI')
#     fuerza = Field(attribute='fuerza', column_name='Fuerza')
#     nro_tel = Field(attribute='nro_tel', column_name='Teléfono')
#     mi_puesto = Field(attribute='puesto', column_name='Puesto')
#     mi_organizacion = Field(attribute='dis_cge', column_name='Distrito/CGE')
#     mi_subdistrito = Field(attribute='subdis', column_name='Subdistrito')
#     tipo_armamento = Field(attribute='get_tipo_armamento_display', column_name='Tipo de armamento')
#     numero_armamento = Field(attribute='numero_armamento', column_name='Nro de armamento')
#
#     class Meta:
#         model = Persona
#         fields = ('grado', 'nombre', 'apellido', 'fuerza', 'mi_puesto', 'dni', 'nro_tel', 'tipo_armamento',
#                   'numero_armamento', 'mi_organizacion', 'mi_subdistrito')
#         export_order = ('grado', 'nombre', 'apellido', 'dni', 'nro_tel', 'fuerza',
#                         'mi_puesto', 'mi_organizacion', 'mi_subdistrito', 'tipo_armamento', 'numero_armamento')
#         # widgets = {
#         #        'fecha_creacion': {'format': '%d.%m.%Y'},
#         #        'fecha_modificacion': {'format': '%d.%m.%Y'},
#         #        }


