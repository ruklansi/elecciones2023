from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', LoginFormView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset/password/', ResetPasswordRequestView.as_view(), name='reset_password'),
    path('change/password/', UserChangePasswordView.as_view(), name='change_password'),
    path('reset_password_confirm/<uidb64>/<token>/', ActivateAccountView.as_view(), name='password_reset_confirm'),
    path('resetclaveviaajax/', login_required(ResetViaAjax.as_view()),
         name='reser-via-ajax'),
    path('', include('user_sessions.urls', 'user_sessions')),


]