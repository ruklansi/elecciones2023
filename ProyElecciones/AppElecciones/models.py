####Tips y comantarios###########
from auditlog.registry import auditlog
from crum import get_current_user
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models as modelogis
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.forms import model_to_dict
from django.utils import timezone
from django.utils.timezone import now
from guardian.models import UserObjectPermission, GroupObjectPermission
from guardian.shortcuts import assign_perm
from unidecode import unidecode

from AppAdministracion.models import Usuario
from validadores import validar_dni, validar_te


# https://www.b-list.org/weblog/2007/nov/02/handle-choices-right-way/
# Filtro inverso
# Persona.objects.filter((nombre del modelo en minuscula))__camploabuscar__contains='xxx') -> http://django-book.blogspot.com/2012/11/realizando-consultas-una-vez-que-hayas.html


class CamposEnMayusculas(models.CharField):
    def __init__(self, *args, **kwargs):
        super(CamposEnMayusculas, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        # return str(value).lower()
        return str(value).upper()


# https://steelkiwi.com/blog/practical-application-singleton-design-pattern/


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


class CdoGrlElect(SingletonModel):
    nombre = CamposEnMayusculas(max_length=30, default='CdoGrlElec')
    grupo = models.OneToOneField(Group, null=True, blank=True, on_delete=models.PROTECT,
                                 verbose_name="Grupo del CGE",
                                 related_name='gurpo_del_cge')

    class Meta:
        verbose_name = 'Comando General Electoral'
        verbose_name_plural = 'Comando General Electoral'
        permissions = (
            ("admin_pers_cge_cdogrlelect", "Crear Pers y Reserva CGE"),
            ("admin_veh_cge_cdogrlelect", "Asignar Veh Propios y Contratados CGE"),

        )
        db_table = "cdogrlelect"

    def save(self, *args, **kwargs):
        if not self.pk:
            sin_espacios = str(self.nombre).replace(" ", "").lower()
            nombre_grupo_temp = unidecode(sin_espacios)
            nombre_grupo = nombre_grupo_temp
            grupo, creado = Group.objects.get_or_create(name=nombre_grupo)
            self.grupo = grupo
        super(CdoGrlElect, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Distrito(models.Model):
    distrito = CamposEnMayusculas(max_length=50, verbose_name="Distrito Electoral", null=False,
                                  blank=False, unique=True,
                                  error_messages={'unique': 'Ya existe un Distrito con ese nombre.'})
    cge = models.ForeignKey('CdoGrlElect', related_name='cge',
                            on_delete=models.PROTECT, null=True, blank=False)

    grupo = models.OneToOneField(Group, null=True, blank=True, on_delete=models.PROTECT,
                                 verbose_name="Grupo de Distrito",
                                 related_name='gurpo_del_distrito')

    #
    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         sin_espacios = str(self.distrito).replace(" ", "").lower()
    #         nombre_grupo_temp = unidecode(sin_espacios)
    #         nombre_grupo = nombre_grupo_temp
    #         grupo, creado = Group.objects.get_or_create(name=nombre_grupo)
    #         self.grupo = grupo
    #     else:
    #         if self.grupo:
    #             grupo_distrito_guardado, obtenida = Group.objects.get_or_create(name=self.grupo)
    #         nuevo_nombre_sin_espacios = str(self.distrito).replace(" ", "").lower()
    #         nombre_grupo_temp_nuevo = unidecode(nuevo_nombre_sin_espacios)
    #         grupo_distrito_guardado.name = nombre_grupo_temp_nuevo
    #         grupo_distrito_guardado.save()
    #         self.grupo = grupo_distrito_guardado
    #     super(Distrito, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Distrito'
        verbose_name_plural = 'Distritos'

    def __str__(self):
        return self.distrito


class Subdistrito(models.Model):
    subdistrito = CamposEnMayusculas(max_length=1, blank=False, null=True)
    distrito = models.ForeignKey('Distrito', related_name='distrito_electoral',
                                 on_delete=models.PROTECT, null=False, blank=False)
    detalle = CamposEnMayusculas(
        max_length=30, blank=False, null=True, verbose_name='Detalles/aclaraciones')
    nombre_del_grupo = CamposEnMayusculas(max_length=10, blank=False, null=True)

    grupo = models.OneToOneField(Group, null=True, blank=True, on_delete=models.PROTECT,
                                 verbose_name="Grupo del Subdistrito",
                                 related_name='gurpo_del_subdistrito')

    class Meta:
        verbose_name = 'Subdistrito'
        verbose_name_plural = 'Subdistritos'
        permissions = (
            ("ver_subdistrito_subdistrito", "Ver Subdistritos"),
        )

    def __str__(self):
        return "%s->%s" % (self.subdistrito, self.distrito)


class Seccion(models.Model):
    seccion = CamposEnMayusculas(max_length=3, blank=False, null=True)
    subdistrito = models.ForeignKey('Subdistrito', related_name='subdistrito_electoral',
                                    on_delete=models.PROTECT, null=True, blank=False, verbose_name='Subdistrito:')
    distrito = models.ForeignKey('Distrito', related_name='distrito_electora_de_la_seccion',
                                 on_delete=models.PROTECT, null=True, blank=False, verbose_name='Distrito:')
    detalle = CamposEnMayusculas(max_length=30, blank=True, null=False, verbose_name='Detalles/aclaraciones')

    class Meta:
        verbose_name = 'Seccion'
        verbose_name_plural = 'Secciones'

    def __str__(self):
        return self.seccion


class Circuito(models.Model):
    SITUACION = (
        ('Actividades no iniciadas', 'Actividades no iniciadas'),
        ('Inicio despliegue', 'Inicio despliegue'),
        ('Desplegado', 'Desplegado'),
        ('Inicio repliegue', 'Inicio repliegue'),
        ('Replegado', 'Replegado'),
    )
    circuito = CamposEnMayusculas(max_length=5, blank=False, null=True, verbose_name='Circuito:')
    seccion = models.ForeignKey(Seccion, related_name='seccion_electoral', on_delete=models.PROTECT, null=True,
                                blank=False, verbose_name='Sección:')
    situacion = models.CharField(max_length=30, choices=SITUACION,
                                 blank=False, null=True, default='Actividades no iniciadas')
    entrego_urna_en_led = models.BooleanField(
        verbose_name='Se entregó la urna al LED?', blank=True, null=True, default=False)
    detalle = CamposEnMayusculas(max_length=30, blank=True, null=True, verbose_name='Detalles/aclaraciones')
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'Circuito'
        verbose_name_plural = 'Circuitos'

    def __str__(self):
        return self.circuito


class EstadosLocal(models.Model):
    estado = CamposEnMayusculas(max_length=50, blank=False, null=True)
    causa = CamposEnMayusculas(max_length=50, blank=True, null=True, unique=True)

    class Meta:
        verbose_name = 'Estados del local'
        verbose_name_plural = 'Estados del local'

    def __str__(self):
        return "%s  %s" % (self.estado, self.causa)


class Local(models.Model):
    VALIDADO = (
        (0, 'No validado'),
        (1, 'Validado'),
    )
    nombre = CamposEnMayusculas(max_length=100, null=True, blank=False)
    localidad = CamposEnMayusculas(max_length=70, null=True, blank=False)
    direccion = CamposEnMayusculas(max_length=100, null=True, blank=False)
    circuito = models.ForeignKey(
        Circuito, related_name='locales_en_circuito', on_delete=models.PROTECT, null=True, blank=False)
    validado = models.IntegerField(
        choices=VALIDADO, blank=True, null=True, verbose_name='Validado',
        help_text='Validado permito asignarle mesas, datos de seguridad, novedades, iniciarlo y finalizarlo', default=1)

    estado = models.ForeignKey(
        EstadosLocal, on_delete=models.PROTECT, verbose_name='Estado del local', blank=False, null=True)

    ubicacion = modelogis.PointField(
        null=True, blank=False,
        verbose_name='Ubique el local en el mapa usando el buscador y luego debe fijarlo con la herramienta de '
                     '"Dibujar marcador" haciendo click en la misma')

    recepciono_mat_elec = models.BooleanField(
        verbose_name='Recepcionó material electoral?', blank=False, null=True, default=False)
    entrego_urna = models.BooleanField(
        verbose_name='Se entregó la urna?', blank=False, null=True, default=False)
    transmite_telegrama = models.BooleanField(
        verbose_name='Transmite telegrama en el local', blank=False, null=True, default=False)
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'Local'
        verbose_name_plural = 'Locales'
        permissions = (
            ("ver_locals_no_validados_local", "Ver locales no validados"),
            ("ver_locals_a_validar_en_mapa_local", "Ver locales a validar en mapa"),
        )

    def __str__(self):
        return self.nombre


auditlog.register(Local)


class EstadosMesas(models.Model):
    estado = CamposEnMayusculas(max_length=50, blank=False, null=True)
    causa = CamposEnMayusculas(max_length=50, blank=True, null=True, unique=True)

    class Meta:
        verbose_name = 'Estado de la mesa'
        verbose_name_plural = 'Estados de las mesas'

    def __str__(self):
        return self.estado


class MesasEnLocal(models.Model):
    VOTO = (
        (0, 'Nacional'),
        (1, 'Extranjera'),
    )
    local = models.ForeignKey(Local, related_name='mesas_en_local', on_delete=models.PROTECT, blank=False, null=True)
    mesas = CamposEnMayusculas(max_length=10, null=True, blank=False, verbose_name='Nro de mesa',
                               help_text='Cargar de a una mesa no por rango')
    estado = models.ForeignKey(EstadosMesas, on_delete=models.PROTECT, default=1, verbose_name='Estado de la mesa',
                               blank=False, null=True)
    cant_electores = models.IntegerField(blank=False, null=True, validators=[MinValueValidator(1)],
                                         verbose_name='Cantidad de electores')
    voto = models.IntegerField(
        choices=VOTO, blank=False, null=True, verbose_name='Tipo de mesas',
        help_text='Nacionales, extranjeras o mixtas')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")

    def __str__(self):
        return self.mesas


auditlog.register(MesasEnLocal)


class TransmisionTelegramas(models.Model):
    local = models.OneToOneField(Local, related_name='telegramas_en_local',
                                 on_delete=models.PROTECT, blank=False, null=True)
    transmite_telegrama = models.BooleanField(
        verbose_name='Transmitió telegramas?', blank=False, null=True, default=False)

    class Meta:
        verbose_name = 'Transmisión de telegramas'
        verbose_name_plural = 'Transmisión de telegramas'

    def __str__(self):
        return self.local.nombre


class HoraControlVoto(models.Model):
    hora = models.TimeField(blank=False, null=True, verbose_name="Horario a controlar")

    class Meta:
        verbose_name = 'Horario a controlar el voto'
        verbose_name_plural = 'Horarios a controlar los votos'

    def __str__(self):
        return str(self.hora)


class ControlDeVotos(models.Model):
    local = models.ForeignKey(Local, related_name='contro_votos_en_el_local',
                              on_delete=models.CASCADE, blank=False, null=True)
    horario = models.ForeignKey(HoraControlVoto, related_name='horario_a_controlar',
                                on_delete=models.PROTECT, blank=False, null=True, verbose_name='Horario')
    cant_votos = models.FloatField(validators=[MinValueValidator(1),
                                               MaxValueValidator(100)],
                                   blank=False, null=True, verbose_name='Porcentaje', help_text='Poner ayuda')

    class Meta:
        verbose_name = 'Control de votos en el local'
        verbose_name_plural = 'Control de votos en el local'

    def __str__(self):
        return "%s - %s - %s" % (self.horario, self.local, self.cant_votos)

    def save(self, *args, **kwargs):
        self.cant_votos = round(self.cant_votos, 1)
        super(ControlDeVotos, self).save(*args, **kwargs)


class TipoNovedadLocal(models.Model):
    NIVEL = (
        ('0', 'Baja'),
        ('1', 'Media'),
        ('2', 'Alta'),
        ('3', 'Crítica'),
    )
    LUGAR = (
        ('0', 'Local'),
        ('1', 'General'),
        ('2', 'Ambas'),
    )

    tipo = CamposEnMayusculas(
        max_length=30, blank=False, null=True, verbose_name="Tipo de novedad", help_text='Máximo 30 caracteres')
    nivel = models.CharField(max_length=1, choices=NIVEL, blank=False, null=True, default='0')
    lugar = models.CharField(max_length=1, choices=LUGAR, blank=False, null=True)

    class Meta:
        verbose_name = 'Tipo de novedades en el local y general'
        verbose_name_plural = 'Tipo de novedades en el local y generales'

    def __str__(self):
        return self.tipo


def validar_fecha_en_el_futuro(value):
    if value > timezone.now():
        raise ValidationError('La novedad no puede registrarse en el futuro')


class NovedadesEnLocal(models.Model):
    SUBSANADA = (
        ('Si', 'Si'),
        ('No', 'No')
    )
    local = models.ForeignKey(Local, related_name='novedad_en_el_local',
                              on_delete=models.PROTECT, blank=False, null=True)
    fecha = models.DateTimeField(
        verbose_name='Fecha', blank=False, null=False, default=now, validators=[validar_fecha_en_el_futuro])
    tipo = models.ForeignKey(TipoNovedadLocal, related_name='tipo_novedad_en_el_local',
                             on_delete=models.PROTECT, blank=False, null=False)
    detalle = CamposEnMayusculas(
        max_length=100, blank=False, null=True, verbose_name="Detalle",
        help_text="Detalle acotado de la novedad (Máximo 100 caracteres)")
    subsanada = models.CharField(max_length=2, choices=SUBSANADA,
                                 verbose_name='Se subsanó?', blank=False, null=True)
    medidas_adoptadas = CamposEnMayusculas(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'Novedades en el local'
        verbose_name_plural = 'Novedades en el local'

    def __str__(self):
        return "%s - %s" % (self.local, self.tipo)


auditlog.register(NovedadesEnLocal)


class Reparticion(models.Model):
    reparticion = CamposEnMayusculas(max_length=50, blank=False, null=True, unique=True)

    class Meta:
        verbose_name = 'Reparticion'
        verbose_name_plural = 'Reparticion'

    def __str__(self):
        return self.reparticion


class Fuerza(models.Model):
    fuerza = CamposEnMayusculas(max_length=50, blank=False, null=True, unique=True)
    reparticion = models.ForeignKey('Reparticion', related_name='reparticion_a_la_que_pertenece',
                                    on_delete=models.PROTECT, blank=False, null=True)
    orden = models.IntegerField(blank=False, null=True, validators=[MinValueValidator(1)], verbose_name='Orden',
                                help_text='Orden de precedencia')

    class Meta:
        verbose_name = 'Fuerzas Armadas'
        verbose_name_plural = 'Fuerzas Armadas'

    def __str__(self):
        return self.fuerza


class FuerzaSeguridad(models.Model):
    fuerza_seg = CamposEnMayusculas(max_length=50, blank=False, null=True, unique=True)
    reparticion = models.ForeignKey('Reparticion', related_name='reparticion_a_la_que_pertenece_fza_seg',
                                    on_delete=models.PROTECT, blank=False, null=True)
    orden = models.IntegerField(blank=False, null=True, validators=[MinValueValidator(1)], verbose_name='Orden',
                                help_text='Orden de precedencia')

    class Meta:
        verbose_name = 'Fuerzas de Seguridad'
        verbose_name_plural = 'Fuerzas de Seguridad'

    def __str__(self):
        return self.fuerza_seg


class SegExternaLocal(models.Model):
    fuerza = models.ForeignKey(FuerzaSeguridad, related_name='fuerza_seguridad_externa',
                               on_delete=models.PROTECT, blank=False, null=True)
    local = models.ForeignKey(Local, related_name='local_seguridad_externa',
                              on_delete=models.PROTECT, blank=False, null=True)
    cant_efectivos = models.IntegerField(validators=[MinValueValidator(1)],
                                         blank=False, null=False, verbose_name='Cantidad de Efectivos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        # unique_together = ("fuerza", "local")
        verbose_name = 'Seguridad externa en el local'
        verbose_name_plural = 'Seguridad externa en el local'

    def __str__(self):
        return "%s provee  %s efectivos" % (self.fuerza, self.cant_efectivos)


auditlog.register(SegExternaLocal)


class Jerarquia(models.Model):
    jerarquia = CamposEnMayusculas(max_length=50, blank=False, null=True, unique=True)
    orden = models.IntegerField(blank=False, null=True, validators=[MinValueValidator(1)], verbose_name='Orden',
                                help_text='Orden de precedencia')

    class Meta:
        verbose_name = 'Jerarquia'
        verbose_name_plural = 'Jerarquia'

    def __str__(self):
        return self.jerarquia


class Grado(models.Model):
    grado = CamposEnMayusculas(max_length=50, blank=False, null=True, unique=True)
    fuerza = models.ManyToManyField(Fuerza, blank=False)
    jerarquia = models.ForeignKey('Jerarquia', related_name='jerarquia_del_grado',
                                  on_delete=models.PROTECT, blank=False, null=True)

    class Meta:
        verbose_name = 'Grado'
        verbose_name_plural = 'Grados'

    def __str__(self):
        return str(self.grado)


class Persona(models.Model):
    VALIDADO = (
        (0, 'No validado'),
        (1, 'Validado'),
    )
    ARMAMENTO = (
        ('fusil', 'Fusil'),
        ('pistola', 'Pistola'),
        ('sin_armamento', 'Sin armamento'),
    )
    distrito = models.ForeignKey(Distrito, related_name='distrito_persona', on_delete=models.PROTECT,
                                 blank=False, null=True)
    fuerza = models.ForeignKey(Fuerza, related_name='fuerza_a_la_que_pertenece',
                               on_delete=models.PROTECT, blank=False, null=True, default='')
    grado = models.ForeignKey(Grado, related_name='grado_de_la_persona',
                              on_delete=models.PROTECT, blank=False, null=True)
    nombre = CamposEnMayusculas(max_length=50, blank=False, null=True)
    apellido = CamposEnMayusculas(max_length=50, blank=False, null=True)
    dni = models.CharField(max_length=10, validators=[validar_dni], null=True, blank=False, verbose_name='DNI',
                           unique=True)
    nro_tel = models.CharField(max_length=30, validators=[validar_te], null=True, blank=False,
                               verbose_name='Número de teléfono celular')
    tipo_armamento = models.CharField(max_length=20, choices=ARMAMENTO, blank=False, null=True,
                                      verbose_name='Tipo de armamento', default='',
                                      help_text="Sin armamento es exclusivamente para Cadetes/Aspirantes de Institutos "
                                                "de Formación. También para el Estado Mayor del Cdo Grl Elect, de los "
                                                "Distritos Electorales y Subdistritos")
    numero_armamento = models.IntegerField(blank=True, null=True, verbose_name='Número de armamento sólo con números',
                                           validators=[MinValueValidator(1)], help_text="")
    numero_armamento_con_letras = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número de armamento con números y letras')
    num_cargos = models.IntegerField(blank=True, null=True, verbose_name='Num cargos',
                                     default=0)
    num_conductor = models.IntegerField(blank=True, null=True, verbose_name='Num conductor',
                                        default=0)
    tiene_cargo = models.BooleanField(verbose_name='Tiene cargo?', blank=False, null=True, default=False)
    es_conductor = models.BooleanField(verbose_name='Es conductor?', blank=False, null=True, default=False)
    validado = models.IntegerField(choices=VALIDADO, blank=False, null=True, verbose_name='Validado',
                                   help_text='Validado permite asignarle puesto en la organización', default=1)
    validado_por = models.CharField(blank=True, null=True, max_length=100, verbose_name='Validado por',
                                    default='Sin Confirmar')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'Personas'
        verbose_name_plural = 'Personas'
        permissions = (
            ("ver_personas_no_validados_persona", "Ver Personas no validadas"),
        )

    def usuario(self, id):
        creador = self.usuario_creador
        fecha_creacion = self.fecha_creacion
        modificador = self.usuario_modificador
        fecha_modificacion = self.fecha_modificacion
        return ' - Creado por el usuario: ' + str(creador) + ' el día: ' + str(
            fecha_creacion.strftime("%d/%m/%y")) + ' - Modificado por el usuario: ' + str(
            modificador) + ' el día: ' + str(fecha_modificacion.strftime("%d/%m/%y"))

    def NombreCompleto(self):
        return "%s %s %s DNI: %s" % (self.grado, self.nombre, self.apellido, self.dni)

    def NombreCompletoDestino(self):
        return "%s %s %s DNI: %s %s" % (self.grado, self.nombre, self.apellido, self.dni, self.usuario(self))

    def __str__(self):
        return "%s %s DNI %s" % (self.grado, self.apellido, self.dni)


class SubdistritoPersona(models.Model):
    persona = models.ForeignKey(Persona, related_name="persona", on_delete=models.PROTECT, blank=False, null=True, verbose_name='Persona')
    subdistrito = models.ForeignKey(Subdistrito, related_name="subdistrito_persona", on_delete=models.PROTECT, blank=False, null=True, verbose_name='Subdistrito')
    class Meta:
        verbose_name = 'Persona en subdistrito'
        verbose_name_plural = 'Persona en subdistrito'

    def __str__(self):
        return "%s  %s" % (self.persona, self.subdistrito)


class SegInternaLocal(models.Model):
    local = models.ForeignKey(Local, related_name='local_seguridad_interna',
                              on_delete=models.PROTECT, blank=False, null=True)
    jefe_local = models.OneToOneField(Persona, null=True, blank=False, on_delete=models.PROTECT,
                                      verbose_name="Jefe de Local", related_name='jefe_local')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Seguridad interna en local - Jefe local'
        verbose_name_plural = 'Seguridad interna en local - Jefe local'

    def __str__(self):
        return "%s %s" % (self.local, self.jefe_local.NombreCompleto())


auditlog.register(SegInternaLocal)


class AuxiliarLocal(models.Model):
    seg_interna_local = models.ForeignKey(SegInternaLocal, related_name='aux_interna_del_local',
                                          on_delete=models.PROTECT, blank=False, null=True)
    auxiliar = models.OneToOneField(Persona, null=True, blank=False, on_delete=models.PROTECT,
                                    verbose_name="Auxiliar del Local", related_name='aux_local')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Seguridad interna en local - Auxiliares'
        verbose_name_plural = 'Seguridad interna en local - Auxiliares'

    def __str__(self):
        return "%s %s" % (self.seg_interna_local, self.auxiliar.NombreCompleto())


auditlog.register(AuxiliarLocal)


class Unidad(models.Model):
    nombre = CamposEnMayusculas(max_length=150, blank=False, null=False)
    abreviatura = CamposEnMayusculas(max_length=50, blank=False, null=False)

    class Meta:
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'

    def toJSON(self):
        item = model_to_dict(self)
        return item

    def __str__(self):
        return self.nombre


class Medios(models.Model):
    medios_transporte = CamposEnMayusculas(max_length=30, blank=False, null=False)

    class Meta:
        verbose_name = 'Medio de transporte'
        verbose_name_plural = 'Medios de transporte'

    def __str__(self):
        return self.medios_transporte


class TipoVehiculoProvisto(models.Model):
    medio = models.ForeignKey('Medios', related_name='medios_tipo_de_vehiculo_provisto',
                              on_delete=models.PROTECT, verbose_name="Medio", blank=False, null=True)
    tipo_vehiculo_provisto = CamposEnMayusculas(
        max_length=50, blank=False, null=False, verbose_name='Tipo de vehículo propio: ')

    class Meta:
        verbose_name = 'Tipo de vehículo propio'
        verbose_name_plural = 'Tipo de vehículo provisto'

    def __str__(self):
        return self.tipo_vehiculo_provisto


class Tareas(models.Model):
    tareas = CamposEnMayusculas(max_length=50, blank=False, null=False)

    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'

    def __str__(self):
        return self.tareas


auditlog.register(Tareas)


class TipoCombustible(models.Model):
    tipo_combustible = CamposEnMayusculas(
        max_length=30, blank=False, null=False, verbose_name='Tipo de Combustible: ')

    class Meta:
        verbose_name = 'Tipo de combustible'
        verbose_name_plural = 'Tipos de combustible'

    def __str__(self):
        return self.tipo_combustible


class VehiculosPropios(models.Model):
    TRONCAL = (
        (1, 'Primaria'),
        (2, 'Secundaria'),
        (3, 'Ninguna')
    )
    distrito = models.ForeignKey(Distrito, related_name='distrito_veh_propios', on_delete=models.PROTECT, blank=False,
                                 null=True)

    unidad = models.ForeignKey('Unidad', related_name='unidad_a_la_que_pertenece_el_vehiculo',
                               on_delete=models.PROTECT, blank=False, null=False,
                               help_text='Filtra a medida que escribe', verbose_name='Unidad que provee el vehículo')
    tipo_vehiculo_provisto = models.ForeignKey('TipoVehiculoProvisto', related_name='tipo_de_vehiculo_provisto',
                                               on_delete=models.PROTECT, verbose_name="Vehículo", blank=False,
                                               null=True)
    ni_patente_matricula = CamposEnMayusculas(max_length=20, blank=False, null=False, verbose_name="Indentificacion",
                                              help_text='Para Medio Terrestre: NI y Patente, Para Médio Aéreo, Marítimo o Fluvial: Nro de Matrícula o Identificación')
    consumo_en_litros_horas_voladas = models.FloatField(blank=False, null=False, verbose_name="Total del consumo",
                                                        help_text='Terrestre->Listros de combustible, Aéreos->Cantidad de horas voladas, Marítimo o Fluvial->Cantidad de Horas navegadas y Mulas/Caballos->kilos de alfalfa',
                                                        validators=[MinValueValidator(1)])
    tipo_combustible = models.ForeignKey('TipoCombustible', related_name='tipo_de_combustible',
                                         on_delete=models.PROTECT, verbose_name='Tipo de combustible', blank=False,
                                         null=False)
    tiene_destino = models.BooleanField(
        verbose_name='Tiene destino?', blank=False, null=False, default=False)
    cantidad_empleos = models.IntegerField(blank=True, null=True, verbose_name='Veces empleado', default=0)
    posee_sensor_rastreo = models.BooleanField(verbose_name='Posee sensor de rastreo (Spot/Celular)', blank=False,
                                               null=True)
    troncal = models.IntegerField(choices=TRONCAL, verbose_name='Se usa como troncal', blank=False, null=True,
                                  )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'Vehículo propio'
        verbose_name_plural = 'Vehículos propios'

    def __str__(self):
        return "%s Vehículo: %s Unidad: %s" % (
            self.ni_patente_matricula, self.tipo_vehiculo_provisto.tipo_vehiculo_provisto, self.unidad.nombre)


auditlog.register(VehiculosPropios)


class TipoVehiculoCivil(models.Model):
    medio = models.ForeignKey('Medios', related_name='medios_tipo_de_vehiculo_civil',
                              on_delete=models.PROTECT, verbose_name="Medio", blank=False, null=True)
    tipo_vehiculo_civil = CamposEnMayusculas(
        max_length=50, blank=False, null=False, verbose_name='Tipo de vehículo civil: ')

    class Meta:
        verbose_name = 'Tipo de vehículo civil'
        verbose_name_plural = 'Tipo de vehículo civil'

    def __str__(self):
        return self.tipo_vehiculo_civil


class VehiculosContratados(models.Model):
    TRONCAL = (
        (1, 'Primaria'),
        (2, 'Secundaria'),
        (3, 'Ninguna')
    )
    distrito = models.ForeignKey(Distrito, related_name='distrito_veh_contratado', on_delete=models.PROTECT,
                                 blank=False,
                                 null=True)
    tipo_vehiculo_contratado = models.ForeignKey('TipoVehiculoCivil', related_name='tipo_de_vehiculo_contratado',
                                                 on_delete=models.PROTECT, verbose_name="Vehículo", blank=False,
                                                 null=True)
    patente_matricula = CamposEnMayusculas(max_length=20, blank=False, null=True, verbose_name="Patente")

    tiene_destino = models.BooleanField(verbose_name='Tiene destino?', blank=False, null=False, default=False)
    posee_sensor_rastreo = models.BooleanField(verbose_name='Posee sensor de rastreo (Spot/Celular)', blank=False,
                                               null=True)
    troncal = models.IntegerField(choices=TRONCAL, verbose_name='Se usa como troncal', blank=False, null=True,
                                  )
    cantidad_empleos = models.IntegerField(blank=True, null=True, verbose_name='Veces empleado', default=0)
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'Vehículo contratado'
        verbose_name_plural = 'Vehículos contratados'

    def __str__(self):
        return '%s Patente: %s ' % (self.tipo_vehiculo_contratado.tipo_vehiculo_civil, self.patente_matricula)


auditlog.register(VehiculosContratados)


class NovedadesGenerales(models.Model):
    SUBSANADA_NOV_GRL = (
        ('Si', 'Si'),
        ('No', 'No')
    )
    distrito = models.ForeignKey(Distrito, related_name='distrito_nov', on_delete=models.PROTECT, blank=False,
                                 null=True)
    fecha = models.DateTimeField(verbose_name='Fecha y hora', blank=False, null=True,
                                 validators=[validar_fecha_en_el_futuro])
    tipo = models.ForeignKey(TipoNovedadLocal, related_name='tipo_novedad_general',
                             on_delete=models.PROTECT, blank=False, null=True, verbose_name='Tipo de novedad')
    detalle = CamposEnMayusculas(max_length=150, blank=False, null=True,
                                 help_text="Detalle acotado de la novedad (Máximo 150 caracteres)")
    subsanada = models.CharField(max_length=2, choices=SUBSANADA_NOV_GRL,
                                 verbose_name='Se subsanó?', blank=False, null=True,
                                 help_text='En caso afirmativo, debe explicar como la subsanó')
    medidas_adoptadas = CamposEnMayusculas(max_length=50, blank=True, null=True, verbose_name='')
    ubicacion = modelogis.PointField(null=True, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'Novedades generales'
        verbose_name_plural = 'Novedades generales'
        permissions = (
            ("ver_novedades_generales_novedadesgenerales", "Ver novedades generales"),
        )

    def __str__(self):
        return "%s" % (self.tipo)


auditlog.register(NovedadesGenerales)


class TipoMovimiento(models.Model):
    tipo = CamposEnMayusculas(max_length=100, blank=False, null=True, verbose_name="Tipo de movimiento")

    class Meta:
        verbose_name = 'Tipo de movimiento'
        verbose_name_plural = 'Tipo de movimientos'

    def __str__(self):
        return self.tipo


class Movimientos(models.Model):
    distrito = models.ForeignKey(Distrito, related_name='mov_en_distrito',
                                 on_delete=models.PROTECT, null=True, blank=False, verbose_name='Distrito')
    tipo = models.ForeignKey(TipoMovimiento, related_name='tipo_mov',
                             on_delete=models.PROTECT, null=True, blank=False, verbose_name='Tipo de movimiento')
    efectivos = models.IntegerField(
        null=True, blank=False, verbose_name='Cantidad de efectivos empleados', validators=[MinValueValidator(1)])
    vehiculos = models.IntegerField(
        null=True, blank=False, verbose_name='Cantidad de vehículos empleados', validators=[MinValueValidator(1)])
    inicio = models.DateTimeField(blank=False, null=True,
                                  verbose_name="Fecha de inicio")
    fin = models.DateTimeField(
        blank=False, null=True, verbose_name="Fecha de fin")
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")
    lugar_desde = CamposEnMayusculas(max_length=100, blank=False, null=True, verbose_name="Desde", help_text='Localidad/Departamento donde inicia el movimiento')
    lugar_hasta = CamposEnMayusculas(max_length=100, blank=False, null=True, verbose_name="Hasta", help_text='Localidad/Departamento donde termina el movimiento')
    distancia = models.IntegerField(
        null=True, blank=False, verbose_name='Distancia', validators=[MinValueValidator(1)], help_text='En kilómetros')

    def __str__(self):
        return self.tipo.tipo

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'


auditlog.register(Movimientos)


class TipoLed(models.Model):
    tipo = CamposEnMayusculas(max_length=20, blank=False, null=True, verbose_name="Tipo de LED")

    class Meta:
        verbose_name = 'Tipo de LED'
        verbose_name_plural = 'Tipo de LED'

    def __str__(self):
        return self.tipo


class Led(models.Model):
    distrito = models.ForeignKey(Distrito, related_name='distrito_led',
                                 on_delete=models.PROTECT, blank=False, null=True, verbose_name='Distrito')
    direccion = CamposEnMayusculas(max_length=100, blank=False, null=True, verbose_name="Dirección")
    ubicacion = modelogis.PointField(null=True, blank=False)
    tipo = models.ForeignKey(TipoLed, related_name='tipo_led',
                             on_delete=models.PROTECT, blank=False, null=True, verbose_name='Tipo de LED')
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones',
                             help_text='Otro dato de interés. Por defecto Sin novedad.',
                             default='Sin novedad')
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")

    def __str__(self):
        return "LED de %s (tipo: %s)" % (self.distrito, self.tipo.tipo)

    class Meta:
        verbose_name = 'LED'
        verbose_name_plural = 'LED'


auditlog.register(Led)


class SegEnLedFuerzaArmada(models.Model):
    led = models.ForeignKey(Led, related_name='led_seg_ffaa',
                            on_delete=models.PROTECT, blank=False, null=True)
    fecha_inicio = models.DateTimeField(
        verbose_name='Fecha de inicio', blank=False, null=True)
    fecha_fin = models.DateTimeField(
        verbose_name='Fecha de fin', blank=False, null=True)
    fuerza_armada = models.ForeignKey(Fuerza, related_name='fuerza_a_la_que_pertenece_seg_led',
                                      on_delete=models.PROTECT, blank=False, null=True)
    cant_personal = models.IntegerField(
        blank=True, null=True, verbose_name='Cantidad de personal', validators=[MinValueValidator(1)])
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")

    def __str__(self):
        return "Seg en el LED del %s " % (self.fuerza_armada)

    class Meta:
        verbose_name = 'Fuerzas Armadas en custodia en LED'
        verbose_name_plural = 'Fuerzas Armadas en custodia en LED'


auditlog.register(SegEnLedFuerzaArmada)


class SegEnLedFuerzaSeguridad(models.Model):
    led = models.ForeignKey(Led, related_name='led_seg_ffseg',
                            on_delete=models.PROTECT, blank=False, null=True)
    fecha_inicio = models.DateTimeField(
        verbose_name='Fecha de inicio', blank=False, null=True)
    fecha_fin = models.DateTimeField(
        verbose_name='Fecha de fin', blank=False, null=True)
    fuerza_seguridad = models.ForeignKey(FuerzaSeguridad, related_name='fuerza_seg_a_la_que_pertenece_seg_led',
                                         on_delete=models.PROTECT, blank=False, null=True)
    cant_personal = models.IntegerField(
        blank=False, null=True, verbose_name='Cantidad de personal', validators=[MinValueValidator(1)])
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'Fuerzas de Seguridad en custodia en LED'
        verbose_name_plural = 'Fuerzas de Seguridad en custodia en LED'

    def __str__(self):
        return "Seg en el LED del %s " % (self.fuerza_seguridad)


auditlog.register(SegEnLedFuerzaSeguridad)


class Cargo(models.Model):
    cargo = CamposEnMayusculas(max_length=50, blank=False, null=True)
    guia = models.BooleanField(verbose_name='Se usa en la guia', blank=False, null=True)
    prioridad = models.IntegerField(verbose_name='Prioridad', blank=False, null=True, unique=True)

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'

    def __str__(self):
        return self.cargo


class DistribucionPersonalCdoGrlElect(models.Model):
    cge = models.ForeignKey(CdoGrlElect, related_name='distribucion_personal_en_cdogrlelect',
                            on_delete=models.PROTECT, null=True, blank=False)
    cargo = models.ForeignKey(Cargo, related_name='cargo_en_el_cdogrlelect',
                              on_delete=models.PROTECT, blank=False, null=True)
    designacion = CamposEnMayusculas(max_length=50, blank=False,
                                     null=True, default='---',
                                     help_text='Agregar donde desempeña el cargo (si corresponde), Ejemplo: Div Fin, Op(s)',
                                     verbose_name="Aclaraciones sobre el cargo que ocupa - No obligatorio")
    integrante = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Personal", related_name='cge_persona')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, )

    class Meta:
        verbose_name = 'Distribución de personal en el Cdo Grl Elect'
        verbose_name_plural = 'Distribución de personal en el Cdo Grl Elect'

    def __str__(self):
        return "%s  %s %s" % (self.integrante.NombreCompleto(), self.cargo, self.designacion)


auditlog.register(DistribucionPersonalCdoGrlElect)


class ReservaCdoGrlElect(models.Model):
    cge = models.ForeignKey(CdoGrlElect, related_name='reserva_en_cdogrlelect',
                            on_delete=models.PROTECT, null=True, blank=False)
    integrante = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Personal",
        related_name='reserva_cge_persona')
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones',
                             help_text='Cualquier otro dato de interés que se desee aclarar.', default='---')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, )

    class Meta:
        verbose_name = 'Reserva en el Cdo Grl Elect'
        verbose_name_plural = 'Reserva en el Cdo Grl Elect'

    def __str__(self):
        return "%s reserva en el Cdo Grl Elect" % (self.integrante.NombreCompleto())


auditlog.register(ReservaCdoGrlElect)


class VehiculosPropiosCdoGrlElect(models.Model):
    cge = models.ForeignKey(CdoGrlElect, related_name='veh_propios_en_cdogrlelect',
                            on_delete=models.PROTECT, null=True, blank=False)
    veh_propio = models.ForeignKey(
        VehiculosPropios, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Vehículo",
        related_name='veh_propio_cge')
    conductor = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Conductor",
        related_name='veh_pro_cge_persona')

    desde = models.DateField(blank=False, null=True, verbose_name="Desde")
    hasta = models.DateField(blank=False, null=True, verbose_name="Hasta")
    tareas = models.ForeignKey('Tareas', related_name='tareas_para_vehiculos_propios1',
                               on_delete=models.PROTECT, blank=False, null=True)
    zona_trabajo = CamposEnMayusculas(
        max_length=50, blank=False, null=True, verbose_name="Zona de trabajo")

    kilometros_a_recorrer = models.FloatField(blank=False, null=True, verbose_name="Distancia",
                                              validators=[MinValueValidator(1)])
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones', default='Sin novedad')

    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Vehículos Propios en el Cdo Grl Elect'
        verbose_name_plural = 'Vehículos Propios en el Cdo Grl Elect'

    def __str__(self):
        return "%s conductor en el Cdo Grl Elect" % (self.veh_propio)


