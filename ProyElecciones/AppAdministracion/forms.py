from django.forms import Form, CharField, TextInput, ChoiceField, RadioSelect
from django import forms
from AppAdministracion.models import Usuario


class UsuarioForm(forms.ModelForm):
    # OPCIONES_SUPERUSER = [(True, "Sí"), (False, "No")]
    # is_superuser = ChoiceField(choices=OPCIONES_SUPERUSER, widget=RadioSelect(), required=True,
    #                                    label='Es super usuario')

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'username', 'password', 'rol', 'dni', 'nro_tel', 'grupo_organizacion')
        exclude = ['user_permissions', 'last_login', 'date_joined', 'is_staff','is_active', 'is_superuser']
        error_messages = {
            'username': {
                'unique': "Nombre de usuario asignado, utilice otro",

            }, }
        widgets = {
            'rol': forms.Select(
                attrs={
                    'id': 'id_rol',
                    'style': 'width: 100%',
                }
            ),
            'grupo_organizacion': forms.Select(
                attrs={
                    'id': 'id_grupo',
                    'style': 'width: 100%',
                }
            ),
            'dni': forms.TextInput(
                attrs={
                    'style': 'width: 100%',
                }),
            'nro_tel': forms.TextInput(attrs={
                'style': 'width: 100%',
            }),
            'first_name': forms.TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'password': forms.PasswordInput(render_value=True,
                                            attrs={
                                                'placeholder': 'Ingrese la clave',
                                                'style': 'width: 100%',
                                            }
                                            ),
            'username': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese el nombre de usuario',
                    'style': 'width: 100%',
                    'autocomplete': 'off'
                }
            ),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                pwd = self.cleaned_data['password']
                u = form.save(commit=False)
                # La logica que sigue ponerla aca, no en la sobreescritura
                # del método save del modelo, porque sino al crear un superuser
                # por consola no reconoce la contraseña ya que hacemos en la
                # sobreescritura en el modelo una doble encriptación con el método
                # set_password, ya que hereda de AbstractUser y esta clase ya
                # encripta la contraseña
                # Aca si estoy creando un usuario
                if u.pk is None:
                    u.set_password(pwd)
                # Aca si estoy modificando un usuario
                else:
                    user = Usuario.objects.get(pk=u.pk)
                    if user.password != pwd:
                        u.set_password(pwd)
                u.save()
                # Agregado aca para que funciona tanto para la creación de usuarios como la modificación de los mismos
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data



class BuscarForm(Form):
    rango_fechas = CharField(
        widget=TextInput(
            attrs={
                'id': 'id_rango_fechas',
                'autocomplete': 'off',
                'style': 'width: 100%',
            }
        )
    )
