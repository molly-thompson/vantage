from django.contrib import admin

from .models import IncidentNote, Log, LogTag

admin.site.register([IncidentNote, Log, LogTag])
