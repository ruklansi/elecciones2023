from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from captcha.fields import CaptchaField
from django.contrib.auth.models import User


class MyChangeFormPassword(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        self.user = User
        super().__init__(user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Ingrese su contraseña actual'})
        self.fields['new_password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Ingrese su nueva contraseña'})
        self.fields['new_password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Repita su nueva contraseña'})
        self.fields['old_password'].widget.attrs.update(
            {'style': 'width: 100%'})
        self.fields['new_password1'].widget.attrs.update(
            {'style': 'width: 100%'})
        self.fields['new_password2'].widget.attrs.update(
            {'style': 'width: 100%'})


class MyAutenticationForm(AuthenticationForm):
    captcha = CaptchaField()
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'style': 'width: 100%'})
        self.fields['password'].widget.attrs.update(
            {'style': 'width: 100%'})


class PasswordResetRequestForm(PasswordResetForm):
    pass


class SetPasswordForm(SetPasswordForm):
    pass
