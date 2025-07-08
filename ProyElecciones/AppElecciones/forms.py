####Tips para formularios#####
# initial = kwargs.get("initial", {}) como obtener valores iniciales pasados desde la vista
# https://simpleisbetterthancomplex.com/tutorial/2018/01/29/how-to-implement-dependent-or-chained-dropdown-list-with-django.html
# y soluciona el famoso error: Seleccione una opción válida. La opción seleccionada no es una de las disponibles.
# Importante!!!: El nuevo queryset que se asigna al atributo fuerza debe tener el objeto de la fuerza que se esta editando
# en caso de la edicion del form sino no se muestra, en cambio para el formulario en blanco, cuando se crea un registro, debe tener
# el queryset con la logica de filtrado que se necesite
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import ModelForm, TextInput, ModelChoiceField, Select, HiddenInput, RadioSelect, Textarea, DateInput, \
    ModelMultipleChoiceField, SelectMultiple, Form, CharField, ChoiceField
from leaflet.forms.widgets import LeafletWidget
from crum import get_current_user
from AppElecciones.funciones_comunes import organizacion_del_usuario
from guardian.shortcuts import get_objects_for_user
from AppElecciones.models import (
    Distrito, Subdistrito, Seccion, Circuito, Local, MesasEnLocal, NovedadesEnLocal, SegExternaLocal, Fuerza, Grado,
    Persona, SegInternaLocal, VehiculosPropios, NovedadesGenerales, TipoNovedadLocal, Movimientos,
    Led, SegEnLedFuerzaArmada, SegEnLedFuerzaSeguridad, DistribucionPersonalCdoGrlElect, ReservaCdoGrlElect,
    VehiculosPropiosCdoGrlElect, VehiculosContratadosCdoGrlElect, DistribucionPersonalDistrito, ReservaDistrito,
    VehiculosPropiosDistrito, VehiculosContratadosDistrito, DistribucionPersonalSubdistrito, ReservaSubdistrito,
    VehiculosPropiosSubdistrito, VehiculosContratadosSubdistrito, DistribucionPersonalSeccion, VehiculosPropiosSeccion,
    VehiculosContratadosSeccion, VehiculosContratados, AuxiliarLocal, SACASPuntosRecoleccion, SACACircuitoRecoleccion,
    Sed, LugarInteres, GuiaAutoridades, PuestoGuiaAutoridades, Cargo, DistritoGuia, TipoLugarInteres
)


class FormCircuito(ModelForm):
    distrito = ModelChoiceField(
        queryset=Distrito.objects.all(),
        widget=Select(
            attrs={'id': 'distrito', 'style': 'width: 100%'}),
        required=True)
    subdistrito = ModelChoiceField(
        queryset=Subdistrito.objects.none(),
        widget=Select(
            attrs={'id': 'subdistrito', 'style': 'width: 100%'}),
        required=False)

    seccion = ModelChoiceField(
        queryset=Seccion.objects.none(),
        widget=Select(
            attrs={'id': 'seccion', 'style': 'width: 100%'}),
        required=True)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        org = organizacion_del_usuario()
        if org['org'] == 'distrito':
            queryset = org['distrito_queryset']
        if org['org'] == 'subdistrito':
            queryset = org['distrito_queryset']
        self.fields['distrito'].queryset = queryset

        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'distrito' in self.data:
            try:
                distrito_id = int(self.data.get('distrito'))
                sub_en_bd_cir = Subdistrito.objects.filter(distrito_id=distrito_id)
                if sub_en_bd_cir:
                    self.fields['subdistrito'].queryset = sub_en_bd_cir
                    subdistrito_id = int(self.data.get('subdistrito'))
                    self.fields['seccion'].queryset = Seccion.objects.filter(subdistrito_id=subdistrito_id)
                elif not sub_en_bd_cir:
                    self.fields['seccion'].queryset = Seccion.objects.filter(distrito_id=distrito_id)

            except (ValueError, TypeError):
                pass
        elif self.instance.pk:

            organizacion = organizacion_del_usuario()['org']
            if organizacion == 'distrito':
                # print('por distrito')
                self.fields['distrito'].initial = self.instance.seccion.distrito.id

                self.fields['subdistrito'].initial = self.instance.seccion.subdistrito.id
                self.fields['subdistrito'].queryset = Subdistrito.objects.filter(
                    distrito=self.instance.seccion.distrito.id)

                self.fields['seccion'].initial = self.instance.seccion.id
                self.fields['seccion'].queryset = Seccion.objects.filter(distrito_id=self.instance.seccion.distrito.id)


            if organizacion == 'subdistrito':
                # print(self.instance.seccion.subdistrito.id)
                self.fields['distrito'].initial = self.instance.seccion.distrito.id

                self.fields['subdistrito'].initial = self.instance.seccion.subdistrito.id
                self.fields['subdistrito'].queryset = Subdistrito.objects.filter(id=self.instance.seccion.subdistrito.id)

                self.fields['seccion'].initial = self.instance.seccion.id
                self.fields['seccion'].queryset = Seccion.objects.filter(subdistrito_id=self.instance.seccion.subdistrito.id)


    def clean(self):
        cleaned_data = super(FormCircuito, self).clean()

        distrito = cleaned_data.get("distrito")
        subdistrito = cleaned_data.get("subdistrito")

        sub_en_bd_circuito = Subdistrito.objects.filter(distrito=distrito)

        if distrito:
            if sub_en_bd_circuito:
                if not subdistrito:
                    self.fields['subdistrito'].required = True
                    msg = "Esta campo es obligatorio"
                    self.add_error('subdistrito', msg)
            elif not sub_en_bd_circuito:
                self.fields['subdistrito'].widget = HiddenInput()
                self.fields['seccion'].queryset = Seccion.objects.filter(
                    distrito_id=distrito.id)
        else:
            if not subdistrito:
                msg = "Esta campo es obligatorio si el Distrito posee Subdistritos"
                self.add_error('subdistrito', msg)
        return cleaned_data

    class Meta:
        model = Circuito
        fields = ('distrito', 'subdistrito', 'seccion', 'circuito', 'detalle')
        exclude = ['cant_locales', 'situacion', 'entrego_urna_en_led']
        widgets = {
            'circuito': TextInput(
                attrs={
                    'placeholder': 'Ingrese el código del circuito',
                    'style': 'width: 100%',
                }
            ),
            'detalle': TextInput(
                attrs={
                    'placeholder': 'Detalles sobre el circuito',
                    'style': 'width: 100%',
                }
            ),
            'seccion': Select(
                attrs={
                    'id': 'seccion',
                    'style': 'width: 100%',
                }
            ),
        }


