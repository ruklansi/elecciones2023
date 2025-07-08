from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from mptt.admin import DraggableMPTTAdmin
from guardian.admin import GuardedModelAdmin

# from .models import Usuario
from .models import ManualLectorCGE, Usuario, Estado, ManualPersonalCGE, ManualLogisticaCGE, ManualDistrito, \
    ManualSubdistrito, ManualTableros, MensajeParaUsuario

admin.site.register(ManualLectorCGE)
admin.site.register(ManualPersonalCGE)
admin.site.register(ManualLogisticaCGE)
admin.site.register(ManualDistrito)
admin.site.register(ManualSubdistrito)
admin.site.register(ManualTableros)


class UsuarioRecurso(resources.ModelResource):
    class Meta:
        model = Usuario


class UsuarioAdmin(GuardedModelAdmin, UserAdmin, ImportExportModelAdmin):
    resource_class = UsuarioRecurso
    list_display = ('username', 'first_name', 'last_name', 'dni', 'nro_tel', 'rol', 'is_active', 'is_staff', 'is_superuser', 'email',
                    'fecha_registro_usuario', 'grupos')
    list_filter = ('rol',)

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('rol', 'dni', 'nro_tel')}),
    )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     (None, {'fields': ('is_active', 'is_staff', 'is_superuser', 'email',
    #                        'rol', 'dni', 'nro_tel','groups')}),
    # )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_active', 'rol', 'email', 'dni', 'nro_tel',)}),
    )
    def grupos(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UsuarioAdmin, self).get_inline_instances(request, obj)

class EstadoRecurso(resources.ModelResource):
    class Meta:
        model = Estado

class EstadoAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = EstadoRecurso
    list_display = ('user', 'status', 'inicio_sesion')

# Zona de desregistración/registracion de los modelos
admin.site.unregister(Group)

class  MensajeParaUsuarioRecurso(resources.ModelResource):
    class Meta:
        model = MensajeParaUsuario
class MensajeParaUsuarioAdmin(GuardedModelAdmin, ImportExportModelAdmin):
    resource_class = MensajeParaUsuarioRecurso
    list_display = ('mensaje', 'fecha_creacion', 'activo')

admin.site.register(MensajeParaUsuario, MensajeParaUsuarioAdmin)

class grupoAdmin(DraggableMPTTAdmin,ImportExportModelAdmin):
    pass
admin.site.register(Group,grupoAdmin )
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Estado, EstadoAdmin)
