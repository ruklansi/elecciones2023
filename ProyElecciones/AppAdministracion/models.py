import mptt
from django.contrib.auth.models import Group, AbstractUser, Permission
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, post_delete
from mptt.fields import TreeForeignKey

from ProyElecciones import settings
from validadores import ContentTypeRestrictedFileField, validar_te, validar_dni


class CamposEnMayusculas(models.CharField):
    def __init__(self, *args, **kwargs):
        super(CamposEnMayusculas, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        # return str(value).lower()
        return str(value).upper()


TreeForeignKey(Group, on_delete=models.CASCADE, related_name='grupo_coffa', blank=True, null=True,
               db_index=True).contribute_to_class(Group, 'parent')
mptt.register(Group, order_insertion_by=['name'])


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        pass

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

        self.set_cache()

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)


class ManualLectorCGE(SingletonModel):
    manual = ContentTypeRestrictedFileField(content_types=['application/pdf', ],
                                            max_upload_size=5242880, blank=True, null=True,
                                            verbose_name="Manual del usuario Lector-CGE")

    class Meta:
        verbose_name = 'Manual del usuario Lector-CGE'
        verbose_name_plural = 'Manual del usuario Lector-CGE'


class ManualPersonalCGE(SingletonModel):
    manual = ContentTypeRestrictedFileField(content_types=['application/pdf', ],
                                            max_upload_size=5242880, blank=True, null=True,
                                            verbose_name="Manual del usuario Personal-CGE")

    class Meta:
        verbose_name = 'Manual del usuario Personal-CGE'
        verbose_name_plural = 'Manual del usuario Personal-CGE'


class ManualLogisticaCGE(SingletonModel):
    manual = ContentTypeRestrictedFileField(content_types=['application/pdf', ],
                                            max_upload_size=5242880, blank=True, null=True,
                                            verbose_name="Manual del usuario Logística-CGE")

    class Meta:
        verbose_name = 'Manual del usuario Logística-CGE'
        verbose_name_plural = 'Manual del usuario Logística-CGE'


class ManualDistrito(SingletonModel):
    manual = ContentTypeRestrictedFileField(content_types=['application/pdf', ],
                                            max_upload_size=5242880, blank=True, null=True,
                                            verbose_name="Manual del usuario Distrito")

    class Meta:
        verbose_name = 'Manual del usuario Distrito'
        verbose_name_plural = 'Manual del usuario Distrito'


class ManualSubdistrito(SingletonModel):
    manual = ContentTypeRestrictedFileField(content_types=['application/pdf', ],
                                            max_upload_size=5242880, blank=True, null=True,
                                            verbose_name="Manual del usuario Subdistrito")

    class Meta:
        verbose_name = 'Manual del usuario subdistrito'
        verbose_name_plural = 'Manual del usuario Subdistrito'


class ManualTableros(SingletonModel):
    manual = ContentTypeRestrictedFileField(content_types=['application/pdf', ],
                                            max_upload_size=5242880, blank=True, null=True,
                                            verbose_name="Manual de tableros de visualización")

    class Meta:
        verbose_name = 'Manual de tablero de visualización'
        verbose_name_plural = 'Manual de tableros de visualización'


class Usuario(AbstractUser):
    ROL = (
        (1, 'adminsistema'),
        (2, 'cge'),
        (3, 'distrito'),
        (4, 'subdistrito'),
        (5, 'seccion'),
        (6, 'circuito'),
        (7, 'personal'),
        (8, 'logistica'),
        (9, 'personal-CGE'),
        (10, 'material-CGE'),
        (100, 'sin rol'),
    )
    RESET = (
        (1, 'adminsistema'),
        (2, 'usuario'),
    )
    first_name = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Grado y Nombre(s)',
                                    help_text='Ejemplo: SM Juan Carlos Rodriguez')
    last_name = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Apellido(s)')
    is_staff = models.BooleanField(verbose_name='Es staff?', blank=False, null=True, default=False)
    is_superuser = models.BooleanField(verbose_name='Es Super usuario?', blank=False, null=True, default=False)
    is_active = models.BooleanField(verbose_name='Esta activa su cuenta?', blank=False, null=True, default=True)
    email = models.EmailField(max_length=254, blank=False, unique=True)
    dni = models.CharField(max_length=10, validators=[validar_dni], null=True, blank=False, verbose_name='DNI',
                           unique=True)
    nro_tel = models.CharField(max_length=30, validators=[validar_te], null=True, blank=False,
                               verbose_name='Número de teléfono celular')
    fecha_registro_usuario = models.DateTimeField(auto_now_add=True, null=True, blank=True,
                                                  verbose_name="Fecha registro usuario")
    rol = models.PositiveSmallIntegerField(choices=ROL, null=True, blank=False)
    grupo_organizacion = models.ForeignKey(Group, on_delete=models.PROTECT, null=True, blank=False,
                                           related_name='grupo_usuario')
    fecha_reseteo = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de reset")
    tipo_reseteo = models.PositiveSmallIntegerField(choices=RESET, null=True, blank=False)

    class Meta:
        verbose_name = 'Usuarios'
        verbose_name_plural = 'Usuarios'
        ordering = ('-fecha_registro_usuario',)
        db_table = "usuario"

    def save(self, *args, **kwargs):
        super(Usuario, self).save(*args, **kwargs)


# auditlog.register(Usuario)


# https://docs.djangoproject.com/en/3.2/topics/auth/default/#permissions-and-authorization
def asignar_usuario_a_grupo(sender, instance, created, **kwargs):
    if not instance.is_superuser:
        if instance.rol > 1 and instance.rol <= 10:
            grupo_sistema = Group.objects.get(id=instance.grupo_organizacion.id)
            instance.groups.clear()
            grupo_sistema.user_set.add(instance)
        if instance.rol == 1:
            grupo_adminsistema = Group.objects.get(id=instance.grupo_organizacion.id)
            instance.groups.clear()
            grupo_adminsistema.user_set.add(instance)



def borrar_usuario_de_un_grupo(sender, instance, **kwargs):
    if not instance.is_superuser:
        if instance.rol > 1 and instance.rol <= 10:
            grupo_sistema = Group.objects.get(id=instance.grupo_organizacion.id)
            grupo_sistema.user_set.remove(instance)
        if instance.rol == 1:
            instance.user_permissions.clear()


post_save.connect(asignar_usuario_a_grupo, sender=Usuario)
post_delete.connect(borrar_usuario_de_un_grupo, sender=Usuario)


class Estado(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='estado')
    status = models.BooleanField(default=False)
    inicio_sesion = models.DateTimeField(auto_now=True, null=True, blank=False)

    def __str__(self):
        return f"Estado de {self.user.username}"


class MensajeParaUsuario(models.Model):
    mensaje = models.TextField(max_length=400, null=True, blank=False,
                               verbose_name='Mensaje para el usuario')
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=False, verbose_name="Creado el día")
    activo = models.BooleanField(
        verbose_name='Se encuentra activo?', blank=False, null=True)

    class Meta:
        verbose_name = 'Mensaje para los usuarios'
        verbose_name_plural = 'Mensaje para los usuarios'

    def __str__(self):
        return "Último mensaje del: %s" % self.fecha_creacion
