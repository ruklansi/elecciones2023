from datetime import datetime, timedelta

from crum import get_current_user
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LogoutView
from django.core.mail import send_mail
from django.db.models.query_utils import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse_lazy
# No es necesario sobreescribir LogoutView, así con solo importarla se consume se la url sin problema
from django.utils import timezone
# Para resetear contraseña
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import FormView

# from .forms import MyChangeFormPassword, MyAutenticationForm, PasswordResetRequestForm, SetPasswordForm
from AppAdministracion.models import Usuario, MensajeParaUsuario
from .forms import *
from .tokens import account_activation_token
from django.utils.safestring import mark_safe


class LoginFormView(FormView):
    form_class = MyAutenticationForm
    template_name = 'AppLogin/login.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = MyAutenticationForm(user=self.request.user)
        return form

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = MyAutenticationForm(request.user, request.POST)
            if form.is_valid():
                login(self.request, form.get_user())
                if not get_current_user().is_staff:
                    mensaje = MensajeParaUsuario.objects.all().last()
                    if mensaje and mensaje.activo:
                        #https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#urlize
                        messages.info(request, mark_safe(mensaje.mensaje))
                return redirect('inicio')
        else:
            form = MyAutenticationForm(request.user)
        return render(request, 'AppLogin/login.html', {'form': form})