auditlog.register(VehiculosPropiosCdoGrlElect)


class VehiculosContratadosCdoGrlElect(models.Model):
    cge = models.ForeignKey(CdoGrlElect, related_name='veh_contratados_en_cdogrlelect',
                            on_delete=models.PROTECT, null=True, blank=False)
    vehiculo_contratado = models.ForeignKey('VehiculosContratados', related_name='vehiculo_contratado_cge',
                                            on_delete=models.PROTECT, verbose_name="Vehículo", blank=False, null=True)
    cantidad_pasajeros = models.IntegerField(
        blank=False, null=True, verbose_name="Cantidad de pasajeros", validators=[MinValueValidator(1)])
    tareas = models.ForeignKey('Tareas', related_name='tareas_para_vehiculos_contratados1',
                               on_delete=models.PROTECT, blank=False, null=True)
    zona_trabajo = CamposEnMayusculas(
        max_length=50, blank=False, null=True, verbose_name="Zona de trabajo")
    desde = models.DateField(blank=False, null=True)
    hasta = models.DateField(blank=False, null=True)
    kilometros_a_recorrer = models.FloatField(blank=False, null=True, verbose_name="Distancia",
                                              validators=[MinValueValidator(1)])
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones', default='Sin novedad')
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")
    responsable = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Responsable",
        related_name='veh_con_cge_persona')

    class Meta:
        verbose_name = 'Vehículo contratados Cdo Grl Elect'

    def __str__(self):
        return self.vehiculo_contratado.tipo_vehiculo_contratado.tipo_vehiculo_civil


