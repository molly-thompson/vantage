from django.contrib import admin

from .models import ApiEntity, System

admin.site.register([System, ApiEntity])
