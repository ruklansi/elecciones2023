"""ProyElecciones URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from ProyElecciones import settings
from django.conf.urls import handler400, handler403, handler404, handler500


urlpatterns = [
    path('elecciones/', include('AppLogin.urls'), name='pepe'),
    path('elecciones/login/', include('AppLogin.urls')),
    path('elecciones/nido/', admin.site.urls),
    path('elecciones/captcha/', include('captcha.urls')),
    path('elecciones/inicio/', include('AppElecciones.urls')),
    path('elecciones/administracion/', include('AppAdministracion.urls')),
    path('elecciones/django_plotly_dash/', include('django_plotly_dash.urls')),
]
handler403 = 'ProyElecciones.views.permission_denied'
handler404 = 'ProyElecciones.views.error_404'
handler500 = 'ProyElecciones.views.error_500'

admin.site.site_header = "Tablero de Comando COFFAA"
admin.site.site_title = "Tablero de Comando COFFAA"
admin.site.index_title = "Tablero de Comando COFFAA - Módulo administration"


# required to see the media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