auditlog.register(VehiculosContratadosCdoGrlElect)


class DistribucionPersonalDistrito(models.Model):
    distrito = models.ForeignKey(Distrito, related_name='distribucion_personal_en_distrito',
                                 on_delete=models.PROTECT, null=True, blank=False, verbose_name='Distrito')
    cargo = models.ForeignKey(Cargo, related_name='cargo_en_el_distrito',
                              on_delete=models.PROTECT, blank=False, null=True)
    designacion = CamposEnMayusculas(max_length=50, blank=False,
                                     null=True, default='---',
                                     help_text='Agregar donde desempeña el cargo (si corresponde), Ejemplo: Div Fin, Op(s)',
                                     verbose_name="Aclaraciones sobre el cargo que ocupa - No obligatorio")
    integrante = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Personal",
        related_name='distrito_persona')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Distribución de personal en el Distrito'
        verbose_name_plural = 'Distribución de personal en el Distrito'

    def __str__(self):
        return "%s  %s en distrito %s" % (self.integrante.NombreCompleto(), self.cargo, self.distrito.distrito)


auditlog.register(DistribucionPersonalDistrito)


class ReservaDistrito(models.Model):
    distrito = models.ForeignKey(Distrito, related_name='reserva_en_distrito',
                                 on_delete=models.PROTECT, null=True, blank=False)
    integrante = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Personal",
        related_name='res_dis_personal')
    obs = CamposEnMayusculas(max_length=50, blank=True, null=False, verbose_name='Obsrvaciones',
                             help_text='Cualquier otro dato de interés que se desee aclarar.', default='---')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Reserva en el Distrito'
        verbose_name_plural = 'Reserva en el Distrito'

    def __str__(self):
        return "%s esta de reserva en el distrito %s" % (self.integrante.NombreCompleto(), self.distrito.distrito)


