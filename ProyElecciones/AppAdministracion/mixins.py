from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.encoding import force_text


class AuditMixin(object):
    def save_log(self, user, message, ACTION):
        log = LogEntry.objects.create(
            user_id=user.id,
            content_type_id=ContentType.objects.get_for_model(self).id,
            object_id=self.id,
            object_repr=force_text(self),
            action_flag=ACTION,
            change_message=message
        )

    def save_addition(self, user):
        self.save_log(user, 'Creo', ADDITION)

    def save_edition(self, user):
        self.save_log(user, 'Modificó', CHANGE)

    def save_deletion(self, user):
        self.save_log(user, 'Eliminó', DELETION)

# class AdminEjercicio(object):
#
#     def dispatch(self, request, *args, **kwargs):
#         if request.user.groups.filter(Q(name='ADMIN_SISTEMA')):
#             return super().dispatch(request, *args, **kwargs)
#         messages.error(request, 'No tiene permisos')
#         return redirect('inicio')
