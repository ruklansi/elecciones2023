from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls.base import reverse

from django.utils.deprecation import MiddlewareMixin

# https://github.com/labd/django-session-timeout/blob/master/src/django_session_timeout/middleware.py
import time
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

SESSION_TIMEOUT_KEY = "_session_init_timestamp_"


class AjaxRedirectHandlerMiddleware(MiddlewareMixin):
    """
    Middleware for AJAX redirects in Django.
    """

    def process_request(self, request):
        if not hasattr(request, "session") or request.session.is_empty():
            return
        init_time = request.session.setdefault(SESSION_TIMEOUT_KEY, time.time())
        expire_seconds = getattr(settings, "SESSION_EXPIRE_SECONDS", settings.SESSION_COOKIE_AGE)
        session_is_expired = time.time() - init_time > expire_seconds
        if session_is_expired:
            if request.is_ajax():
                response = JsonResponse({
                    'error': 'Error',
                    'error_message': 'Session expired',
                    'redirect_to': reverse('login'),
                })
                response.status_code = 403
                return response

            request.session.flush()
            messages.info(request, 'Debe volver a iniciar sesión')
            redirect_url = getattr(settings, "SESSION_TIMEOUT_REDIRECT", None)

            if redirect_url:
                return redirect(redirect_url)
            else:
                return redirect_to_login(next=request.path)

        expire_since_last_activity = getattr(settings, "SESSION_EXPIRE_AFTER_LAST_ACTIVITY", False)

        grace_period = getattr(
            settings, "SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD", 1
        )

        if expire_since_last_activity and time.time() - init_time > grace_period:
            request.session[SESSION_TIMEOUT_KEY] = time.time()