auditlog.register(ReservaDistrito)


class VehiculosPropiosDistrito(models.Model):
    distrito = models.ForeignKey(Distrito, related_name='veh_propios_en_distritos',
                                 on_delete=models.PROTECT, null=True, blank=False)
    veh_propio = models.ForeignKey(
        VehiculosPropios, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Vehículo",
        related_name='veh_propio_distrito')
    conductor = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Conductor",
        related_name='veh_pro_dis_persona')

    desde = models.DateField(blank=False, null=True, verbose_name="Desde")
    hasta = models.DateField(blank=False, null=True, verbose_name="Hasta")
    tareas = models.ForeignKey('Tareas', related_name='tareas_para_vehiculos_propios_distrito',
                               on_delete=models.PROTECT, blank=False, null=True)
    zona_trabajo = CamposEnMayusculas(
        max_length=50, blank=False, null=True, verbose_name="Zona de trabajo")

    kilometros_a_recorrer = models.FloatField(blank=False, null=True, verbose_name="Distancia",
                                              validators=[MinValueValidator(1)])
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones', default='Sin novedad')

    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Vehículos Propios en el Distrito'
        verbose_name_plural = 'Vehículos Propios en el Distrito'

    def __str__(self):
        return "%s asignado en el Distrito %s" % (self.veh_propio, self.distrito)