class FormLocal(ModelForm):
    OPCIONES_TELEGRAMA = [(True, "Sí"), (False, "No")]
    transmite_telegrama = ChoiceField(choices=OPCIONES_TELEGRAMA, widget=RadioSelect(), required=True,
                                      label='Transmite telegrama en el local')

    distrito = ModelChoiceField(
        queryset=Distrito.objects.none(),
        widget=Select(
            attrs={'id': 'distrito', 'style': 'width: 100%'}),
        required=True)

    subdistrito = ModelChoiceField(
        queryset=Subdistrito.objects.none(),
        widget=Select(
            attrs={'id': 'subdistrito', 'style': 'width: 100%'}),
        required=False)

    seccion = ModelChoiceField(
        queryset=Seccion.objects.none(),
        widget=Select(
            attrs={'id': 'seccion', 'style': 'width: 100%'}),
        required=True)

    circuito = ModelChoiceField(
        queryset=Circuito.objects.none(),
        widget=Select(
            attrs={'id': 'circuito', 'style': 'width: 100%'}),
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        org = organizacion_del_usuario()
        if org['org'] == 'distrito':
            queryset = org['distrito_queryset']
        if org['org'] == 'subdistrito':
            queryset = org['distrito_queryset']
        self.fields['distrito'].queryset = queryset

        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['validado'].widget = HiddenInput()
        self.fields['transmite_telegrama'].initial = False

        if 'distrito' in self.data:
            try:
                distrito_id = int(self.data.get('distrito'))
                sub_en_bd_ = Subdistrito.objects.filter(distrito_id=distrito_id)

                if sub_en_bd_:
                    self.fields['subdistrito'].queryset = sub_en_bd_
                    subdistrito_id = int(self.data.get('subdistrito'))
                    self.fields['seccion'].queryset = Seccion.objects.filter(subdistrito_id=subdistrito_id)

                elif not sub_en_bd_:
                    self.fields['seccion'].queryset = Seccion.objects.filter(distrito_id=distrito_id)

                seccion_id = int(self.data.get('seccion'))
                self.fields['circuito'].queryset = Circuito.objects.filter(seccion_id=seccion_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            organizacion = organizacion_del_usuario()['org']
            if organizacion == 'distrito':
                self.fields['distrito'].initial = self.instance.circuito.seccion.distrito.id

                self.fields['subdistrito'].initial = self.instance.circuito.seccion.subdistrito.id
                self.fields['subdistrito'].queryset = Subdistrito.objects.filter(
                    distrito=self.instance.circuito.seccion.distrito.id)

                self.fields['seccion'].initial = self.instance.circuito.seccion.id
                self.fields['seccion'].queryset = Seccion.objects.filter(distrito_id=self.instance.circuito.seccion.distrito.id)

                self.fields['circuito'].initial = self.instance.circuito.id
                self.fields['circuito'].queryset = Circuito.objects.filter(id=self.instance.circuito.id)

            if organizacion == 'subdistrito':
                self.fields['distrito'].initial = self.instance.circuito.seccion.distrito.id

                self.fields['subdistrito'].initial = self.instance.circuito.seccion.subdistrito.id
                self.fields['subdistrito'].queryset = Subdistrito.objects.filter(
                    id=self.instance.circuito.seccion.subdistrito.id)

                self.fields['seccion'].initial = self.instance.circuito.seccion.id
                self.fields['seccion'].queryset = Seccion.objects.filter(
                    subdistrito_id=self.instance.circuito.seccion.subdistrito.id)

                self.fields['circuito'].initial = self.instance.circuito.id
                self.fields['circuito'].queryset = Circuito.objects.filter(id=self.instance.circuito.id)

    def clean(self):

        cleaned_data = super(FormLocal, self).clean()

        distrito = cleaned_data.get("distrito")
        subdistrito = cleaned_data.get("subdistrito")

        sub_en_bd = Subdistrito.objects.filter(distrito=distrito)

        if distrito:
            if sub_en_bd:
                if not subdistrito:
                    self.fields['subdistrito'].required = True
                    msg = "Esta campo es obligatorio"
                    self.add_error('subdistrito', msg)
            elif not sub_en_bd:
                self.fields['subdistrito'].widget = HiddenInput()
                self.fields['seccion'].queryset = Seccion.objects.filter(distrito_id=distrito.id)
        else:
            if not subdistrito:
                msg = "Este campo es obligatorio si el Distrito posee Subdistritos"
                self.add_error('subdistrito', msg)
        return cleaned_data

    class Meta:
        model = Local
        # fields = '__all__'
        fields = ('seccion', 'nombre', 'localidad', 'direccion',
                  'circuito', 'validado', 'ubicacion', 'distrito', 'subdistrito', 'transmite_telegrama')
        exclude = ['causa', 'estado']

        widgets = {
            'ubicacion': LeafletWidget(),
            'nombre': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'localidad': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'direccion': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'validado': Select(attrs={'id': 'id_validado', 'style': 'width: 100%'}),

        }
        error_messages = {
            'ubicacion': {
                'required': "No se ha ubicado el local en el mapa",
            },
        }


class FormMesasLocal(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['mesas'].widget.attrs['autofocus'] = True

    class Meta:
        model = MesasEnLocal
        fields = ('mesas', 'voto')
        exclude = ('local', 'estado')
        error_messages = {
            'mesas': {
                'unique': 'Este número de mesa ya se asignó a un local'
            },
        }
        widgets = {
            'mesas': TextInput(
                attrs={'style': 'width: 100%'}
            ),

            'voto': Select(attrs={'id': 'id_voto', 'style': 'width: 100%'}),
        }


class FormNovedadesLocal(ModelForm):

    def __init__(self, *args, **kwargs):
        # initial = kwargs.get("initial", {}) como obtener valores iniciales pasados desde la vista
        # id_local = kwargs.pop('id_del_local', None)
        super().__init__(*args, **kwargs)
        # Lugar: 0=local, 1=general y 2=ambas
        self.fields['tipo'].queryset = TipoNovedadLocal.objects.filter(Q(lugar=0) | Q(lugar=2))
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    def clean(self):
        subsanada = self.cleaned_data.get('subsanada')
        medidas_adoptadas = self.cleaned_data.get('medidas_adoptadas')
        if subsanada:  # si viene con si o no
            if subsanada == 'Si':
                # print('subsanada: si')
                if not medidas_adoptadas:
                    # print('subsanada: si y med adop vacio')
                    msg = ValidationError(
                        "Este campo es obligatorio sin se subsano la novedad.")
                    self.add_error('medidas_adoptadas', msg)
                if medidas_adoptadas == '--':
                    msg = ValidationError(
                        "Este campo es obligatorio sin se subsano la novedad.")
                    self.add_error('medidas_adoptadas', msg)

            if subsanada == 'No':
                self.cleaned_data['medidas_adoptadas'] = '--'
                # print('subsanada: no')

        else:
            self.cleaned_data['medidas_adoptadas'] = ''
            # print('subsanada vacio')

        return self.cleaned_data

    class Meta:
        model = NovedadesEnLocal
        fields = ('local', 'fecha', 'tipo', 'detalle',
                  'subsanada', 'medidas_adoptadas')
        exclude = ['local']
        widgets = {
            'fecha': DateInput(
                attrs={
                    'style': 'width: 100%',
                },
                format=('%d/%m/%Y %H:%M')
                # format=('%d/%m/%Y')
            ),
            'tipo': Select(
                attrs={
                    'id': 'tipo',
                    'style': 'width: 100%',
                }
            ),
            'medidas_adoptadas': TextInput(
                attrs={
                    'placeholder': 'Resuma brevemente como subsanó la novedad',
                    'style': 'width: 100%',
                }),
            'detalle': Textarea(
                attrs={
                    "rows": 2,
                    "cols": 20,
                    # "style": "resize: none"
                    "style": "width: 100%"
                }),
            'subsanada': Select(
                attrs={
                    'id': 'subsanada',
                    'style': 'width: 100%',
                }
            ),
            'medidas_adoptadas': Textarea(
                attrs={
                    "rows": 2,
                    "cols": 20,
                    "style": "width: 100%"}),
        }
        labels = {
            'medidas_adoptadas': '',
        }


class FormSeguridadExternaLocal(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SegExternaLocal
        fields = ('fuerza', 'local', 'cant_efectivos')
        exclude = ['local']
        widgets = {

            'fuerza': Select(
                attrs={
                    'id': 'fuerza',
                    'style': 'width: 100%',
                }
            ),
            'cant_efectivos': TextInput(
                attrs={
                    'style': 'width: 100%',
                    'placeholder': ''
                }
            )
        }


class FormPersona(ModelForm):
    fuerza = ModelChoiceField(
        queryset=Fuerza.objects.all(),
        widget=Select(
            attrs={'id': 'id_fuerza', 'style': 'width: 100%'}),
        required=True)



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        self.fields['validado'].widget = HiddenInput()

        self.fields['grado'].queryset = Grado.objects.none()

        if 'fuerza' in self.data:
            # print(self.data)
            try:
                grado_id = int(self.data.get('grado'))

                self.fields['grado'].queryset = Grado.objects.filter(
                    id=grado_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['grado'].init = Grado.objects.filter(id=self.instance.grado.id)
            self.fields['grado'].queryset = Grado.objects.filter(fuerza=self.instance.fuerza)

    def clean(self):
        cleaned_data = super().clean()
        field1 = cleaned_data.get('numero_armamento')
        field2 = cleaned_data.get('numero_armamento_con_letras')
        tipo_armamento = cleaned_data.get('tipo_armamento')
        if field1 and field2:
            raise ValidationError("Solo se permite agregar un Número de armamento")
        if tipo_armamento == 'fusil' or tipo_armamento == 'pistola':
            if not field1 and not field2:
                raise ValidationError("Al seleccionar el tipo de armamento debe asignarle un Número")
        if tipo_armamento == 'sin_armamento':
            if field1 or field2:
                raise ValidationError("Al seleccionar Sin armamento no debe asignarle un Número")

        return cleaned_data

    class Meta:
        model = Persona
        fields = ('fuerza', 'grado', 'nombre', 'apellido',
                  'dni', 'nro_tel', 'tipo_armamento', 'numero_armamento', 'validado', 'numero_armamento_con_letras')
        error_messages = {
            'dni': {
                'unique': 'La persona con este DNI ya ha sido cargada'
            },
        }
        exclude = ['distrito', ]

        widgets = {
            'tipo_armamento': RadioSelect(attrs={'id': 'value'}),
            'grado': Select(
                attrs={
                    'id': 'grado',
                    'style': 'width: 100%',
                }
            ),
            'nombre': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'apellido': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'dni': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'nro_tel': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'numero_armamento': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'numero_armamento_con_letras': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'validado': Select(attrs={'id': 'id_validado_persona', 'style': 'width: 100%'}),
        }


class FormSeguridadInternaLocal(ModelForm):
    jefe_local = ModelChoiceField(
        queryset=Persona.objects.none(),
        widget=Select(
            attrs={'id': 'id_jefe_local', 'style': 'width: 100%'}),
        required=True)

    auxiliares = ModelMultipleChoiceField(
        queryset=Persona.objects.none(),
        widget=SelectMultiple(
            attrs={'id': 'id_auxiliares', 'style': 'width: 100%'}),
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'jefe_local' in self.data:
            try:
                self.fields['jefe_local'].queryset = Persona.objects.filter(id=int(self.data.get('jefe_local')))
                self.fields['auxiliares'].queryset = Persona.objects.filter(id__in=self.data.getlist('auxiliares'))
            except (ValueError, TypeError):
                pass

        elif self.instance.pk:
            self.fields['jefe_local'].initial = self.instance.jefe_local.id
            self.fields['jefe_local'].queryset = Persona.objects.filter(id=self.instance.jefe_local.id)
            self.fields['auxiliares'].initial = [a.auxiliar.id for a in
                                                 AuxiliarLocal.objects.filter(seg_interna_local=self.instance)]
            self.fields['auxiliares'].queryset = Persona.objects.filter(
                id__in=[a.auxiliar.id for a in AuxiliarLocal.objects.filter(seg_interna_local=self.instance)])

    def clean(self):
        cleaned_data = super(FormSeguridadInternaLocal, self).clean()
        jefeLocal = cleaned_data.get("jefe_local")
        auxiliares = cleaned_data.get("auxiliares")

        if jefeLocal and auxiliares:
            if jefeLocal in auxiliares:
                msg = "No puede repetir el Jefe de Local como Auxiliar."
                self.add_error('auxiliares', msg)

        return cleaned_data

    class Meta:
        model = SegInternaLocal
        fields = ('local', 'jefe_local', 'auxiliares')
        exclude = ['local']
        # fields = "__all__"
        widgets = {
        }


class FormVehiculoPropio(ModelForm):
    OPCIONES_SENSOR = [(True, "Sí"), (False, "No")]
    posee_sensor_rastreo = ChoiceField(choices=OPCIONES_SENSOR, widget=RadioSelect(), required=True,
                                       label='Posee sensor de rastreo (Spot/Celular)')

    OPCIONES_TRONCAL = [(1, "Primaria"), (2, "Secundaria"), (3, "Ninguna")]
    troncal = ChoiceField(choices=OPCIONES_TRONCAL, widget=RadioSelect(), required=True,
                          label='Se usa como troncal')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = VehiculosPropios
        # fields = '__all__'
        fields = ('unidad', 'tipo_vehiculo_provisto', 'tipo_combustible', 'ni_patente_matricula',
                  'consumo_en_litros_horas_voladas', 'posee_sensor_rastreo', 'troncal')
        exclude = ['distrito', ]
        widgets = {
            'fuerza': Select(
                attrs={
                    'id': 'fuerza',
                    'style': 'width: 100%',

                }
            ),
            'unidad': Select(
                attrs={
                    'id': 'unidad',
                    'style': 'width: 100%',

                }
            ),
            'tipo_vehiculo_provisto': Select(
                attrs={
                    'id': 'tipo_veh_pro',
                    'style': 'width: 100%',

                }
            ),
            # 'tareas': Select(
            #     attrs={
            #         'id': 'tareas',
            #         'style': 'width: 100%',
            #
            #     }
            # ),
            'tipo_combustible': Select(
                attrs={
                    'id': 'tipo_combustible',
                    'style': 'width: 100%',

                }
            ),
            # 'desde': DateInput(format=('%d/%m/%Y'), attrs={'autocomplete': 'off', 'style': 'width: 100%'}),
            # 'hasta': DateInput(format=('%d/%m/%Y'), attrs={'autocomplete': 'off', 'style': 'width: 100%'}),
            # 'cantidad_pasajeros': TextInput(
            #     attrs={
            #         'style': 'width: 100%'
            #     }
            # ),
            # 'zona_trabajo': TextInput(
            #     attrs={
            #         'style': 'width: 100%'
            #     }
            # ),
            # 'kilometros_a_recorrer': TextInput(
            #     attrs={
            #         'style': 'width: 100%'
            #     }
            # ),
            # 'obs': TextInput(
            #     attrs={
            #         'style': 'width: 100%'
            #     }
            # ),
            'ni_patente_matricula': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'consumo_en_litros_horas_voladas': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
        }


class FormVehiculoContratado(ModelForm):
    OPCIONES_SENSOR = [(True, "Sí"), (False, "No")]
    posee_sensor_rastreo = ChoiceField(choices=OPCIONES_SENSOR, widget=RadioSelect(), required=True,
                                       label='Posee sensor de rastreo (Spot/Celular)')

    OPCIONES_TRONCAL = [(1, "Primaria"), (2, "Secundaria"), (3, "Ninguna")]
    troncal = ChoiceField(choices=OPCIONES_TRONCAL, widget=RadioSelect(), required=True,
                          label='Se usa como troncal')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = VehiculosContratados
        # fields = '__all__'
        fields = ('tipo_vehiculo_contratado', 'patente_matricula', 'posee_sensor_rastreo', 'troncal')
        exclude = ['distrito', ]
        widgets = {
            'tipo_vehiculo_contratado': Select(
                attrs={
                    'id': 'tipo_veh_cont',
                    'style': 'width: 100%',
                }
            ),
            'patente_matricula': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
        }


class FormNovedadesGenerales(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lugar: 0=local, 1=general y 2=ambas
        self.fields['tipo'].queryset = TipoNovedadLocal.objects.filter(Q(lugar=1) | Q(lugar=2))
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    def clean(self):
        subsanada = self.cleaned_data.get('subsanada')
        medidas_adoptadas = self.cleaned_data.get('medidas_adoptadas')
        if subsanada:  # si viene con si o no
            if subsanada == 'Si':
                # print('subsanada: si')
                if not medidas_adoptadas:
                    # print('subsanada: si y med adop vacio')
                    msg = ValidationError(
                        "Este campo es obligatorio sin se subsano la novedad.")
                    self.add_error('medidas_adoptadas', msg)
                if medidas_adoptadas == '--':
                    msg = ValidationError(
                        "Este campo es obligatorio sin se subsano la novedad.")
                    self.add_error('medidas_adoptadas', msg)

            if subsanada == 'No':
                self.cleaned_data['medidas_adoptadas'] = '--'
                # print('subsanada: no')

        else:
            self.cleaned_data['medidas_adoptadas'] = ''
            # print('subsanada vacio')

        # ubicacion = self.cleaned_data.get('ubicacion')
        # # print(ubicacion)
        # if ubicacion == None:
        #     raise forms.ValidationError(
        #         "No se ha ubicado la novedad en el mapa. Utilice la herramienta 'Dibujar marcador' desplazando el mismo a la dirección buscada.")

        return self.cleaned_data

    class Meta:
        model = NovedadesGenerales
        fields = ('fecha', 'tipo', 'detalle', 'subsanada', 'medidas_adoptadas', 'ubicacion')
        exclude = ['distrito', ]
        widgets = {
            'ubicacion': LeafletWidget(),
            'fecha': DateInput(
                attrs={
                    'id': 'fecha_nov',
                    'style': 'width: 100%',
                },
                format=('%d/%m/%Y %H:%M')
            ),
            'tipo': Select(
                attrs={
                    'id': 'tipo_nov_grl',
                    'style': 'width: 100%',
                }
            ),
            'medidas_adoptadas': TextInput(
                attrs={
                    'placeholder': 'Resuma brevemente como subsanó la novedad máximo 50 caracteres',
                    'style': 'width: 100%',
                }),
            'detalle': Textarea(
                attrs={
                    "rows": 1,
                    "cols": 20,
                    # "style": "resize: none"
                    "style": "width: 100%"
                }),
            'subsanada': Select(
                attrs={
                    'id': 'subsanada',
                    'style': 'width: 100%',
                }
            ),
        }
        error_messages = {
            'ubicacion': {
                'required': 'Debe ubicar la novedad en el mapa'
            },
        }


class FormMovimientos(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    def clean(self):
        cleaned_data = super(FormMovimientos, self).clean()
        inicio = cleaned_data.get("inicio")
        fin = cleaned_data.get("fin")
        if inicio and fin:
            if inicio > fin:
                msg = "Esta fecha de inicio no puede ser posterior a la de finalización"
                self.add_error('inicio', msg)

    class Meta:
        model = Movimientos
        fields = ('tipo', 'efectivos', 'vehiculos', 'inicio', 'fin', 'lugar_desde', 'lugar_hasta', 'distancia')
        exclude = ['distrito', ]
        widgets = {
            'tipo': Select(
                attrs={
                    'id': 'tipo_mov',
                    'style': 'width: 100%',
                }
            ),
            'efectivos': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'vehiculos': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'lugar_desde': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'lugar_hasta': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'distancia': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'inicio': DateInput(format=('%d/%m/%Y %H:%M'),
                                attrs={'id': 'inicio', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'fin': DateInput(format=('%d/%m/%Y %H:%M'),
                             attrs={'id': 'fin', 'autocomplete': 'off', 'style': 'width: 100%'}),
        }


class FormLed(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Led
        # fields = '__all__'
        fields = ('direccion', 'ubicacion', 'tipo', 'obs')
        exclude = ['distrito', ]
        widgets = {
            'direccion': TextInput(
                attrs={
                    "style": "width: 100%"
                }),
            'ubicacion': LeafletWidget(),
            'tipo': Select(
                attrs={
                    'id': 'tipo_led',
                    'style': 'width: 100%',
                }
            ),
            'obs': TextInput(
                attrs={
                    "style": "width: 100%"
                }),
        }
        error_messages = {
            'ubicacion': {
                'required': 'Debe ubicar el LED en el mapa'
            },
        }


class FormSegLedFFAA(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    def clean(self):
        cleaned_data = super(FormSegLedFFAA, self).clean()
        inicio = cleaned_data.get("fecha_inicio")
        fin = cleaned_data.get("fecha_fin")
        if inicio and fin:
            if inicio > fin:
                msg = "Esta fecha de inicio no puede ser posterior a la de finalización"
                self.add_error('fecha_inicio', msg)

    class Meta:
        model = SegEnLedFuerzaArmada
        fields = ('fecha_inicio', 'fecha_fin',
                  'fuerza_armada', 'cant_personal')
        exclude = ['led', ]
        widgets = {
            'fecha_inicio': DateInput(format=('%d/%m/%Y %H:%M'),
                                      attrs={'id': 'fecha_inicio', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'fecha_fin': DateInput(format=('%d/%m/%Y %H:%M'),
                                   attrs={'id': 'fecha_fin', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'fuerza_armada': Select(
                attrs={
                    'id': 'fuerza_armada',
                    'style': 'width: 100%',
                }
            ),
            'cantidad_personal': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
        }


class FormSegLedFFSeguridad(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    def clean(self):
        cleaned_data = super(FormSegLedFFSeguridad, self).clean()
        inicio = cleaned_data.get("fecha_inicio")
        fin = cleaned_data.get("fecha_fin")
        if inicio and fin:
            if inicio > fin:
                msg = "Esta fecha de inicio no puede ser posterior a la de finalización"
                self.add_error('fecha_inicio', msg)

    class Meta:
        model = SegEnLedFuerzaSeguridad
        fields = ('fecha_inicio', 'fecha_fin',
                  'fuerza_seguridad', 'cant_personal')
        exclude = ['led', ]
        widgets = {
            'fecha_inicio': DateInput(format=('%d/%m/%Y %H:%M'),
                                      attrs={'id': 'fecha_inicio_ffseg', 'autocomplete': 'off',
                                             'style': 'width: 100%'}),
            'fecha_fin': DateInput(format=('%d/%m/%Y %H:%M'),
                                   attrs={'id': 'fecha_fin_ffseg', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'fuerza_seguridad': Select(
                attrs={
                    'id': 'fuerza_seguridad',
                    'style': 'width: 100%',
                }
            ),
            'cantidad_personal': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
        }


class FormDistribucionPersonalCdoGrlElect(ModelForm):
    integrante = ModelChoiceField(
        queryset=Persona.objects.none(),
        widget=Select(
            attrs={'id': 'integrantes', 'style': 'width: 100%'}),
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cargo'].queryset = Cargo.objects.filter(guia=False)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'integrante' in self.data:
            try:
                self.fields['integrante'].queryset = Persona.objects.filter(id=int(self.data.get('integrante')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:

            self.fields['integrante'].initial = self.instance.integrante.id
            self.fields['integrante'].queryset = Persona.objects.filter(id=self.instance.integrante.id)

    class Meta:
        model = DistribucionPersonalCdoGrlElect
        fields = ('cargo', 'designacion', 'integrante')
        exclude = ('cge',)
        widgets = {
            'cargo': Select(
                attrs={
                    'id': 'cargo',
                    'style': 'width: 100%',
                }
            ),
            'designacion': TextInput(
                attrs={
                    'style': 'width: 100%',
                    'placeholder': ''
                }
            ),
        }
        error_messages = {
            'designacion': {
                'required': "Esta campo es obligatorio, ingrese --- si no tiene datos",
            },
        }


class FormReservaCdoGrlElect(ModelForm):
    integrante = ModelChoiceField(
        queryset=Persona.objects.none(),
        widget=Select(
            attrs={'id': 'integrante_reserva_cge', 'style': 'width: 100%'}),
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'integrante' in self.data:
            try:
                self.fields['integrante'].queryset = Persona.objects.filter(id=int(self.data.get('integrante')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:

            self.fields['integrante'].initial = self.instance.integrante.id
            self.fields['integrante'].queryset = Persona.objects.filter(id=self.instance.integrante.id)

    class Meta:
        model = ReservaCdoGrlElect
        fields = ('integrante', 'obs')
        exclude = ('cge',)
        widgets = {
            'obs': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese --- si no tiene datos",
            },
        }


class FormVehiculosPropiosCdoGrlElect(ModelForm):
    # conductor = ModelChoiceField(
    #     queryset=Persona.objects.none(),
    #     widget=Select(
    #         attrs={'id': 'conductor_veh_propio', 'style': 'width: 100%'}),
    #     required=True)
    veh_propio = ModelChoiceField(
        queryset=VehiculosPropios.objects.none(),
        widget=Select(
            attrs={'id': 'veh_propio', 'style': 'width: 100%'}),
        label="Vehículo",
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'veh_propio' in self.data:
            try:
                self.fields['veh_propio'].queryset = VehiculosPropios.objects.filter(
                    id=int(self.data.get('veh_propio')))
                # self.fields['conductor'].queryset = Persona.objects.filter(id=int(self.data.get('conductor')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['veh_propio'].initial = self.instance.veh_propio.id
            self.fields['veh_propio'].queryset = VehiculosPropios.objects.filter(id=self.instance.veh_propio.id)
            # self.fields['conductor'].initial = self.instance.conductor.id
            # self.fields['conductor'].queryset = Persona.objects.filter(id=self.instance.conductor.id)

    def clean(self):
        cleaned_data = super(FormVehiculosPropiosCdoGrlElect, self).clean()
        desde = cleaned_data.get("desde")
        hasta = cleaned_data.get("hasta")

        if desde and hasta:
            if desde > hasta:
                msg = "Esta fecha de comienzo debe ser posterior a la de finalización"
                self.add_error('desde', msg)
        return cleaned_data

    class Meta:
        model = VehiculosPropiosCdoGrlElect
        fields = ('veh_propio', 'desde', 'hasta', 'tareas', 'zona_trabajo', 'kilometros_a_recorrer', 'obs')
        exclude = ('cge',' conductor')
        widgets = {
            'tareas': Select(
                attrs={
                    'id': 'tareas',
                    'style': 'width: 100%',
                }
            ),
            'desde': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_desde', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'hasta': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_hasta', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'zona_trabajo': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'kilometros_a_recorrer': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'obs': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            )
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese Sin novedad si no tiene datos",
            },
        }


class FormVehiculosContratadosCdoGrlElect(ModelForm):
    # responsable = ModelChoiceField(
    #     queryset=Persona.objects.none(),
    #     widget=Select(
    #         attrs={'id': 'responsable_veh_contratado', 'style': 'width: 100%'}),
    #     required=True)

    vehiculo_contratado = ModelChoiceField(
        queryset=VehiculosContratados.objects.none(),
        widget=Select(
            attrs={'id': 'veh_cont_cge', 'style': 'width: 100%'}),
        label="Vehículo",
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'vehiculo_contratado' in self.data:
            try:
                # self.fields['responsable'].queryset = Persona.objects.filter(id=int(self.data.get('responsable')))
                self.fields['vehiculo_contratado'].queryset = VehiculosContratados.objects.filter(
                    id=int(self.data.get('vehiculo_contratado')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # self.fields['responsable'].initial = self.instance.responsable.id
            # self.fields['responsable'].queryset = Persona.objects.filter(id=self.instance.responsable.id)
            self.fields['vehiculo_contratado'].initial = self.instance.vehiculo_contratado.id
            self.fields['vehiculo_contratado'].queryset = VehiculosContratados.objects.filter(
                id=self.instance.vehiculo_contratado.id)

    def clean(self):
        cleaned_data = super(FormVehiculosContratadosCdoGrlElect, self).clean()
        desde = cleaned_data.get("desde")
        hasta = cleaned_data.get("hasta")

        if desde and hasta:
            if desde > hasta:
                msg = "Esta fecha de comienzo debe ser posterior a la de finalización"
                self.add_error('desde', msg)
        return cleaned_data

    class Meta:
        model = VehiculosContratadosCdoGrlElect
        fields = ('vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde',
                  'hasta', 'kilometros_a_recorrer', 'obs')
        exclude = ('cge', 'responsable')
        widgets = {

            'cantidad_pasajeros': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'tareas': Select(
                attrs={
                    'id': 'tareas_veh_cont_cge',
                    'style': 'width: 100%',
                }
            ),
            'zona_trabajo': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'desde': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_desde', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'hasta': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_hasta', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'kilometros_a_recorrer': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'obs': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese Sin novedad si no tiene datos",
            },
        }


class FormDistribucionPersonalDistrito(ModelForm):
    integrante = ModelChoiceField(
        queryset=Persona.objects.none(),
        widget=Select(
            attrs={'id': 'integrantes', 'style': 'width: 100%'}),
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cargo'].queryset = Cargo.objects.filter(guia=False)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'integrante' in self.data:
            try:
                self.fields['integrante'].queryset = Persona.objects.filter(id=int(self.data.get('integrante')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:

            self.fields['integrante'].initial = self.instance.integrante.id
            self.fields['integrante'].queryset = Persona.objects.filter(id=self.instance.integrante.id)

    class Meta:
        model = DistribucionPersonalDistrito
        fields = ('cargo', 'designacion', 'integrante')
        exclude = ('distrito',)
        widgets = {
            'cargo': Select(
                attrs={
                    'id': 'cargo',
                    'style': 'width: 100%',
                }
            ),
            'designacion': TextInput(
                attrs={
                    'style': 'width: 100%',
                    'placeholder': ''
                }
            ),
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese --- si no tiene datos",
            },
        }


class FormReservaDistrito(ModelForm):
    integrante = ModelChoiceField(
        queryset=Persona.objects.none(),
        widget=Select(
            attrs={'id': 'integrante_reserva_distrito', 'style': 'width: 100%'}),
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'integrante' in self.data:
            try:
                self.fields['integrante'].queryset = Persona.objects.filter(id=int(self.data.get('integrante')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:

            self.fields['integrante'].initial = self.instance.integrante.id
            self.fields['integrante'].queryset = Persona.objects.filter(id=self.instance.integrante.id)

    class Meta:
        model = ReservaDistrito
        fields = ('integrante', 'obs')
        exclude = ('distrito',)
        widgets = {
            'obs': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese --- si no tiene datos",
            },
        }


class FormVehiculosPropiosDistrito(ModelForm):
    # conductor = ModelChoiceField(
    #     queryset=Persona.objects.none(),
    #     widget=Select(
    #         attrs={'id': 'conductor_veh_propio_d', 'style': 'width: 100%'}),
    #     required=True)
    veh_propio = ModelChoiceField(
        queryset=VehiculosPropios.objects.none(),
        widget=Select(
            attrs={'id': 'veh_propio_d', 'style': 'width: 100%'}),
        label="Vehículo",
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'veh_propio' in self.data:
            try:
                self.fields['veh_propio'].queryset = VehiculosPropios.objects.filter(
                    id=int(self.data.get('veh_propio')))
                # self.fields['conductor'].queryset = Persona.objects.filter(id=int(self.data.get('conductor')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['veh_propio'].initial = self.instance.veh_propio.id
            self.fields['veh_propio'].queryset = VehiculosPropios.objects.filter(id=self.instance.veh_propio.id)
            # self.fields['conductor'].initial = self.instance.conductor.id
            # self.fields['conductor'].queryset = Persona.objects.filter(id=self.instance.conductor.id)

    def clean(self):
        cleaned_data = super(FormVehiculosPropiosDistrito, self).clean()
        desde = cleaned_data.get("desde")
        hasta = cleaned_data.get("hasta")

        if desde and hasta:
            if desde > hasta:
                msg = "Esta fecha de comienzo debe ser posterior a la de finalización"
                self.add_error('desde', msg)
        return cleaned_data

    class Meta:
        model = VehiculosPropiosDistrito
        fields = ('veh_propio', 'desde', 'hasta', 'tareas', 'zona_trabajo', 'kilometros_a_recorrer', 'obs')
        exclude = ('distrito','conductor')
        widgets = {
            'tareas': Select(
                attrs={
                    'id': 'tareas_d',
                    'style': 'width: 100%',
                }
            ),
            'desde': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_desde_d', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'hasta': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_hasta_d', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'zona_trabajo': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'kilometros_a_recorrer': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'obs': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            )
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese Sin novedad si no tiene datos",
            },
        }


class FormVehiculosContratadosDistrito(ModelForm):
    # responsable = ModelChoiceField(
    #     queryset=Persona.objects.none(),
    #     widget=Select(
    #         attrs={'id': 'responsable_veh_contratado_d', 'style': 'width: 100%'}),
    #     required=True)
    vehiculo_contratado = ModelChoiceField(
        queryset=VehiculosContratados.objects.none(),
        widget=Select(
            attrs={'id': 'veh_cont_distrito', 'style': 'width: 100%'}),
        label="Vehículo",
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'vehiculo_contratado' in self.data:
            try:
                # self.fields['responsable'].queryset = Persona.objects.filter(id=int(self.data.get('responsable')))
                self.fields['vehiculo_contratado'].queryset = VehiculosContratados.objects.filter(
                    id=int(self.data.get('vehiculo_contratado')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # self.fields['responsable'].initial = self.instance.responsable.id
            # self.fields['responsable'].queryset = Persona.objects.filter(id=self.instance.responsable.id)
            self.fields['vehiculo_contratado'].initial = self.instance.vehiculo_contratado.id
            self.fields['vehiculo_contratado'].queryset = VehiculosContratados.objects.filter(
                id=self.instance.vehiculo_contratado.id)

    def clean(self):
        cleaned_data = super(FormVehiculosContratadosDistrito, self).clean()
        desde = cleaned_data.get("desde")
        hasta = cleaned_data.get("hasta")

        if desde and hasta:
            if desde > hasta:
                msg = "Esta fecha de comienzo debe ser posterior a la de finalización"
                self.add_error('desde', msg)
        return cleaned_data

    class Meta:
        model = VehiculosContratadosDistrito
        fields = ('vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde',
                  'hasta', 'kilometros_a_recorrer', 'obs')
        exclude = ('distrito','responsable')
        widgets = {
            'cantidad_pasajeros': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'tareas': Select(
                attrs={
                    'id': 'tareas_veh_civil_d',
                    'style': 'width: 100%',
                }
            ),
            'zona_trabajo': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'desde': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_desde_veh_civil_d', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'hasta': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_hasta_veh_civil_d', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'kilometros_a_recorrer': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'obs': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese Sin novedad si no tiene datos",
            },
        }


class FormDistribucionPersonalSubdistrito(ModelForm):
    integrante = ModelChoiceField(
        queryset=Persona.objects.none(),
        widget=Select(
            attrs={'id': 'integrante_pers_sub', 'style': 'width: 100%'}),
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cargo'].queryset = Cargo.objects.filter(guia=False)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'integrante' in self.data:
            try:
                self.fields['integrante'].queryset = Persona.objects.filter(id=int(self.data.get('integrante')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:

            self.fields['integrante'].initial = self.instance.integrante.id
            self.fields['integrante'].queryset = Persona.objects.filter(id=self.instance.integrante.id)

    class Meta:
        model = DistribucionPersonalSubdistrito
        fields = ('cargo', 'designacion', 'integrante')
        exclude = ('subdistrito',)
        widgets = {
            'cargo': Select(
                attrs={
                    'id': 'cargo_pers_sub',
                    'style': 'width: 100%',
                }
            ),
            'designacion': TextInput(
                attrs={
                    'style': 'width: 100%',
                    'placeholder': ''
                }
            ),
        }


class FormReservaSubdistrito(ModelForm):
    integrante = ModelChoiceField(
        queryset=Persona.objects.none(),
        widget=Select(
            attrs={'id': 'integrante_reserva_subdistrito', 'style': 'width: 100%'}),
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'integrante' in self.data:
            try:
                self.fields['integrante'].queryset = Persona.objects.filter(id=int(self.data.get('integrante')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:

            self.fields['integrante'].initial = self.instance.integrante.id
            self.fields['integrante'].queryset = Persona.objects.filter(id=self.instance.integrante.id)

    class Meta:
        model = ReservaSubdistrito
        fields = ('integrante', 'obs')
        exclude = ('subdistrito',)
        widgets = {
            'obs': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese --- si no tiene datos",
            },
        }


class FormVehiculosPropiosSubdistrito(ModelForm):
    # conductor = ModelChoiceField(
    #     queryset=Persona.objects.none(),
    #     widget=Select(
    #         attrs={'id': 'conductor_veh_propio_s', 'style': 'width: 100%'}),
    #     required=True)
    veh_propio = ModelChoiceField(
        queryset=VehiculosPropios.objects.none(),
        widget=Select(
            attrs={'id': 'veh_propio_s', 'style': 'width: 100%'}),
        label="Vehículo",
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'veh_propio' in self.data:
            try:
                self.fields['veh_propio'].queryset = VehiculosPropios.objects.filter(
                    id=int(self.data.get('veh_propio')))
                # self.fields['conductor'].queryset = Persona.objects.filter(id=int(self.data.get('conductor')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['veh_propio'].initial = self.instance.veh_propio.id
            self.fields['veh_propio'].queryset = VehiculosPropios.objects.filter(id=self.instance.veh_propio.id)
            # self.fields['conductor'].initial = self.instance.conductor.id
            # self.fields['conductor'].queryset = Persona.objects.filter(id=self.instance.conductor.id)

    def clean(self):
        cleaned_data = super(FormVehiculosPropiosSubdistrito, self).clean()
        desde = cleaned_data.get("desde")
        hasta = cleaned_data.get("hasta")

        if desde and hasta:
            if desde > hasta:
                msg = "Esta fecha de comienzo debe ser posterior a la de finalización"
                self.add_error('desde', msg)
        return cleaned_data

    class Meta:
        model = VehiculosPropiosSubdistrito
        fields = ('veh_propio', 'desde', 'hasta', 'tareas', 'zona_trabajo', 'kilometros_a_recorrer', 'obs')
        exclude = ('subdistrito','conductor')
        widgets = {
            'tareas': Select(
                attrs={
                    'id': 'tareas_s',
                    'style': 'width: 100%',
                }
            ),
            'desde': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_desde_s', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'hasta': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_hasta_s', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'zona_trabajo': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'kilometros_a_recorrer': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'obs': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            )
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese Sin novedad si no tiene datos",
            },
        }


class FormVehiculosContratadosSubdistrito(ModelForm):
    # responsable = ModelChoiceField(
    #     queryset=Persona.objects.none(),
    #     widget=Select(
    #         attrs={'id': 'responsable_veh_contratado_s', 'style': 'width: 100%'}),
    #     required=True)
    vehiculo_contratado = ModelChoiceField(
        queryset=VehiculosContratados.objects.none(),
        widget=Select(
            attrs={'id': 'veh_cont_subdistrito', 'style': 'width: 100%'}),
        label="Vehículo",
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'vehiculo_contratado' in self.data:
            try:
                # self.fields['responsable'].queryset = Persona.objects.filter(id=int(self.data.get('responsable')))
                self.fields['vehiculo_contratado'].queryset = VehiculosContratados.objects.filter(
                    id=int(self.data.get('vehiculo_contratado')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # self.fields['responsable'].initial = self.instance.responsable.id
            # self.fields['responsable'].queryset = Persona.objects.filter(id=self.instance.responsable.id)
            self.fields['vehiculo_contratado'].initial = self.instance.vehiculo_contratado.id
            self.fields['vehiculo_contratado'].queryset = VehiculosContratados.objects.filter(
                id=self.instance.vehiculo_contratado.id)

    def clean(self):
        cleaned_data = super(FormVehiculosContratadosSubdistrito, self).clean()
        desde = cleaned_data.get("desde")
        hasta = cleaned_data.get("hasta")

        if desde and hasta:
            if desde > hasta:
                msg = "Esta fecha de comienzo debe ser posterior a la de finalización"
                self.add_error('desde', msg)
        return cleaned_data

    class Meta:
        model = VehiculosContratadosSubdistrito
        fields = ('vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde',
                  'hasta', 'kilometros_a_recorrer', 'obs')
        exclude = ('subdistrito','responsable')
        widgets = {
            'cantidad_pasajeros': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'tareas': Select(
                attrs={
                    'id': 'tareas_veh_civil_s',
                    'style': 'width: 100%',
                }
            ),
            'zona_trabajo': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'desde': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_desde_veh_civil_s', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'hasta': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_hasta_veh_civil_s', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'kilometros_a_recorrer': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'obs': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese Sin novedad si no tiene datos",
            },
        }


class FormDistribucionPersonalSeccion(ModelForm):
    integrante = ModelChoiceField(
        queryset=Persona.objects.none(),
        widget=Select(
            attrs={'id': 'integrante_pers_sec', 'style': 'width: 100%'}),
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cargo'].queryset = Cargo.objects.filter(guia=False)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'integrante' in self.data:
            try:
                self.fields['integrante'].queryset = Persona.objects.filter(id=int(self.data.get('integrante')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:

            self.fields['integrante'].initial = self.instance.integrante.id
            self.fields['integrante'].queryset = Persona.objects.filter(id=self.instance.integrante.id)

    class Meta:
        model = DistribucionPersonalSeccion
        fields = ('cargo', 'designacion', 'integrante')
        exclude = ('seccion',)
        widgets = {
            'cargo': Select(
                attrs={
                    'id': 'cargo_pers_sec',
                    'style': 'width: 100%',
                }
            ),
            'designacion': TextInput(
                attrs={
                    'style': 'width: 100%',
                    'placeholder': ''
                }
            ),
        }


class FormVehiculosPropiosSeccion(ModelForm):
    # conductor = ModelChoiceField(
    #     queryset=Persona.objects.none(),
    #     widget=Select(
    #         attrs={'id': 'conductor_veh_propio_sec', 'style': 'width: 100%'}),
    #     required=True)
    veh_propio = ModelChoiceField(
        queryset=VehiculosPropios.objects.none(),
        widget=Select(
            attrs={'id': 'veh_propio_sec', 'style': 'width: 100%'}),
        label="Vehículo",
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'veh_propio' in self.data:
            try:
                self.fields['veh_propio'].queryset = VehiculosPropios.objects.filter(
                    id=int(self.data.get('veh_propio')))
                # self.fields['conductor'].queryset = Persona.objects.filter(id=int(self.data.get('conductor')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['veh_propio'].initial = self.instance.veh_propio.id
            self.fields['veh_propio'].queryset = VehiculosPropios.objects.filter(id=self.instance.veh_propio.id)
            # self.fields['conductor'].initial = self.instance.conductor.id
            # self.fields['conductor'].queryset = Persona.objects.filter(id=self.instance.conductor.id)

    def clean(self):
        cleaned_data = super(FormVehiculosPropiosSeccion, self).clean()
        desde = cleaned_data.get("desde")
        hasta = cleaned_data.get("hasta")

        if desde and hasta:
            if desde > hasta:
                msg = "Esta fecha de comienzo debe ser posterior a la de finalización"
                self.add_error('desde', msg)
        return cleaned_data

    class Meta:
        model = VehiculosPropiosSeccion
        fields = ('veh_propio', 'desde', 'hasta', 'tareas', 'zona_trabajo', 'kilometros_a_recorrer', 'obs')
        exclude = ('seccion','conductor')
        widgets = {
            'tareas': Select(
                attrs={
                    'id': 'tareas_veh_propio_sec',
                    'style': 'width: 100%',
                }
            ),
            'desde': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_desde_veh_propio_sec', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'hasta': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_hasta_veh_propio_sec', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'zona_trabajo': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'kilometros_a_recorrer': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'obs': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            )
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese Sin novedad si no tiene datos",
            },
        }


class FormVehiculosContratadosSeccion(ModelForm):
    # responsable = ModelChoiceField(
    #     queryset=Persona.objects.none(),
    #     widget=Select(
    #         attrs={'id': 'responsable_veh_contratado_sec', 'style': 'width: 100%'}),
    #     required=True)
    vehiculo_contratado = ModelChoiceField(
        queryset=VehiculosContratados.objects.none(),
        widget=Select(
            attrs={'id': 'veh_cont_seccion', 'style': 'width: 100%'}),
        label="Vehículo",
        required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'vehiculo_contratado' in self.data:
            try:
                # self.fields['responsable'].queryset = Persona.objects.filter(id=int(self.data.get('responsable')))
                self.fields['vehiculo_contratado'].queryset = VehiculosContratados.objects.filter(
                    id=int(self.data.get('vehiculo_contratado')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # self.fields['responsable'].initial = self.instance.responsable.id
            # self.fields['responsable'].queryset = Persona.objects.filter(
            #     id=self.instance.responsable.id)
            self.fields['vehiculo_contratado'].initial = self.instance.vehiculo_contratado.id
            self.fields['vehiculo_contratado'].queryset = VehiculosContratados.objects.filter(
                id=self.instance.vehiculo_contratado.id)

    def clean(self):
        cleaned_data = super(FormVehiculosContratadosSeccion, self).clean()
        desde = cleaned_data.get("desde")
        hasta = cleaned_data.get("hasta")

        if desde and hasta:
            if desde > hasta:
                msg = "Esta fecha de comienzo debe ser posterior a la de finalización"
                self.add_error('desde', msg)
        return cleaned_data

    class Meta:
        model = VehiculosContratadosSeccion
        fields = ('vehiculo_contratado', 'cantidad_pasajeros', 'tareas', 'zona_trabajo', 'desde',
                  'hasta', 'kilometros_a_recorrer', 'obs')
        exclude = ('seccion','responsable')
        widgets = {
            'cantidad_pasajeros': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'tareas': Select(
                attrs={
                    'id': 'tareas_veh_civil_sec',
                    'style': 'width: 100%',
                }
            ),
            'zona_trabajo': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'desde': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_desde_veh_civil_sec', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'hasta': DateInput(format=('%d/%m/%Y'),
                               attrs={'id': 'id_hasta_veh_civil_sec', 'autocomplete': 'off', 'style': 'width: 100%'}),
            'kilometros_a_recorrer': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
            'obs': TextInput(
                attrs={
                    'style': 'width: 100%'
                }
            ),
        }
        error_messages = {
            'obs': {
                'required': "Esta campo es obligatorio, ingrese Sin novedad si no tiene datos",
            },
        }


class FormBuscarPersona(Form):
    rango_fechas = CharField(
        widget=TextInput(
            attrs={
                'id': 'id_dni',
                'class': 'form-control',
                'placeholder': "Ingrese el dni a buscar"
            }
        ),
        label=""

    )


class FormSACAPuntoRecoleccion(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'
        usuario = get_current_user()
        if usuario.rol == 1:
            queryset = get_objects_for_user(usuario, 'view_distrito', Distrito)
        else:
            queryset = get_objects_for_user(usuario, 'view_distrito', Distrito, accept_global_perms=False)
        self.fields['distrito'].queryset = queryset
    class Meta:
        model = SACASPuntosRecoleccion
        # fields = '__all__'
        fields = ('direccion', 'denominacion_puesto', 'ubicacion', 'cant_sacas', 'cant_uupp', 'distrito')
        # exclude = ['', ]
        widgets = {
            'cant_sacas': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'cant_uupp': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'ubicacion': LeafletWidget(),
            'direccion': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'denominacion_puesto': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'historial_estados': Select(
                attrs={
                    "id": "h_estados",
                    "style": "width: 100%"
                }),
            'distrito': Select(
                attrs={
                    'id': 'id_distrito_puntos',
                   'style': 'width: 100%',
                }
            ),
        }
        error_messages = {
            'ubicacion': {
                'required': "No se ha ubicado el Punto de recolección en el mapa",
            },
        }


class FormSACACircuitoRecoleccion(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ocultar_campo = kwargs.pop('ocultar_campo', True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'
        usuario=get_current_user()
        if usuario.rol==1:
           ocultar_campo = False
           queryset = get_objects_for_user(usuario,'view_distrito', Distrito)
        else:
           queryset = get_objects_for_user(usuario, 'view_distrito', Distrito, accept_global_perms=False)

        if ocultar_campo:
            self.fields['prs'].widget = HiddenInput()

        self.fields['distrito'].queryset = queryset
    class Meta:
        model = SACACircuitoRecoleccion
        # fields = '__all__'
        fields = ('ctrs', 'cant_personal', 'vehiculo', 'prs', 'distrito')
        # exclude = [, ]
        widgets = {
            'ctrs': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'vehiculo': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'cant_personal': TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'prs': SelectMultiple(
                attrs={
                    'id': "id_prs",
                    'style': 'width: 100%',
                }
            ),
            'distrito': Select(
                attrs={
                    'id': 'id_distrito_circuito',
                    'style': 'width: 100%',
                }
            ),

        }


class FormSed(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Sed
        # fields = '__all__'
        fields = ('direccion', 'ubicacion', 'sed', 'telefono', 'localidad')
        exclude = ['distrito', ]
        widgets = {
            'direccion': TextInput(
                attrs={
                    "style": "width: 100%"
                }),
            'ubicacion': LeafletWidget(),

            'sed': TextInput(
                attrs={
                    "style": "width: 100%"
                }),
            'telefono': TextInput(
                attrs={
                    "style": "width: 100%"
                }),
            'localidad': TextInput(
                attrs={
                    "style": "width: 100%"
                }),
        }
        error_messages = {
            'ubicacion': {
                'required': 'Debe ubicar la Sucursal en el mapa'
            },
        }

class FormLugarInteres(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_lugar'].queryset = TipoLugarInteres.objects.filter(clase=1)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = LugarInteres
        fields = ('direccion', 'tipo_lugar', 'ubicacion', 'telefono','obs', 'autoridad')
        exclude = ['distrito', ]
        widgets = {
            'direccion': TextInput(
                attrs={
                    "style": "width: 100%"
                }),
            'ubicacion': LeafletWidget(),

            'obs': TextInput(
                attrs={
                    "style": "width: 100%"
                }),
            'telefono': TextInput(
                attrs={
                    "style": "width: 100%"
                }),
            'tipo_lugar': Select(
                attrs={
                    "id": "jose",
                    "style": "width: 100%"
                }),
            'autoridad': TextInput(
                attrs={
                    "style": "width: 100%"
                }),
        }
        error_messages = {
            'ubicacion': {
                'required': 'Debe ubicar el punto de interés en el mapa'
            },
        }

class FormGuiaAutoridades(ModelForm):
    persona_guia = ModelChoiceField(
        queryset=Persona.objects.none(),
        label='Integrante',
        widget=Select(
            attrs={'id': 'id_persona_guia', 'style': 'width: 100%'}
        ),
        required=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        if 'persona_guia' in self.data:
            try:
                self.fields['persona_guia'].queryset = Persona.objects.filter(id=int(self.data.get('persona_guia')))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['persona_guia'].initial = self.instance.persona_guia.id
            self.fields['persona_guia'].queryset = Persona.objects.filter(id=self.instance.persona_guia.id)
    class Meta:
        model = GuiaAutoridades
        fields = ('persona_guia', 'puesto_guia', 'gde_guia', 'tel_guia')
        exclude = ('puesto_texto',)
        widgets = {
            'puesto_guia': SelectMultiple(
                attrs={
                    'id': 'id_puesto_guia',
                    'style': 'width: 100%',
                }
            ),
            'gde_guia': TextInput(
                attrs={
                    'style': 'width: 100%',
                    'placeholder': 'Nombre de usuario del sistema GDE'
                }
            ),
            'tel_guia': TextInput(
                attrs={
                    'style': 'width: 100%',
                    'placeholder': 'Tel directo o celular provisto'
                }
            ),
        }
        error_messages = {
            '': {'': "",
            },
        }


