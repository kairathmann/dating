#  -*- coding: UTF8 -*-

import copy
import datetime
import decimal
import json
import uuid

from django.db import models
from django.db.models.query import QuerySet
from django.forms.utils import ValidationError
from django.utils import six, timezone
from django.utils.encoding import force_text
from django.utils.functional import Promise


class JSONEncoder(json.JSONEncoder):
    """
        A JSONEncoder subclass that knows how to encode date/time/timedelta, decimal types, generators
        and other basic python objects.

        Originally based on: https://github.com/tomchristie/django-rest-framework
        ... /blob/master/rest_framework/utils/encoders.py
    """

    def default(self, obj):

        # For Date Time string spec, see ECMA 262 http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15
        if isinstance(obj, Promise):
            return force_text(obj)

        elif isinstance(obj, datetime.datetime):

            representation = obj.isoformat()

            if obj.microsecond:
                representation = representation[:23] + representation[26:]

            if representation.endswith('+00:00'):
                representation = representation[:-6] + 'Z'

            return representation

        elif isinstance(obj, datetime.date):
            return obj.isoformat()

        elif isinstance(obj, datetime.time):

            if timezone and timezone.is_aware(obj):
                raise ValueError("JSON can't represent timezone-aware times.")

            representation = obj.isoformat()

            if obj.microsecond:
                representation = representation[:12]

            return representation

        elif isinstance(obj, datetime.timedelta):
            return six.text_type(obj.total_seconds())

        elif isinstance(obj, decimal.Decimal):
            # Serializers will coerce decimals to strings by default.
            return float(obj)

        elif isinstance(obj, uuid.UUID):
            return six.text_type(obj)

        elif isinstance(obj, QuerySet):
            return tuple(obj)

        elif hasattr(obj, 'tolist'):
            # Numpy arrays and array scalars.
            return obj.tolist()

        elif hasattr(obj, '__getitem__'):

            try:
                return dict(obj)

            except:
                pass

        elif hasattr(obj, '__iter__'):
            return tuple(item for item in obj)

        return super(JSONEncoder, self).default(obj)


class JSONField(models.Field):

    def __init__(self, *args, **kwargs):

        kwargs['null'] = True
        kwargs['default'] = ''
        kwargs['editable'] = False
        kwargs['serialize'] = False

        # Django *cannot* create indexes for JSON fields. Postgres JSON fields can't be indexed using BTREE,
        # which is the only method Django knows, and on top of that, they require a special index syntax. See
        # http://www.postgresql.org/docs/9.4/static/datatype-json.html

        kwargs['db_index'] = False

        self.dump_kwargs = kwargs.pop('dump_kwargs', {
            'cls': JSONEncoder,
            'separators': (',', ':')
        })

        self.load_kwargs = kwargs.pop('load_kwargs', {})

        super(JSONField, self).__init__(*args, **kwargs)

    def db_type(self, *args, **kwargs):
        """
            Returns the Postgres field type that this Django field type uses. This info is used by the
            Django ORM when creating tables that use this field type.
        """

        # We're currently storing this as a Postgres JSON field. When we upgrade the platform to Postgres 9.4,
        # we can update this to a JSONB field, which has GIN and GIST index capability.

        return 'JSON'

    def pre_init(self, value, obj):
        """
            Convert a string value to JSON only if it needs to be deserialized. SubfieldBase metaclass has
            been modified to call this method instead of to_python so that we can check the obj state and
            determine if it needs to be deserialized
        """

        if obj._state.adding:

            # Make sure the primary key actually exists on the object before checking if it's empty.

            if getattr(obj, "pk", None) is not None:

                if isinstance(value, six.string_types):

                    try:
                        return json.loads(value, **self.load_kwargs)

                    except ValueError:
                        raise ValidationError("Enter valid JSON")

        return value

    def to_python(self, value):
        """
            The SubfieldBase metaclass calls pre_init instead of to_python, however to_python
            is still necessary for Django's deserializer
        """
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        """
            Convert JSON object to a string
        """

        if self.null and value is None:
            return None

        return json.dumps(value, **self.dump_kwargs)

    def value_to_string(self, obj):

        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value, None)

    def get_default(self):
        """
            Returns the default value for this field. The default implementation on models.Field calls force_unicode
            on the default, which means you can't set arbitrary Python objects as the default. To fix this, we just
            return the value without calling force_unicode on it. Note that if you set a callable as a default, the
            field will still call it. It will *not* try to pickle and encode it.
        """

        if callable(self.default):
            return self.default()

        return copy.deepcopy(self.default)