auditlog.register(VehiculosPropiosDistrito)


class VehiculosContratadosDistrito(models.Model):
    distrito = models.ForeignKey(Distrito, related_name='veh_contratados_en_distritos',
                                 on_delete=models.PROTECT, null=True, blank=False)
    vehiculo_contratado = models.ForeignKey('VehiculosContratados', related_name='vehiculo_contratado_distrito',
                                            on_delete=models.PROTECT, verbose_name="Vehículo", blank=False, null=True)
    cantidad_pasajeros = models.IntegerField(
        blank=False, null=True, verbose_name="Cantidad de pasajeros", validators=[MinValueValidator(1)])
    tareas = models.ForeignKey('Tareas', related_name='tareas_para_vehiculos_contratados_distrito',
                               on_delete=models.PROTECT, blank=False, null=True)
    zona_trabajo = CamposEnMayusculas(
        max_length=50, blank=False, null=True, verbose_name="Zona de trabajo")
    desde = models.DateField(blank=False, null=True)
    hasta = models.DateField(blank=False, null=True)
    kilometros_a_recorrer = models.FloatField(blank=False, null=True, verbose_name="Distancia",
                                              validators=[MinValueValidator(1)])
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones', default='Sin novedad')
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")
    responsable = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Responsable",
        related_name='veh_con_dis_personal')

    class Meta:
        verbose_name = 'Vehículos Contratados en el Distrito'
        verbose_name_plural = 'Vehículos Contratados en el Distrito'

    def __str__(self):
        return "%s asignado en Distrito %s" % (
            self.vehiculo_contratado.tipo_vehiculo_contratado.tipo_vehiculo_civil, self.distrito)


auditlog.register(VehiculosContratadosDistrito)


