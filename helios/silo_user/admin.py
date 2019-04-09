from django.contrib import admin
from silo_user.user.db import User
from import_export import resources
from import_export.admin import ExportMixin

"""
This adds export functionality to the django admin
"""


class UserResource(resources.ModelResource):
    class Meta:
        model = User


class UserAdmin(ExportMixin, admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