class UserChangePasswordView(FormView):
    model = Usuario
    form_class = MyChangeFormPassword
    template_name = 'AppLogin/change_password.html'
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = MyChangeFormPassword(user=self.request.user)
        return form

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = MyChangeFormPassword(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                # Importante: se utiliza para cerrar o no la sesión
                update_session_auth_hash(request, user)
                messages.success(
                    self.request, 'Su contraseña ha sido cambiada con éxito')
                return redirect('login')
            # else:
            #    messages.error(
            #        request, 'Por favor corrija los errores de validación.')
        else:
            form = MyChangeFormPassword(request.user)

        return render(request, 'AppLogin/change_password.html', {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Cambiar contraseña'
        return context


class ResetPasswordRequestView(FormView):
    template_name = "AppLogin/test_template.html"
    success_url = reverse_lazy('login')
    form_class = PasswordResetRequestForm

    def form_valid(self, form):

        if form.is_valid():
            data = form.cleaned_data["email"]
            usuario = Usuario.objects.filter(
                Q(email=data)).first()
            if usuario:
                fecha_expiracion = datetime.now() + timedelta(hours=24)
                formatted_date = fecha_expiracion.strftime("%d/%m/%Y a las %H horas")  # Formato de fecha y hora
                c = {
                    'email': usuario.email,
                    # 'domain': self.request.META['HTTP_HOST'],
                    # 'site_name': 'your site',
                    'domain': 'https://datoscoffaa.fuerzas-armadas.mil.ar',
                    'uid': urlsafe_base64_encode(force_bytes(usuario.pk)),
                    'usuario': usuario,
                    'token': account_activation_token.make_token(usuario),
                    'protocol': self.request.scheme,
                    'fecha_expiracion': formatted_date
                }
                email_template_name = 'AppLogin/password_reset_email.txt'

                subject = "Solicitud de reseteo de contraseña"
                email = loader.render_to_string(email_template_name, c)
                send_mail(subject, email, settings.DEFAULT_FROM_EMAIL,
                          [usuario.email], fail_silently=False)
                usuario.fecha_reseteo = timezone.now()
                usuario.tipo_reseteo = 2
                usuario.save()
                messages.success(
                    self.request,
                    '¡Instrucciones enviadas!. Revisa tu correo electrónico.'
                    'Si no recibes el correo en los próximos minutos, revisa la casilla de SPAM. '
                    'Recuerda que el token expirará el '+ formatted_date)

            return super().form_valid(form)
        else:
            PasswordResetRequestForm()


# https://ruddra.com/implementation-of-forgot-reset-password-feature-in-django/
# https://simpleisbetterthancomplex.com/tutorial/2016/09/19/how-to-create-password-reset-view.html
# https://simpleisbetterthancomplex.com/tutorial/2016/08/24/how-to-create-one-time-link.html
# https://medium.com/swlh/email-verified-user-registration-and-password-reset-in-django-ffb9b30939a8

class ActivateAccountView(FormView):
    model = Usuario
    template_name = "AppLogin/password_reset_form.html"
    success_url = reverse_lazy('login')
    form_class = SetPasswordForm
    post_reset_login = True

    def dispatch(self, request, *args, **kwargs):
        """    https://pylessons.com/django-handle-password--->>>>>>no es la guia de abajo pero puede servir
               Override the dispatch method to check if the token is expired before proceeding
               with the password reset process.
               """
        try:
            # Get the user associated with the given token
            self.user = self.get_user(kwargs['uidb64'])
            # Check if the token is expired
            token = kwargs['token']
            if not account_activation_token.check_token(self.user, token):
                # https://neunapp.com/contenido/personalizar-respuestas-de-error-en-django-3-16115
                # raise Http404("El token ha expirado.")
                messages.error(request, 'El enlace ha expirado. Debe restablecer la contraseña.')
                return redirect('inicio')
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            # raise Http404("User not found.")
            messages.error(request, 'Usuario no encontrado')

        return super().dispatch(request, *args, **kwargs)

    def get_user(self, uidb64):
        """
        Get the user associated with the given uidb64.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            return Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    def get_form(self, form_class=None):
        form = SetPasswordForm(user=self.request.user)
        return form

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = SetPasswordForm(request.user, request.POST)
            if form.is_valid():
                uidb64 = self.kwargs["uidb64"]
                mitoken = self.kwargs['token']
                try:
                    uid = urlsafe_base64_decode(uidb64)
                    usuario = Usuario.objects.get(pk=uid)
                except (TypeError, ValueError, OverflowError, usuario.DoesNotExist):
                    usuario = None
                if usuario is not None and account_activation_token.check_token(usuario, mitoken):
                    new_password = form.cleaned_data['new_password2']
                    usuario.set_password(new_password)
                    usuario.save()
                    messages.success(
                        self.request, 'Contraseña restablecida')
                    # return render(request, 'login/login.html', {'form': form})
                    return super().form_valid(form)
                else:
                    messages.error(
                        self.request, 'Contraseña no restablecida')
                    return super().form_valid(form)
            else:
                return render(request, 'AppLogin/password_reset_form.html', {'form': form})


class ResetViaAjax(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        respuesta = dict()
        correo = (request.POST['correo'])
        usuario = Usuario.objects.get(Q(email=correo))
        if usuario:
            fecha_expiracion = datetime.now() + timedelta(hours=24)
            formatted_date = fecha_expiracion.strftime("%d/%m/%Y a las %H horas")  # Formato de fecha y hora
            c = {
                'email': usuario.email,
                # 'domain': self.request.META['HTTP_HOST'],
                # 'site_name': 'your site',
                'domain': 'https://datoscoffaa.fuerzas-armadas.mil.ar',
                'uid': urlsafe_base64_encode(force_bytes(usuario.pk)),
                'usuario': usuario,
                'token': account_activation_token.make_token(usuario),
                'protocol': self.request.scheme,
                'fecha_expiracion': formatted_date
            }
            email_template_name = 'AppLogin/primer_reseteo_password.txt'
            subject = "Primer reseteo de contraseña"
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, settings.DEFAULT_FROM_EMAIL,
                      [usuario.email], fail_silently=False)
            usuario.fecha_reseteo = timezone.now()
            usuario.tipo_reseteo = 1
            usuario.save()
            respuesta['enviado'] = 'Se enviaron instrucciones para restablecer la contraseña al usuario ' \
                                   + usuario.username + ' al correo ' + correo + ', el mismo expira el: ' + formatted_date
        return JsonResponse(respuesta, safe=False)