class DistribucionPersonalSubdistrito(models.Model):
    subdistrito = models.ForeignKey(Subdistrito, related_name='distribucion_personal_en_subdistrito',
                                    on_delete=models.PROTECT, null=True, blank=False, verbose_name='Subdistrito')
    cargo = models.ForeignKey(Cargo, related_name='cargo_en_el_subdistrito',
                              on_delete=models.PROTECT, blank=False, null=True)
    designacion = CamposEnMayusculas(max_length=50, blank=False,
                                     null=True, default='---',
                                     help_text='Agregar donde desempeña el cargo (si corresponde), Ejemplo: Div Fin, Op(s)',
                                     verbose_name="Aclaraciones sobre el cargo que ocupa - No obligatorio")
    integrante = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Personal", related_name='sub_personal')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Distribución de personal en el Subdistrito'
        verbose_name_plural = 'Distribución de personal en el Subdistrito'

    def __str__(self):
        return "%s  %s en subdistrito %s" % (self.integrante.NombreCompleto(), self.cargo, self.subdistrito.subdistrito)


auditlog.register(DistribucionPersonalSubdistrito)


class ReservaSubdistrito(models.Model):
    subdistrito = models.ForeignKey(Subdistrito, related_name='reserva_en_subdistrito',
                                    on_delete=models.PROTECT, null=True, blank=False)
    integrante = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Personal",
        related_name='res_sub_personal')
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones',
                             help_text='Cualquier otro dato de interés que se desee aclarar.', default='---')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Reserva en el Subdistrito'
        verbose_name_plural = 'Reserva en el Subdistrito'

    def __str__(self):
        return "%s esta de reserva en el subdistrito %s" % (
            self.integrante.NombreCompleto(), self.subdistrito.subdistrito)


auditlog.register(ReservaSubdistrito)


class VehiculosPropiosSubdistrito(models.Model):
    subdistrito = models.ForeignKey(Subdistrito, related_name='veh_propios_en_subdistritos',
                                    on_delete=models.PROTECT, null=True, blank=False)
    veh_propio = models.ForeignKey(
        VehiculosPropios, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Vehículo",
        related_name='veh_prop_sub')
    conductor = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Conductor",
        related_name='veh_pro_sub_persona')
    desde = models.DateField(blank=False, null=True, verbose_name="Desde")
    hasta = models.DateField(blank=False, null=True, verbose_name="Hasta")
    tareas = models.ForeignKey('Tareas', related_name='tareas_para_vehiculos_propios_subdistrito',

                               on_delete=models.PROTECT, blank=False, null=True)
    zona_trabajo = CamposEnMayusculas(
        max_length=50, blank=False, null=True, verbose_name="Zona de trabajo")

    kilometros_a_recorrer = models.FloatField(blank=False, null=True, verbose_name="Distancia",
                                              validators=[MinValueValidator(1)])
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones', default='Sin novedad')

    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Vehículos Propios en el Subistrito'
        verbose_name_plural = 'Vehículos Propios en el Subdistrito'

    def __str__(self):
        return "%s asignado en el Subdistrito %s" % (self.veh_propio, self.subdistrito)


auditlog.register(VehiculosPropiosSubdistrito)


class VehiculosContratadosSubdistrito(models.Model):
    subdistrito = models.ForeignKey(Subdistrito, related_name='veh_contratados_en_subdistritos',
                                    on_delete=models.PROTECT, null=True, blank=False)
    vehiculo_contratado = models.ForeignKey('VehiculosContratados', related_name='vehiculo_contratado_subdistrito',
                                            on_delete=models.PROTECT, verbose_name="Vehículo", blank=False, null=True)
    cantidad_pasajeros = models.IntegerField(
        blank=False, null=True, verbose_name="Cantidad de pasajeros", validators=[MinValueValidator(1)])
    tareas = models.ForeignKey('Tareas', related_name='tareas_para_vehiculos_contratados_subdistrito',
                               on_delete=models.PROTECT, blank=False, null=True)
    zona_trabajo = CamposEnMayusculas(
        max_length=50, blank=False, null=True, verbose_name="Zona de trabajo")
    desde = models.DateField(blank=False, null=True)
    hasta = models.DateField(blank=False, null=True)
    kilometros_a_recorrer = models.FloatField(blank=False, null=True, verbose_name="Distancia",
                                              validators=[MinValueValidator(1)])
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones', default='Sin novedad')
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Creado el día")
    responsable = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Responsable",
        related_name='veh_con_sub_personal')

    class Meta:
        verbose_name = 'Vehículos Contratados en el Subdistrito'
        verbose_name_plural = 'Vehículos Contratados en el Subdistrito'

    def __str__(self):
        return "%s asignado en el Subdistrito %s" % (
            self.vehiculo_contratado.tipo_vehiculo_contratado.tipo_vehiculo_civil, self.subdistrito)


auditlog.register(VehiculosContratadosSubdistrito)


class DistribucionPersonalSeccion(models.Model):
    seccion = models.ForeignKey(Seccion, related_name='seccion_organizacion',
                                on_delete=models.PROTECT, null=True, blank=False, verbose_name='Sección')
    cargo = models.ForeignKey(Cargo, related_name='cargo_en_la_seccion',
                              on_delete=models.PROTECT, blank=False, null=True)
    designacion = CamposEnMayusculas(max_length=50, blank=True,
                                     null=True, default='---',
                                     help_text='Agregar donde desempeña el cargo (si corresponde), Ejemplo: Div Fin, Op(s)',
                                     verbose_name="Aclaraciones sobre el cargo que ocupa - No obligatorio")
    integrante = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Personal", related_name='sec_personal')

    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Distribución de personal en la Sección'
        verbose_name_plural = 'Distribución de personal en la Sección'

    def __str__(self):
        return "%s %s" % (self.cargo, self.integrante)


auditlog.register(DistribucionPersonalSeccion)


class VehiculosPropiosSeccion(models.Model):
    seccion = models.ForeignKey(Seccion, related_name='veh_propios_en_seccion',
                                on_delete=models.PROTECT, null=True, blank=False)
    veh_propio = models.ForeignKey(
        VehiculosPropios, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Vehículo",
        related_name='veh_prop_sec')
    conductor = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Conductor",
        related_name='veh_prop_personal_sec')

    desde = models.DateField(blank=False, null=True, verbose_name="Desde")
    hasta = models.DateField(blank=False, null=True, verbose_name="Hasta")
    tareas = models.ForeignKey('Tareas', related_name='tareas_para_veh_propios_seccion',
                               on_delete=models.PROTECT, blank=False, null=True)
    zona_trabajo = CamposEnMayusculas(
        max_length=50, blank=False, null=True, verbose_name="Zona de trabajo")

    kilometros_a_recorrer = models.FloatField(blank=False, null=True, verbose_name="Distancia",
                                              validators=[MinValueValidator(1)])
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones', default='Sin novedad')

    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Vehículos Propios en la Sección'
        verbose_name_plural = 'Vehículos Propios en la Sección'

    def __str__(self):
        return "%s asignado en la Sección %s" % (self.veh_propio, self.seccion)


auditlog.register(VehiculosPropiosSeccion)


class VehiculosContratadosSeccion(models.Model):
    seccion = models.ForeignKey(Seccion, related_name='veh_contratados_en_seccion',
                                on_delete=models.PROTECT, null=True, blank=False)
    vehiculo_contratado = models.ForeignKey('VehiculosContratados', related_name='vehiculo_contratado_seccion',
                                            on_delete=models.PROTECT, verbose_name="Vehículo", blank=False, null=True)
    cantidad_pasajeros = models.IntegerField(
        blank=False, null=True, verbose_name="Cantidad de pasajeros", validators=[MinValueValidator(1)])
    tareas = models.ForeignKey('Tareas', related_name='tareas_para_vehiculos_contratados_seccion',
                               on_delete=models.PROTECT, blank=False, null=True)
    zona_trabajo = CamposEnMayusculas(
        max_length=50, blank=False, null=True, verbose_name="Zona de trabajo")
    desde = models.DateField(blank=False, null=True)
    hasta = models.DateField(blank=False, null=True)
    kilometros_a_recorrer = models.FloatField(blank=False, null=True, verbose_name="Distancia",
                                              validators=[MinValueValidator(1)])
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones', default='Sin novedad')
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=False, verbose_name="Creado el día")
    responsable = models.ForeignKey(
        Persona, null=True, blank=False, on_delete=models.PROTECT, verbose_name="Responsable",
        related_name='veh_cont_personal_sec')

    class Meta:
        verbose_name = 'Vehículos Contratados en la Sección'
        verbose_name_plural = 'Vehículos Contratados en la Sección'

    def __str__(self):
        return "%s asignado en la Sección %s" % (
            self.vehiculo_contratado.tipo_vehiculo_contratado.tipo_vehiculo_civil, self.seccion)


auditlog.register(VehiculosContratadosSeccion)


