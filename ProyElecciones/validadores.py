# https://www.codingforentrepreneurs.com/blog/the-simple-power-of-django-validato
import re
from django.core.exceptions import ValidationError

from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _


def validar_abreviatura_unidad(data):
    if not re.match('^[a-zA-Z0-9 ]{2,20}$', data):
        raise ValidationError(
            "La abreviatura debe contener solo números, letras (no acentuadas ni ñ) y espacios. Un mínimo de 2 caracteres y un máximo de 20", )


def validar_dni(data):
    if not re.match('^[0-9]{8,8}$', data):
        raise ValidationError(
            "El formato del DNI debe ser sin puntos y 8 caracteres", )


def validar_te(data):
    if not re.match('^(?:(?:00)?549?)?0?(?:11|[2368]\d)(?:(?=\d{0,2}15)\d{2})??\d{8}$', data):
        raise ValidationError(
            "El formato del Tel debe ser código de área (sin el cero) más Nro Tel Cel sin el 15", )


def validar_longitud(data):
    if not re.match('^(1[0-7]?[0-9]|[1-8]?[0-9])-([0-5]?[0-9]|60|00)-([0-5]?[0-9]|60|00)-[EOeo]$', data):

        if not re.match('^[\+-]?((1[1-7]?[0-9])(\.\d{3,50})|([1-9]?[0-9])(\.\d{3,50})|180)\D?$', data):
            raise ValidationError(
                "Mala longitud", )


def validar_latitud(data):
    if not re.match('^([0-8]?[0-9]|[1-8]?[0-9])-([0-5]?[0-9]|60|00)-([0-5]?[0-9]|60|00)-[NnSs]$', data):
        if not re.match('^[\+-]?(([1-8]?[0-9])(\.\d{3,50})|90)\D?$', data):
            raise ValidationError(
                "Mala latitud", )


# https://github.com/rayer4u/apksign/blob/master/models.py
class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types.
        Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file
        size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 52428800
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """

    def __init__(self, content_types=[], max_upload_size=429916160, **kwargs):
        self.content_types = content_types
        self.max_upload_size = max_upload_size

        super(ContentTypeRestrictedFileField, self).__init__(**kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField,
                     self).clean(*args, **kwargs)
        file = data.file
        try:
            content_type = file.content_type
            # print(content_type)
            if self.content_types == [] or content_type in self.content_types:
                if file.size > self.max_upload_size:
                    raise forms.ValidationError(
                        _('El tamaño del archivo debe ser de %s como máximo. El que intente subir es de %s')
                        % (filesizeformat(self.max_upload_size), filesizeformat(file.size)))
            else:
                raise forms.ValidationError(
                    _('El formato del archivo no es el correcto'))
        except AttributeError:
            pass
        return data
