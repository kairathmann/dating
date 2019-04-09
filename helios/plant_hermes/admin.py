from django.contrib import admin
from .account.db import TokenAccount

"""
This adds export functionality to the django admin
"""


class TokenAccountAdmin(admin.ModelAdmin):
    pass


admin.site.register(TokenAccount, TokenAccountAdmin)