class SACASPuntosRecoleccion(models.Model):
    distrito = models.ForeignKey(Distrito, related_name='distrito_punto_recoleccion_sacas',
                                 on_delete=models.PROTECT, blank=False, null=True, verbose_name='Distrito')
    direccion = CamposEnMayusculas(max_length=100, blank=False, null=True, verbose_name="Dirección")

    denominacion_puesto = CamposEnMayusculas(max_length=100, blank=False, null=True, unique=True,
                                             verbose_name="Punto de recolección",
                                             help_text='Denominación del Punto de recolección / Punto de control')

    ubicacion = modelogis.PointField(null=True, blank=False)

    cant_sacas = models.IntegerField(blank=False, null=True, verbose_name='Cantidad de SACAS',
                                     validators=[MinValueValidator(1)],
                                     help_text='Cantidad de SACAS a transportar')
    cant_uupp = models.IntegerField(blank=False, null=True, verbose_name='Cantidad de Un(s) Penitenciarias',
                                    help_text='Cantidad de Unidades Penitenciarios')
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=False, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'SACAS - Puntos de recolección'
        verbose_name_plural = 'SACAS - Puntos de recolección'

    def __str__(self):
        return self.denominacion_puesto


auditlog.register(SACASPuntosRecoleccion)


class SACASHistorialPuntosRecoleccion(models.Model):
    ESTADOS = (
        (0, 'NO ENTREGADO'),
        (1, 'ENTREGADO'),
    )
    prs = models.ForeignKey(SACASPuntosRecoleccion, related_name='estado_prs',
                            on_delete=models.PROTECT, blank=False, null=True,
                            verbose_name='Puntos de recolección')
    estado = models.IntegerField(choices=ESTADOS, blank=False, null=True, verbose_name='Estado')

    fecha = models.DateTimeField(
        verbose_name='Fecha y hora', blank=False, null=True, validators=[validar_fecha_en_el_futuro])

    class Meta:
        verbose_name = 'SACAS - Historial de estados Puntos de Recolección'
        verbose_name_plural = 'SACAS - Historial de estados Puntos de Recolección'

    def __str__(self):
        return str(self.get_estado_display())


auditlog.register(SACASHistorialPuntosRecoleccion)


class SACACircuitoRecoleccion(models.Model):
    distrito = models.ForeignKey(Distrito, related_name='distrito_ctrs',
                                 on_delete=models.PROTECT, blank=False, null=False, verbose_name='Distrito')
    ctrs = CamposEnMayusculas(max_length=20, blank=False, null=True, verbose_name="Circuito",
                              help_text='Nombre del circuito de recolección')
    cant_personal = models.IntegerField(blank=False, null=True, verbose_name='Personal',
                                        validators=[MinValueValidator(1)],
                                        help_text='Cantidad de personal que integra la comisión')
    vehiculo = CamposEnMayusculas(
        max_length=100, blank=False, null=True, verbose_name="Vehículo",
        help_text='Datos del vehículo que integra la comisión')
    prs = models.ManyToManyField(
        SACASPuntosRecoleccion, blank=False, through='Circuito_Punto',
        help_text='Puntos de Recolección que integran este Circuito de Recolección')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=False, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'SACAS - Circuitos de recolección'
        verbose_name_plural = 'SACAS - Circuitos de recolección'

    def __str__(self):
        return "Circuito: %s" % (self.ctrs)


auditlog.register(SACACircuitoRecoleccion)


class SACASHistorialCircuitosRecoleccion(models.Model):
    ESTADOS = (
        (0, 'RECEPCIÓN SACAS EN PPRS'),
        (1, 'ENTREGÓ SACAS EN LA CNE'),
        (2, 'INICIÓ REPLIEGUE'),
        (3, 'REPLEGADO'),

    )
    crs = models.ForeignKey(SACACircuitoRecoleccion, related_name='estado_crs',
                            on_delete=models.PROTECT, blank=False, null=True,
                            verbose_name='Circuito recolección')
    estado = models.IntegerField(choices=ESTADOS, blank=False, null=True, verbose_name='Estado')

    fecha = models.DateTimeField(
        verbose_name='Fecha y hora', blank=False, null=True, validators=[validar_fecha_en_el_futuro])

    class Meta:
        verbose_name = 'SACAS - Historial de estados Circuitos de Recolección'
        verbose_name_plural = 'SACAS - Historial de estados Circuitos de Recolección'

    def __str__(self):
        return str(self.get_estado_display())


auditlog.register(SACASHistorialCircuitosRecoleccion)


class Circuito_Punto(models.Model):
    circuito = models.ForeignKey(SACACircuitoRecoleccion, related_name='circuito',
                                 on_delete=models.CASCADE, verbose_name='Circuito recolección',
                                 blank=False, null=True)
    punto = models.ForeignKey(SACASPuntosRecoleccion, related_name='punto',
                              on_delete=models.CASCADE, verbose_name='Punto recolección',
                              blank=False, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=False, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'SACAS - Circuitos_Puntos'
        verbose_name_plural = 'SACAS - Circuitos_Puntos'

    def __str__(self):
        return "%s - %s" % (self.circuito, self.punto)


class Sed(models.Model):
    distrito = models.ForeignKey(Distrito, related_name='distrito_sed',
                                 on_delete=models.PROTECT, blank=False, null=True, verbose_name='Distrito')
    direccion = CamposEnMayusculas(max_length=100, blank=False, null=True, verbose_name="Dirección")

    sed = CamposEnMayusculas(max_length=50, blank=False, null=True, unique=True,
                             verbose_name="SED", )
    localidad = CamposEnMayusculas(max_length=80, blank=False, null=True, unique=True, verbose_name="Localidad")

    ubicacion = modelogis.PointField(null=True, blank=False)
    telefono = models.CharField(max_length=30, validators=[validar_te], null=True, blank=True,
                                verbose_name='Tel responsable')

    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=False, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'SED - Sucursal Electoral Digital'
        verbose_name_plural = 'SED - Sucursales Electorales Digitales'

    def __str__(self):
        return "%s - %s" % (self.sed, self.distrito)

class TipoLugarInteres(models.Model):
    CLASE = (
        (0, 'Se carga en COFFA'),
        (1, 'Se carga en distritos'),
    )
    tipo = CamposEnMayusculas(max_length=100, blank=False, null=True, verbose_name="Tipo de lugar de interés")
    clase = models.IntegerField(choices=CLASE, blank=False, null=True, verbose_name='Clase')

    class Meta:
        verbose_name = 'Tipo de lugar de interés'
        verbose_name_plural = 'Tipo de lugar de interés'

    def __str__(self):
        return "%s" % (self.tipo)

class LugarInteres(models.Model):
    distrito = models.ForeignKey(Distrito, related_name='distrito_lugar_interes',
                                 on_delete=models.PROTECT, blank=False, null=True, verbose_name='Distrito')
    direccion = CamposEnMayusculas(max_length=100, blank=False, null=True, verbose_name="Dirección")

    tipo_lugar = models.ForeignKey(TipoLugarInteres, related_name='lugar_interes',
                                 on_delete=models.PROTECT, blank=False, null=True, verbose_name='Lugar de interés')
    ubicacion = modelogis.PointField(null=True, blank=False)
    telefono = models.CharField(max_length=30, validators=[validar_te], null=True, blank=False,
                                verbose_name='Teléfono')
    autoridad = CamposEnMayusculas(max_length=100, blank=False, null=True, verbose_name="Autoridad")

    fecha_creacion = models.DateTimeField(
        auto_now_add=True, null=True, blank=False, verbose_name="Creado el día")
    obs = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name='Observaciones', default='Sin novedad')

    class Meta:
        verbose_name = 'Lugar de interés'
        verbose_name_plural = 'Lugar de interés'

    def __str__(self):
        return "%s - %s" % (self.tipo_lugar.tipo, self.direccion)

class GuiaAutoridades(models.Model):
    persona_guia = models.ForeignKey(Persona,  related_name='persona_guia',
                                 on_delete=models.PROTECT, blank=False, null=True, verbose_name='Persona')
    puesto_guia = models.ManyToManyField(Cargo, related_name='cargo_guia', blank=False, through='PuestoGuiaAutoridades',
                                         verbose_name='Cargo', help_text='Puede seleccionar mas de uno')
    puesto_texto = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name="Cargo mostrado en texto")
    org_texto = CamposEnMayusculas(max_length=50, blank=False, null=True, verbose_name="Organizacion mostrada en texto")
    org_control = models.CharField(max_length=50, blank=True, null=True, verbose_name="Filtro para el enlace")
    org_id = models.PositiveIntegerField(null=True, blank=False, verbose_name='Id de la organizacion')
    gde_guia = models.CharField(max_length=50, blank=False, null=True, verbose_name="GDE")
    tel_guia = models.CharField(max_length=30, validators=[validar_te], null=True, blank=False, verbose_name='Teléfono')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=False, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'Guia de autoridades'
        verbose_name_plural = 'Guia de autoridades'

    def __str__(self):
        return "%s gde: %s tel directo: %s" % (self.persona_guia, self.gde_guia, self.tel_guia)

class CgeGuia(models.Model):
    guia = models.ForeignKey(GuiaAutoridades, related_name="guia_guia", on_delete=models.PROTECT, blank=False, null=True, verbose_name='Guia de autoridades')
    cge = models.ForeignKey(CdoGrlElect, related_name="cge_guia", on_delete=models.PROTECT, blank=False, null=True, verbose_name='CGE')
    class Meta:
        verbose_name = 'Guia->CGE'
        verbose_name_plural = 'Guia->CGE'

    def __str__(self):
        return "%s  %s" % (self.guia, self.cge)

class DistritoGuia(models.Model):
    guia = models.ForeignKey(GuiaAutoridades, related_name="guia_guia_distrito", on_delete=models.PROTECT, blank=False, null=True, verbose_name='Guia de autoridades')
    dist = models.ForeignKey(Distrito, related_name="distrito_guia", on_delete=models.PROTECT, blank=False, null=True, verbose_name='Distrito')
    class Meta:
        verbose_name = 'Guia->Distrito'
        verbose_name_plural = 'Guia->Distrito'

    def __str__(self):
        return "%s  %s" % (self.guia, self.dist)

# Importante: Para crear una relación M2M a través de throwing primero crear el modelo GuiaAutoridades, luego PuestoGuiaAutoridades
# y finalmente agregar el throw al campo puesto_guia.
class PuestoGuiaAutoridades(models.Model):
    guia = models.ForeignKey(GuiaAutoridades, related_name="guia_puestoautoridades", on_delete=models.PROTECT, blank=False, null=True, verbose_name="Guia Autoridades")
    puesto = models.ForeignKey(Cargo, related_name="puesto_puestoautoridades", on_delete=models.PROTECT, blank=False, null=True, verbose_name="Puesto")
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=False, verbose_name="Creado el día")

    class Meta:
        verbose_name = 'Puesto<->Guia Autoridades (M2M)'
        verbose_name_plural = 'Puesto<->Guia Autoridades (M2M)'

    def __str__(self):
        return "%s %s" % (self.guia, self.puesto)


def remover_permisos_objeto_del_usuario(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
                object_pk=instance.pk)

    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()


def asignar_permisos(sender, instance, created, **kwargs):
    usuario = get_current_user()
    grupo = usuario.grupo_organizacion
    grupo_padre = grupo.get_ancestors()
    if created:
        [assign_perm(x + sender.__name__.lower(), grupo, instance) for x in ['view_', 'change_', 'delete_']]
        assign_perm('view_' + sender.__name__.lower(), grupo_padre, instance)
        if str(Group.objects.get(id=grupo.id)) == 'personal-CGE':
            [assign_perm(x + sender.__name__.lower(), Group.objects.get(name='material-CGE'), instance) for x in ['view_']]



def crear_grupo_adminsistema(sender, instance, **kwargs):
    grupo_admin_sistema, creado = Group.objects.get_or_create(name='adminsistema')

    permisos = ['view', 'add', 'delete', 'change']
    modelos = [Usuario, SACACircuitoRecoleccion, SACASPuntosRecoleccion,Distrito]
    for modelo in modelos:
        for permiso in permisos:
            grupo_admin_sistema.permissions.add(
                Permission.objects.get(content_type__model=modelo.__name__.lower(), name__contains=permiso))


# SACAS
def asignar_permisos_sacas(sender, instance, created, **kwargs):
    usuario = get_current_user()
    grupo = usuario.grupo_organizacion
    if created:
        [assign_perm(x + sender.__name__.lower(), grupo, instance) for x in ['view_', 'change_', 'delete_']]

def remover_permisos_objeto_sacas(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
                object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()


post_save.connect(asignar_permisos_sacas, sender=SACASPuntosRecoleccion)
pre_delete.connect(remover_permisos_objeto_sacas, sender=SACASPuntosRecoleccion)
post_save.connect(asignar_permisos_sacas, sender=SACACircuitoRecoleccion)
pre_delete.connect(remover_permisos_objeto_sacas, sender=SACACircuitoRecoleccion)


# Novedades generales
post_save.connect(asignar_permisos, sender=NovedadesGenerales)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=NovedadesGenerales)

# Led
post_save.connect(asignar_permisos, sender=Led)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=Led)

# Sed
post_save.connect(asignar_permisos, sender=Sed)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=Sed)

# Seguridad en los led de las FFAA
post_save.connect(asignar_permisos, sender=SegEnLedFuerzaArmada)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=SegEnLedFuerzaArmada)

# Seguridad en los led de las Fuerzas de seguridad
post_save.connect(asignar_permisos, sender=SegEnLedFuerzaSeguridad)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=SegEnLedFuerzaSeguridad)

# Movimientos
post_save.connect(asignar_permisos, sender=Movimientos)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=Movimientos)

# Vehículos contratados
post_save.connect(asignar_permisos, sender=VehiculosContratados)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=VehiculosContratados)

# Vehículos propios
post_save.connect(asignar_permisos, sender=VehiculosPropios)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=VehiculosPropios)

# Persona
post_save.connect(asignar_permisos, sender=Persona)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=Persona)

# Cdo Grl Electoral
post_save.connect(crear_grupo_adminsistema, sender=CdoGrlElect)

post_save.connect(asignar_permisos, sender=DistribucionPersonalCdoGrlElect)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=DistribucionPersonalCdoGrlElect)

post_save.connect(asignar_permisos, sender=ReservaCdoGrlElect)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=ReservaCdoGrlElect)

post_save.connect(asignar_permisos, sender=VehiculosPropiosCdoGrlElect)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=VehiculosPropiosCdoGrlElect)

post_save.connect(asignar_permisos, sender=VehiculosContratadosCdoGrlElect)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=VehiculosContratadosCdoGrlElect)

# Distritos
post_save.connect(asignar_permisos, sender=DistribucionPersonalDistrito)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=DistribucionPersonalDistrito)

post_save.connect(asignar_permisos, sender=ReservaDistrito)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=ReservaDistrito)

post_save.connect(asignar_permisos, sender=VehiculosPropiosDistrito)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=VehiculosPropiosDistrito)

post_save.connect(asignar_permisos, sender=VehiculosContratadosDistrito)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=VehiculosContratadosDistrito)

# Subdistritos
post_save.connect(asignar_permisos, sender=DistribucionPersonalSubdistrito)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=DistribucionPersonalSubdistrito)

post_save.connect(asignar_permisos, sender=ReservaSubdistrito)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=ReservaSubdistrito)

post_save.connect(asignar_permisos, sender=VehiculosPropiosSubdistrito)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=VehiculosPropiosSubdistrito)

post_save.connect(asignar_permisos, sender=VehiculosContratadosSubdistrito)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=VehiculosContratadosSubdistrito)

# Secciones
post_save.connect(asignar_permisos, sender=DistribucionPersonalSeccion)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=DistribucionPersonalSeccion)

post_save.connect(asignar_permisos, sender=VehiculosPropiosSeccion)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=VehiculosPropiosSeccion)

post_save.connect(asignar_permisos, sender=VehiculosContratadosSeccion)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=VehiculosContratadosSeccion)

# Circuitos
post_save.connect(asignar_permisos, sender=Circuito)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=Circuito)

# Locales
post_save.connect(asignar_permisos, sender=Local)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=Local)

post_save.connect(asignar_permisos, sender=SegInternaLocal)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=SegInternaLocal)

post_save.connect(asignar_permisos, sender=SegExternaLocal)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=SegExternaLocal)

post_save.connect(asignar_permisos, sender=NovedadesEnLocal)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=NovedadesEnLocal)

post_save.connect(asignar_permisos, sender=MesasEnLocal)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=MesasEnLocal)

# Lugares de interés
post_save.connect(asignar_permisos, sender=LugarInteres)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=LugarInteres)

# GuiaAutoridades
post_save.connect(asignar_permisos, sender=GuiaAutoridades)
pre_delete.connect(remover_permisos_objeto_del_usuario, sender=GuiaAutoridades)



####Modelo para consumir vistar materializadas de la bd

class exportarpersonal(models.Model):
    grado = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=50)
    nro_tel = models.CharField(max_length=50)
    fuerza = models.CharField(max_length=50)
    cargo = models.CharField(max_length=50)
    cge = models.CharField(max_length=50)
    distrito = models.CharField(max_length=50)
    subdistrito = models.CharField(max_length=50)
    seccion = models.CharField(max_length=50)
    circuito = models.CharField(max_length=10)
    nombre_local = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    localidad = models.CharField(max_length=50)
    reserva = models.CharField(max_length=50)
    seg_interna_local = models.CharField(max_length=50)
    latitud = models.CharField(max_length=50)
    longitud = models.CharField(max_length=50)
    tipo_armamento = models.CharField(max_length=50)
    nro_armamento = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'exportarpersonal'

class exportarlocales(models.Model):
    transmite_telegrama = models.CharField(max_length=50)
    estado_local = models.CharField(max_length=50)
    nro_mesas = models.CharField(max_length=50)
    cant_mesas = models.CharField(max_length=50)
    cant_electores = models.CharField(max_length=50)
    cant_seg_ext = models.CharField(max_length=50)
    cant_seg_interna = models.CharField(max_length=50)
    ubicacion =modelogis.PointField()
    distrito = models.CharField(max_length=50)
    subdistrito = models.CharField(max_length=50)
    seccion = models.CharField(max_length=50)
    circuito = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    localidad = models.CharField(max_length= 50)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'exportarlocales'
